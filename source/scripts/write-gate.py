#!/usr/bin/env python3
"""PreToolUse gate for Write/Edit and Bash: to block writes outside the Bootcamper's
project, and block obvious secrets -- DURING a bootcamp only.

Two independent checks on Write and Edit, governed by two different invariants:

* **Location (INV-200)** -- every file the bootcamp writes lives inside the Bootcamper's
  project. Blocks any resolved target outside it, including one reached by a ``..``
  escape; allows project-relative and in-project absolute paths, including a project
  that legitimately lives beneath a temp directory (resolve, then compare). System temp
  and ``~/Downloads`` are not a separate rule -- they are the cases that get a more
  specific message than the general boundary one.
* **Secrets (INV-109)** -- PEM private keys, AWS access-key IDs and Senzing ``AQAAAD``
  license blobs are blocked whatever the path. Runs independently of the location logic
  and fails closed.

On **Bash** (#876) the gate is deliberately narrower: it blocks only a command whose
top-level output target resolves to system temp or Downloads outside the project, and runs
no secret check. ``shlex`` splits the command as the shell would, and its operator tokens
(``;``, ``&&``, ``||``, ``|``, newline, ``>``, ``>>``) split it into simple commands. Each
simple command's redirect targets are checked, and so are the output arguments of a small
table of writers: ``curl -o``/``--output``/``--output-dir``, ``wget -O``/``-P``, ``tee``, and
the destination of ``cp``/``mv``. A quoted string is one word and is never parsed again, so
an ``sh -c '...'`` or ``docker exec ... bash -c '...'`` payload is not inspected; nor is a
write made by a program the command runs. A target outside the project that is not temp or
Downloads (``/opt/senzing``, ``~/.cargo``) is allowed: installers write there. A command
``shlex`` cannot split (an unbalanced quote) is allowed, as a Write/Edit payload whose target
cannot be extracted is.

On a **PowerShell** command the rule is the same and only the reading differs. The hook
adapter adds ``"shell_dialect": "powershell"`` to the Bash payload when the assistant's
profile declares the shell tool that sent the command a PowerShell one; a payload that names
no dialect is read as POSIX shell, exactly as above. ``powershell_tokens()`` reads the
command by PowerShell's rules and hands the same pipeline the same tokens: a backslash is a
literal character and the backtick is the escape, a single-quoted string is literal, a
double-quoted string is one word in which the variables below still count, and ``;``, a
newline, ``|``, ``&&`` and ``||`` end a command. Checked are a ``>`` or ``>>`` redirect, alone
or with a stream in front (``2>``, ``2>>``, ``*>``, ``*>>``), and the PowerShell writers:
``Out-File``, ``Set-Content`` and ``Add-Content`` (``sc``, ``ac``), ``Tee-Object`` (``tee``),
the destination of ``Copy-Item`` and ``Move-Item`` (``cp``, ``copy``, ``cpi``, ``mv``,
``move``, ``mi``) and ``Invoke-WebRequest -OutFile`` (``iwr``, ``curl``, ``wget``). Command
and parameter names match in any case, and ``curl.exe -o`` and ``wget -O`` are still read as
above. System temp is also ``$env:TEMP``, ``$env:TMP`` and ``$env:TMPDIR``, with or without
braces, and the home directory is ``$HOME``, ``$env:USERPROFILE``, ``$env:HOME`` or ``~``.
``$null`` names no file, nor does ``2>&1``, which joins two streams, and a here-string's
body is data. Any other variable, an expression and an abbreviated parameter name
(``-Dest``) are not evaluated. The payload a PowerShell tool sends on Windows has not been
observed: the tests simulate it.

Gate: the hook enforces nothing unless ``config/bootcamp_progress.json`` EXISTS, and it tests
existence on purpose, not ``recap_checkpoint.bootcamp_active()``: existence answers "is this
a bootcamp project", not "is a bootcamp in progress" (INV-227). The onboarding preface
creates the file empty and nothing records a module until Bootcamp preparation's final
write, yet both write project files, and those writes must stay in the project and free of
secrets too.

Cross-platform: invoked as a ``type: command`` hook whose ``command`` names the
interpreter and this script, quoted (``python3 "<path>"``), per INV-052.
Native JSON parsing replaces the previous grep/sed field extraction.

The payload is read as bytes and decoded as UTF-8, and the block message is written as
UTF-8 bytes, so the result is the same whatever encoding the console gives Python (#25).
A payload that is not valid UTF-8 is read with replacement characters and judged as usual.
"""
import json
import os
import re
import shlex
import sys

# Bytes, decoded as UTF-8: a text-mode read takes the console code page on Windows, where
# a curly quote in the payload failed the decode and the gate exited 1, allowing the write
# (#25). Replacement characters keep a payload that is not valid UTF-8 judged, not crashed.
data = sys.stdin.buffer.read().decode("utf-8", errors="replace")

# Gate: only enforce when a bootcamp is active, so the plugin never blocks writes in
# unrelated sessions.
if not os.path.isfile(os.path.join("config", "bootcamp_progress.json")):
    sys.exit(0)

LOC_MSG = (
    "Write blocked: use a project-relative path, not a system temp or Downloads "
    "directory."
)
OUTSIDE_MSG = (
    "Write blocked: that path is outside the Bootcamp project. Every file the bootcamp "
    "writes stays inside the project directory -- use a project-relative path."
)
SECRET_MSG = (
    "Write blocked: a possible hardcoded secret was detected. Use environment "
    "variables instead."
)
# Added to SECRET_MSG when an edit is blocked for a secret its new text does not hold:
# "use environment variables" alone points away from the next step that works (#47).
SECRET_REPLACED_MSG = (
    " The possible secret is in the text being replaced, not in the new text. To take "
    "it out of the file, write the whole file again without the secret."
)

# System temp / Downloads locations to block (outside-project writes only). Prefix
# entries match the start of the normalized, lower-cased path; substring entries
# match anywhere (Downloads and the Windows temp dir can appear mid-path).
TEMP_PREFIXES = ("/tmp/", "/var/tmp/", "/private/tmp/", "/private/var/folders/")
# `/windows/temp/` is the SYSTEM account's temp dir on Windows (%SystemRoot%\Temp) — the
# Windows counterpart of /tmp, and previously the one uncovered system temp location.
TEMP_SUBSTRINGS = ("/downloads/", "/appdata/local/temp/", "/windows/temp/")


def block(message):
    # UTF-8 bytes, whatever encoding the console gave stderr (#25).
    sys.stderr.flush()
    sys.stderr.buffer.write((message + "\n").encode("utf-8"))
    sys.stderr.buffer.flush()
    sys.exit(2)


def norm(path):
    """Backslash-normalize, collapse repeated slashes, and resolve `.`/`..`
    segments (portably, without touching the filesystem) so Windows and POSIX
    targets compare correctly and cannot escape the project via `..`."""
    p = re.sub(r"/+", "/", path.replace("\\", "/"))
    leading = "/" if p.startswith("/") else ""
    out = []
    for seg in p.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if out and out[-1] != "..":
                out.pop()
            elif not leading:
                out.append("..")
        else:
            out.append(seg)
    return leading + "/".join(out)


def location(file_path):
    """Classify a write target: ``None`` (inside the project, or no target), ``"temp"``
    (system temp or Downloads outside the project) or ``"outside"`` (anywhere else
    outside the project). Write/Edit blocks both of the last two; Bash only ``"temp"``."""
    # Expand a leading ~ / ~user so a home-relative target (e.g. ~/Downloads/x) is
    # classified by its real location instead of being treated as a bogus in-project
    # segment joined onto the cwd. (No-op on empty/absolute/%TEMP% paths.)
    if file_path:
        file_path = os.path.expanduser(file_path)

    # An unexpanded Windows temp env-var reference (%TEMP%/%TMP%) is always a temp
    # target, independent of the project directory. Windows env-var names are
    # case-insensitive, so compare case-folded (%Temp%, %tmp%, ... all count).
    _fp_upper = file_path.upper()
    if "%TEMP%" in _fp_upper or "%TMP%" in _fp_upper:
        return "temp"

    # Resolve to an absolute path. A relative path is, by definition, inside the project,
    # so it is always allowed on location grounds.
    if file_path.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", file_path):
        abs_path = file_path                       # POSIX or Windows-drive absolute
    elif file_path == "":
        return None                                # extraction failed -> fail open
    else:
        abs_path = os.path.join(os.getcwd(), file_path)

    # Location check: exempt the project directory FIRST, then classify everything outside
    # it. The gate's intent is "don't write outside the project" (INV-200), so the
    # temp/Downloads lists below do NOT decide *whether* Write/Edit blocks -- they only
    # choose the more specific message. A project that merely lives under a path containing
    # /tmp/ (e.g. /home/user/tmp/proj) must not trip the gate for its own in-project
    # writes, which is why the exemption is checked first.
    target = norm(abs_path)          # `..` resolved, so escapes can't slip the block
    here = norm(os.getcwd())
    # Case-fold both sides of the exemption with the SAME rule the temp/Downloads
    # checks use below (Windows/macOS filesystems are case-insensitive), so an
    # in-project path whose case differs from the cwd is exempted, not blocked.
    low = target.lower()
    here_low = here.lower()
    if low == here_low or low.startswith(here_low + "/"):
        return None  # inside the project -> allowed on location grounds (checked FIRST)
    if any(low.startswith(p) for p in TEMP_PREFIXES) or any(
        s in low for s in TEMP_SUBSTRINGS
    ):
        return "temp"
    # Per-user / relocated temp dirs the prefix lists cannot enumerate: macOS puts
    # its under $TMPDIR (e.g. /var/folders/...), Windows under %TEMP%/%TMP%. Consult
    # all three so no platform is covered less well than the others (INV-001).
    # These now only refine the Write/Edit message -- the fall-through blocks them anyway.
    for var in ("TMPDIR", "TEMP", "TMP"):
        env_tmp = os.environ.get(var, "")
        if not env_tmp:
            continue
        tmp_norm = norm(env_tmp.rstrip("/\\")).lower()
        if tmp_norm and low.startswith(tmp_norm + "/"):
            return "temp"
    # Anything else that resolved outside the project. Without this the gate was
    # a temp-and-Downloads blocker, not the boundary INV-200 states: a target
    # outside the project that named no list -- including one reached by a `..`
    # escape -- fell through here and was ALLOWED.
    return "outside"


# --- Bash (#876): top-level output targets only --------------------------------------------

# shlex's own operator characters, plus newline: a newline ends a simple command as `;` does,
# and shlex would otherwise read it as plain whitespace.
BASH_PUNCT = "();<>|&\n"
# shlex returns a run of operator characters as one token (`)>`, `;\n`); this splits a run
# into the shell's operators, longest first.
BASH_OPS = re.compile(
    r"&>>|;;&|&>|>>|>\||>&|<<<|<<|<>|<&|&&|\|\||\|&|;;|;&|[;&|()<>\n]")
COMMAND_ENDS = {";", "&&", "||", "|", "|&", "&", "\n", ";;", ";&", ";;&", "(", ")"}
COMMAND_ENDS |= {"{", "}"}            # PowerShell's script block; shlex never returns either
WRITE_REDIRECTS = {">", ">>", ">|", "&>", "&>>", "<>", ">&"}
READ_REDIRECTS = {"<", "<<", "<<<", "<&"}
# A here-document's body is data, not commands: it is cut out before splitting.
HEREDOC = re.compile(r"(?<!<)<<(-?)[ \t]*(['\"]?)\\?([^\s'\"\\<>;&|()]+)\2")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# `$TMPDIR`/`$TEMP`/`$TMP` in a target is temp, as `%TEMP%`/`%TMP%` is on the Write path.
TEMP_VAR = re.compile(r"\$\{?(?:TMPDIR|TEMP|TMP)(?![A-Za-z0-9_])")
HOME_VAR = re.compile(r"^\$\{?HOME\}?(?=/|$)")
# PowerShell's spellings, in any case. `` `$ `` is how powershell_tokens() keeps a literal dollar.
PS_TEMP_VAR = re.compile(r"(?<!`)\$\{?env:(?:TMPDIR|TEMP|TMP)(?![A-Za-z0-9_])", re.I)
PS_HOME_VAR = re.compile(r"^(?:~|\$\{?(?:env:(?:USERPROFILE|HOME)|HOME)\}?)(?=[\\/]|$)", re.I)

# Words that run the command after them, each with its short options that take a value.
WRAPPERS = {"sudo": "CDghprtUu", "env": "CSu", "exec": "a", "nice": "n",
            "nohup": "", "time": "", "command": "", "builtin": ""}
# Shell words that open a compound command; the command after them is still a command.
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{"}


def parse_opts(args, short_value, long_value):
    """Split getopt-style ``args`` into ``([(option, value)], positionals)``.

    ``short_value`` holds the short letters that take a value, ``long_value`` the long
    names. A short bundle is read letter by letter (``-fsSLo``): the first value-taking
    letter takes the rest of the bundle as its value (``-o/tmp/x``), or the next word when
    the bundle ends there. ``--name=value`` and ``--name value`` both work; ``--`` ends
    the options. Options after positionals are still options, as GNU getopt permutes.
    """
    opts, positionals = [], []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--":
            positionals.extend(args[i + 1:])
            break
        if arg.startswith("--"):
            name, eq, value = arg[2:].partition("=")
            if not eq and name in long_value and i + 1 < len(args):
                i += 1
                value = args[i]
            opts.append(("--" + name, value))
        elif arg.startswith("-") and len(arg) > 1:
            for j, letter in enumerate(arg[1:], 1):
                if letter in short_value:
                    value = arg[j + 1:]
                    if not value and i + 1 < len(args):
                        i += 1
                        value = args[i]
                    opts.append(("-" + letter, value))
                    break
                opts.append(("-" + letter, ""))
        else:
            positionals.append(arg)
        i += 1
    return opts, positionals


def option_values(opts, names):
    return [value for option, value in opts if option in names and value]


def curl_targets(args):
    # curl's short options that take a value, so a bundle such as `-sSfo` is read right.
    opts, _ = parse_opts(args, "AbcCdDeEFHKmoPQrtTuUwxXyYz", {"output", "output-dir"})
    return option_values(opts, ("-o", "--output", "--output-dir"))


def wget_targets(args):
    # wget's short options that take a value (`-n` too: it spells -nv, -nc, -nd, -np).
    opts, _ = parse_opts(args, "aABDeIilnoOPQRtTUwX", {"output-document", "directory-prefix"})
    return option_values(opts, ("-O", "--output-document", "-P", "--directory-prefix"))


def tee_targets(args):
    return parse_opts(args, "", set())[1]


def cp_mv_targets(args):
    opts, positionals = parse_opts(
        args, "St", {"target-directory", "suffix", "sparse", "no-preserve"})
    named = option_values(opts, ("-t", "--target-directory"))
    if named:
        return named
    return positionals[-1:] if len(positionals) >= 2 else []


WRITERS = {"curl": curl_targets, "wget": wget_targets, "tee": tee_targets,
           "cp": cp_mv_targets, "mv": cp_mv_targets}

# PowerShell switch parameters: one takes no value, so the word after it is a positional.
PS_SWITCHES = frozenset(
    "append asbytestream confirm container debug force noclobber nonewline passthru recurse "
    "usetransaction verbose whatif".split())


def powershell_args(args):
    """Split a cmdlet's ``args`` into ``({parameter: value}, positionals)``.

    A parameter name is matched lower-cased and whole: an abbreviated name is another
    parameter. ``-Name:value`` carries its value, a switch takes none, and any other
    parameter takes the next argument. Words joined by a comma are one argument
    (``a.txt, b.txt``), so a list of sources is never read as a source and a destination.
    """
    joined = []
    for arg in args:
        if joined and (joined[-1].endswith(",") or arg.startswith(",")):
            joined[-1] += arg
        else:
            joined.append(arg)
    named, positionals = {}, []
    i = 0
    while i < len(joined):
        arg = joined[i]
        if re.match(r"-[A-Za-z]", arg):
            name, colon, value = arg[1:].partition(":")
            name = name.lower()
            if not colon and name not in PS_SWITCHES and i + 1 < len(joined):
                i += 1
                value = joined[i]
            named[name] = value
        else:
            positionals.append(arg)
        i += 1
    return named, positionals


def powershell_file_targets(*parameters):
    """A writer whose target is one of ``parameters`` or, with none named, its first positional."""
    def targets(args):
        named, positionals = powershell_args(args)
        return [named[p] for p in parameters if p in named] or positionals[:1]
    return targets


def powershell_copy_targets(args):
    named, positionals = powershell_args(args)
    if "destination" in named:
        return [named["destination"]]
    first = 0 if "path" in named or "literalpath" in named else 1
    return positionals[first:first + 1]


def powershell_web_targets(args):
    named, _ = powershell_args(args)
    return [named["outfile"]] if "outfile" in named else []


def both(*writers):
    """A writer for a name both shells have: the targets either reading finds."""
    return lambda args: [target for writer in writers for target in writer(args)]


# WRITERS as a PowerShell tool's command is read: the same table, with PowerShell's writers
# added. A name both shells have is read both ways, except `cp` and `mv`, which are the
# `Copy-Item` and `Move-Item` aliases only: read as getopt, `-Destination src -Path <temp>`
# would give the source for the destination.
POWERSHELL_WRITERS = dict(WRITERS)
for _names, _writer in (
        ("out-file", powershell_file_targets("filepath", "literalpath")),
        ("set-content add-content sc ac", powershell_file_targets("path", "literalpath")),
        ("tee-object", powershell_file_targets("filepath", "literalpath")),
        ("tee", both(powershell_file_targets("filepath", "literalpath"), tee_targets)),
        ("copy-item move-item cp copy cpi mv move mi", powershell_copy_targets),
        ("invoke-webrequest iwr", powershell_web_targets),
        ("curl", both(powershell_web_targets, curl_targets)),
        ("wget", both(powershell_web_targets, wget_targets))):
    POWERSHELL_WRITERS.update(dict.fromkeys(_names.split(), _writer))


def command_targets(words, writers=WRITERS):
    """The output targets one simple command's arguments name, by the ``writers`` table."""
    while words:
        first = words[0]
        if ASSIGNMENT.match(first) or first in KEYWORDS:
            words = words[1:]
        elif first in WRAPPERS:
            opts_end = 1
            while opts_end < len(words) and (
                    words[opts_end].startswith("-") or ASSIGNMENT.match(words[opts_end])):
                letter = words[opts_end][-1:]
                takes_value = (not words[opts_end].startswith("--")
                               and len(words[opts_end]) == 2
                               and letter in WRAPPERS[first])
                opts_end += 2 if takes_value else 1
            words = words[opts_end:]
        else:
            break
    if not words:
        return []
    name = os.path.basename(words[0].replace("\\", "/")).lower()
    if name.endswith(".exe"):
        name = name[:-4]
    writer = writers.get(name)
    return writer(words[1:]) if writer else []


def strip_heredocs(command):
    """Cut each here-document body out of ``command``, keeping the line that opens it."""
    out, pos = [], 0
    while True:
        m = HEREDOC.search(command, pos)
        if not m:
            break
        line_end = command.find("\n", m.end())
        if line_end < 0:
            break
        out.append(command[pos:line_end + 1])
        pos = len(command)            # an unterminated body runs to the end
        start = line_end + 1
        while start < len(command):
            end = command.find("\n", start)
            stop = end if end >= 0 else len(command)
            line = command[start:stop]
            if (line.lstrip("\t") if m.group(1) else line) == m.group(3):
                pos = stop
                break
            start = stop + 1
    out.append(command[pos:])
    return "".join(out)


PS_REDIRECT = re.compile(r"[1-6*]?(>>?)(?:&([1-6]))?")
PS_COMMAND_END = re.compile(r"&&|\|\||[;|&(){}\n]")
PS_HERE_STRING = re.compile(r"@(['\"])[ \t]*\r?\n")
PS_CONTINUATION = re.compile(r"`\r?\n")


def powershell_tokens(command):
    """``command`` read by PowerShell's rules, as the ``(is_operator, text)`` tokens
    ``bash_targets()`` makes of a POSIX command, so one pipeline reads both shells.

    A backslash is a literal character and the backtick is the escape. A single-quoted
    string is literal: its ``$`` is kept as PowerShell spells a literal one, `` `$ ``, so no
    variable is read from it. A double-quoted string is one word whose variables still
    count. A stream in front of a redirect belongs to the operator (``2>``, ``*>>``), and
    ``2>&1``, which joins two streams, becomes the ``>&`` descriptor copy. A here-string's
    body and a comment are dropped. Raises ``ValueError`` when a quote never closes.
    """
    tokens, word, i = [], None, 0

    def end_word():
        nonlocal word
        if word is not None:
            tokens.append((False, word))
            word = None

    def literal(char):
        return "`$" if char == "$" else char

    while i < len(command):
        char = command[i]
        if word is None and command.startswith("<#", i):        # a block comment
            close = command.find("#>", i)
            i = len(command) if close < 0 else close + 2
            continue
        if word is None and char == "#":                        # a comment, to the line's end
            close = command.find("\n", i)
            i = len(command) if close < 0 else close
            continue
        redirect = PS_REDIRECT.match(command, i) if word is None or char == ">" else None
        ends = PS_COMMAND_END.match(command, i)
        here = PS_HERE_STRING.match(command, i)
        continuation = PS_CONTINUATION.match(command, i)
        if redirect:
            end_word()
            if redirect.group(2):       # `2>&1` joins two streams and names no file
                tokens += [(True, ">&"), (False, redirect.group(2))]
            else:
                tokens.append((True, redirect.group(1)))
            i = redirect.end()
        elif ends:
            end_word()
            tokens.append((True, ends.group()))
            i = ends.end()
        elif char in " \t\r":
            end_word()
            i += 1
        elif continuation:              # a backtick at the end of a line joins the next one
            i = continuation.end()
        elif here:                      # the body is data, as a here-document's is
            close = command.find("\n" + here.group(1) + "@", here.end() - 1)
            i = len(command) if close < 0 else close + 3
            word = word or ""
        elif char == "`":
            word = (word or "") + literal(command[i + 1:i + 2])
            i += 2
        elif char == "'":
            word = word or ""
            while True:
                close = command.find("'", i + 1)
                if close < 0:
                    raise ValueError("No closing quotation")
                word += command[i + 1:close].replace("$", "`$")
                i = close + 1
                if command[i:i + 1] != "'":
                    break
                word += "'"             # a doubled quote is one literal quote
        elif char == '"':
            word = word or ""
            i += 1
            while True:
                if i >= len(command):
                    raise ValueError("No closing quotation")
                char = command[i]
                if char == "`":
                    word += literal(command[i + 1:i + 2])
                    i += 2
                elif char != '"':
                    word += char
                    i += 1
                elif command[i + 1:i + 2] == '"':
                    word += '"'         # a doubled quote is one literal quote
                    i += 2
                else:
                    i += 1
                    break
        elif command.startswith("${", i):                       # a braced variable name
            close = command.find("}", i)
            close = len(command) if close < 0 else close + 1
            word = (word or "") + command[i:close]
            i = close
        else:
            word = (word or "") + char
            i += 1
    end_word()
    return tokens


def bash_targets(command, powershell=False):
    """Every top-level output target in a Bash command line, or in a PowerShell one.

    Raises ``ValueError`` when the command cannot be split.
    """
    if powershell:
        return token_targets(command, powershell_tokens(command), POWERSHELL_WRITERS)
    command = strip_heredocs(command).replace("\\\n", "")
    lexer = shlex.shlex(command, posix=True, punctuation_chars=BASH_PUNCT)
    lexer.whitespace_split = True
    lexer.whitespace = lexer.whitespace.replace("\n", "")
    lexer.commenters = ""             # `#` mid-word (a URL fragment) is not a comment
    tokens = []
    for token in lexer:
        if token and all(c in BASH_PUNCT for c in token):
            tokens.extend((True, op) for op in BASH_OPS.findall(token))
        else:
            tokens.append((False, token))
    return token_targets(command, tokens, WRITERS)


def token_targets(command, tokens, writers):
    """The output targets among ``tokens``: each redirect's, and each simple command's."""
    targets, words = [], []
    in_comment = last_was_word = False
    i = 0
    while i < len(tokens):
        is_op, token = tokens[i]
        word = False
        if in_comment:
            in_comment = not (is_op and token == "\n")
            if not in_comment:
                targets += command_targets(words, writers)
                words = []
        elif not is_op:
            if token.startswith("#"):
                in_comment = True     # a comment runs to the end of the line
            else:
                words.append(token)
                word = True
        elif token in COMMAND_ENDS:
            targets += command_targets(words, writers)
            words = []
        elif token in WRITE_REDIRECTS or token in READ_REDIRECTS:
            # `2>`: shlex splits the descriptor from the operator, so a bare number written
            # against the operator is the descriptor, not the command's last argument.
            if (last_was_word and words[-1].isdigit()
                    and re.search(r"(?:^|[\s;&|()])%s[<>]" % words[-1], command)):
                words.pop()
            if i + 1 < len(tokens) and not tokens[i + 1][0]:
                i += 1
                operand = tokens[i][1]
                fd_copy = token == ">&" and re.fullmatch(r"\d+|-", operand)
                if token in WRITE_REDIRECTS and not fd_copy:
                    targets.append(operand)
        last_was_word = word
        i += 1
    targets += command_targets(words, writers)
    return targets


def bash_target_is_temp(target, powershell=False):
    """True when a Bash output target is system temp or Downloads outside the project."""
    if (PS_TEMP_VAR if powershell else TEMP_VAR).search(target):
        return True
    home = PS_HOME_VAR if powershell else HOME_VAR
    target = home.sub(lambda _m: os.path.expanduser("~"), target)
    # A destination may be a directory (`cp x /tmp`, `wget -P /tmp`), and `/tmp` itself
    # matches no `/tmp/` prefix, so a file inside it is classified too.
    inside = target.rstrip("/\\") + "/_"
    return "temp" in (location(target), location(inside))


def bash_command(payload):
    """The command when this call is the Bash tool, else None."""
    try:
        parsed = json.loads(payload)
    except ValueError:
        return "" if re.search(r'"tool_name"\s*:\s*"Bash"', payload) else None
    if not isinstance(parsed, dict) or parsed.get("tool_name") != "Bash":
        return None
    tool_input = parsed.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    return command if isinstance(command, str) else ""


def powershell_command(payload):
    """True when the hook adapter says a PowerShell tool sent this command.

    A payload that names no dialect, or one this gate does not read, is POSIX shell.
    """
    try:
        return json.loads(payload).get("shell_dialect") == "powershell"
    except (ValueError, AttributeError):
        return False


bash = bash_command(data)
if bash is not None:
    powershell = powershell_command(data)
    try:
        bash_out = bash_targets(bash, powershell)
    except ValueError:
        sys.exit(0)                   # it could not be split -> allow
    if any(bash_target_is_temp(t, powershell) for t in bash_out):
        block(LOC_MSG)
    sys.exit(0)                       # Bash: no general boundary, no secret check

# Extract the write target (tool_input.file_path). Prefer JSON; fall back to a field
# match. File paths do not contain double quotes, so the first match is the real
# target; fail open (allow on location grounds) if extraction yields nothing.
file_path = ""
try:
    file_path = (json.loads(data).get("tool_input") or {}).get("file_path") or ""
except (ValueError, AttributeError):
    m = re.search(r'"file_path"\s*:\s*"([^"]*)"', data)
    file_path = m.group(1) if m else ""

where = location(file_path)
if where == "temp":
    block(LOC_MSG)
if where == "outside":
    block(OUTSIDE_MSG)

# Secrets: PEM private keys, AWS access-key IDs, and raw Senzing license payloads
# (base64 blobs with the documented AQAAAD prefix). The long base64 tail keeps the
# check off prose that merely mentions "AQAAAD" and off .lic file *paths*.
def holds_secret(data):
    """True when `data` matches a secret pattern.

    `tests/test_secret_patterns_are_shared.py` reads the `re.search(` call below out of
    this file's text, so its shape and the name `data` stay as they are.
    """
    if re.search(
        r"BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY"
        r"|AKIA[0-9A-Z]{16}"
        r"|AQAAAD[A-Za-z0-9+/=]{16,}",
        data,
    ):
        return True
    return False


def secret_is_only_replaced(payload):
    """True for an edit whose new text holds no secret, when the payload does.

    The edit is blocked either way, because the gate judges the whole payload. This only
    decides whether the message adds where the secret is. A payload that does not parse
    cannot tell old text from new, so it gets SECRET_MSG alone. Every assistant's edit
    arrives as tool_name "Edit" with its new text in tool_input.new_string.
    """
    try:
        parsed = json.loads(payload)
    except ValueError:
        return False
    if not isinstance(parsed, dict) or parsed.get("tool_name") != "Edit":
        return False
    tool_input = parsed.get("tool_input")
    new_text = tool_input.get("new_string") if isinstance(tool_input, dict) else None
    return isinstance(new_text, str) and not holds_secret(new_text)


if holds_secret(data):
    block(SECRET_MSG + (SECRET_REPLACED_MSG if secret_is_only_replaced(data) else ""))

sys.exit(0)
