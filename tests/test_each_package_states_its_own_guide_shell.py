"""Each assistant's package states its own guide shell, and its fallback commands suit it (#27).

Until #27 every package said a guide-run block runs "with its Bash tool" in "the guide's POSIX
shell, which on Windows is Git Bash", and the line after each guide-run block repeated it. That
describes one assistant. The other profiles name their shell tool `bash`, `execute_bash` and
`run_command`, one lists a PowerShell tool as well, and no `hosts/*/checks.json` records a run on
Windows, so what shell those assistants give the guide there is not known.

`test_guide_run_blocks_declare_their_shell.py` reads `source/`, where both host blocks of the
statement sit side by side. This file builds all five packages and reads what each one ships:

1. **The host value.** `vars.shell_tool` in every `hosts/*/host.json` equals that profile's own
   `hooks.tools.shell`. `{{host.…}}` reads only `vars`, so the tool a package names is a second
   copy of the hook matcher's tool name; this is what stops the two from drifting.
   `vars.scripts_dir_powershell` is held to `vars.scripts_dir` the same way: the same path, with
   the plugin-root variable read as PowerShell reads an environment variable (`$env:NAME`,
   INV-167's #505 note).
2. **The tool and the shell, per package.** The statement at `#guide-run-blocks` names the tool
   that package's profile declares. A package in `POSIX_SHELL_KNOWN` keeps the earlier meaning: a
   POSIX shell, which on Windows is Git Bash. Every other package says the block runs in whichever
   shell that tool provides, that which shell that is on Windows is unverified, and what the guide
   does when its shell is PowerShell: translate the block with the 5.1 table in that section, run
   the translation, and treat the result as unverified.
3. **No claim the profile does not back.** In a package outside `POSIX_SHELL_KNOWN`, no Markdown
   file states a kind of shell as the guide's own, and none names, as the guide's own, a shell tool
   the profile does not declare. A condition is not a claim: "in a POSIX shell, `$!` …" and "where
   the guide's shell is PowerShell" carry no possessive before the kind of shell, and the scan
   reads only that shape.
4. **The line after each guide-run block.** One wording in every package, at every site, which
   names no shell and no tool, keeps "unverified on Windows: no test runs it there" and links the
   statement. Each package carries as many as `source/` does, so no site is lost in a build.
5. **The fallback commands.** In a package outside `POSIX_SHELL_KNOWN`, every command in
   `host-rules.md` is given twice: the POSIX form, and a Windows PowerShell 5.1 form after it that
   runs the same script, takes the scripts directory from `$env:`, closes the script's input with
   `$null |` where the POSIX form uses `< /dev/null`, and carries nothing the 5.1 table bans. A
   package in `POSIX_SHELL_KNOWN` carries no fallback command today, and a test says so.

Each check is a function returning its problems, and a negative control feeds it text that breaks
the rule and sees it reported. The package in `POSIX_SHELL_KNOWN` is itself the control for check
3: read as any other assistant's, its statement is a claim that assistant's profile does not back.

**What ran, and what did not.** On a POSIX host each POSIX form is run as written, with `sh`, from
the built package, in a throwaway bootcamp project, with the tool's input left open. A control
runs the one script that reads its input without the redirect and sees it wait.

**No test executes a PowerShell form, on any machine.** The PowerShell forms are checked by
reading (check 5), and each script is run on the input `$null |` is expected to hand it, which
runs the script and not PowerShell. No PowerShell was on `PATH` where #27 was written, so a class
that ran the forms would have had its first run in CI, never seen to pass; it was left out, and
#27's entry in `specs/IMPLEMENTED.md` records the forms as unexecuted (INV-163). Nothing here runs
on Windows either, which is what every package still says.

It does **not** establish which shell any assistant gives the guide on Windows, or that a live
guide translates a block correctly. A real run recorded in `hosts/<assistant>/checks.json` is what
moves an assistant into `POSIX_SHELL_KNOWN`, with the two host-block lines in `ground-rules.md`.

Prose is read wrap-aware (INV-346). Stdlib only (INV-108).

Enforces **INV-001**, **INV-163**, **INV-167** and **INV-300** on each built package.

Run:  python3 -m unittest discover -s tests
"""
import dataclasses
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _built import built
from _wrapped_text import collapsed_blocks

from tools.bootcamp_build.model import host_ids, load_host  # _built puts the repository on sys.path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "source"
HOSTS = tuple(host_ids())
#: The assistants whose guide shell is known: a POSIX shell, Git Bash on Windows. Every other
#: assistant's shell on Windows is unverified, and its package says so.
POSIX_SHELL_KNOWN = ("claude",)
UNVERIFIED = tuple(host for host in HOSTS if host not in POSIX_SHELL_KNOWN)

ANCHOR_ID = "guide-run-blocks"
ANCHOR = f'<a id="{ANCHOR_ID}"></a>'
#: The line after each guide-run block, with its link's path replaced: the path is relative to
#: the file, so a skill and a command write it differently.
STAMP = "Guide-run; unverified on Windows: no test runs it there ([guide-run blocks](<link>))."
STAMP_QUOTED = '"Guide-run; unverified on Windows: no test runs it there."'
STAMP_LINK = re.compile(r"\]\(([^)\s]*)#" + ANCHOR_ID + r"\)")

#: The sentence naming the tool, and the two sentences naming the shell.
TOOL_SENTENCE = re.compile(r"\*\*A guide-run block\*\* is one the guide runs itself with its `([^`]+)` tool\.")
POSIX_SENTENCE = ("It runs in the guide's POSIX shell, which on Windows is Git Bash, so it needs no "
                  "PowerShell form")
UNVERIFIED_SENTENCE = ("It runs in whichever shell that tool provides, and which shell that is on "
                       "Windows is unverified.")
#: What a package outside POSIX_SHELL_KNOWN says the guide does when its shell is PowerShell.
POWERSHELL_RULE = (
    ("**Where the guide's shell is PowerShell,** the guide translates a guide-run block to Windows "
     "PowerShell 5.1 with the table of 5.1 syntax limits above, runs the translation, and treats "
     "the result as unverified in that shell", "translate with the 5.1 table, run, treat as unverified"),
    ("A translated block that fails follows its own site's failure rule", "the failure rule"),
    ("What is already PowerShell needs no translation and is run directly, as written: a "
     "PowerShell-only guide-run block", "a PowerShell-only block is run directly"),
    ("The `powershell.exe -NoProfile -Command …` call the next bullet gives, and its `'\\''` "
     "quoting, apply only from a POSIX shell", "the wrapper applies only from a POSIX shell"),
)
#: The header of the 5.1 table the rule points at, which sits above the statement.
TABLE_HEADER = "| Bash-shaped | Why it fails on 5.1 | Use instead |"

#: A claim that the guide's own shell is a named kind: a possessive, then the kind. No profile
#: declares a shell, only tools, so outside POSIX_SHELL_KNOWN every match is unbacked.
OWN_SHELL = re.compile(
    r"(?i)\b(?:the guide's|its|your)\s+(?:own\s+)?(?:POSIX|bash|Git Bash|PowerShell|pwsh|zsh|cmd)\s+shell\b"
    r"|\bwhich on Windows is Git Bash\b")
#: A claim that the guide's own tool has a given name: a possessive, the name, then "tool".
OWN_TOOL = re.compile(r"\b(?:the guide's|its|your)\s+(?:own\s+)?`?([A-Za-z_]+)`?\s+tool\b")

#: The fence languages a fallback command is written in.
POSIX_LANGS = {"bash", "sh"}
POWERSHELL_LANGS = {"powershell", "ps1", "pwsh"}
#: The script a fallback command runs.
SCRIPT = re.compile(r'/([a-z0-9_-]+\.py)"')
#: What a Windows PowerShell 5.1 command must not carry: the 5.1 table's parser errors, a bare
#: `$NAME` where an environment variable is meant (INV-167's #505 note), and the POSIX null device.
POWERSHELL_BANNED = (
    (re.compile(r"&&|\|\|"), "a chaining operator, which 5.1 does not parse"),
    (re.compile(r"<"), "an input redirect or heredoc, which 5.1 does not parse"),
    (re.compile(r"\bpython3?\s+-c\b"), "inline `python -c`, which 5.1 re-quotes"),
    (re.compile(r"\$\{?[A-Z][A-Z0-9_]*\}?(?![\w:])"), "a bare `$NAME`, which is not the environment variable"),
    (re.compile(r"/dev/null"), "`/dev/null`, which Windows does not have"),
)


def read(path):
    return Path(path).read_bytes().decode("utf-8")


def flat(text):
    return " ".join(text.split())


def markdown(root):
    return sorted(Path(root).rglob("*.md"))


def onboarding(host_id):
    """The onboarding skill's directory in ``host_id``'s built package."""
    return built(host_id) / load_host(host_id).layout["skills"] / "bootcamp-onboarding"


def ground_rules(host_id):
    return read(onboarding(host_id) / "ground-rules.md")


def host_rules(host_id):
    return read(onboarding(host_id) / "host-rules.md")


def statement(text):
    """The one statement: from the anchor to the next `## ` heading, whitespace collapsed."""
    begin = text.index(ANCHOR)
    end = text.find("\n## ", begin)
    return flat(text[begin:len(text) if end == -1 else end])


def with_statement(text, change):
    """``text`` with its statement replaced by ``change(statement)``, for a negative control."""
    begin = text.index(ANCHOR)
    end = text.find("\n## ", begin)
    return text[:begin] + change(statement(text)) + text[len(text) if end == -1 else end:]


def shell_tools(host):
    """Every shell tool ``host``'s profile declares: the hook matcher's, and the adapter's."""
    categories = host.options.get("adapter", {}).get("tool_categories", {})
    return {host.hooks["tools"]["shell"]} | {name for name, kind in categories.items() if kind == "shell"}


#: Every name any profile gives a shell tool, and the two shells' own names. A tool named outside
#: this set (a file tool, say) is not this file's subject, and "its shell tool" names no tool.
SHELL_TOOL_WORDS = ((set().union(*(shell_tools(load_host(host)) for host in HOSTS))
                     | {"Bash", "bash", "PowerShell", "powershell"}) - {"shell"})


# --- checks: each returns a list of problems ------------------------------------------------


def host_value_problems(host):
    """``shell_tool`` is the profile's own shell tool, and the PowerShell scripts path its POSIX one."""
    problems = []
    declared = host.hooks["tools"]["shell"]
    if host.vars.get("shell_tool") != declared:
        problems.append(f"{host.id}: vars.shell_tool is {host.vars.get('shell_tool')!r}, but "
                        f"hooks.tools.shell is {declared!r}")
    posix = "${%s}" % host.vars["plugin_root_var"]
    scripts = host.vars["scripts_dir"]
    if not scripts.startswith(posix):
        return problems + [f"{host.id}: vars.scripts_dir does not start with {posix}"]
    expected = "$env:" + host.vars["plugin_root_var"] + scripts[len(posix):]
    if host.vars.get("scripts_dir_powershell") != expected:
        problems.append(f"{host.id}: vars.scripts_dir_powershell is "
                        f"{host.vars.get('scripts_dir_powershell')!r}, not {expected!r}")
    return problems


def tool_problems(text, host):
    """The statement names one tool, and it is the one ``host``'s profile declares."""
    named = TOOL_SENTENCE.findall(statement(text))
    if named != [host.hooks["tools"]["shell"]]:
        return [f"{host.id}: the statement names the tool {named!r}, but hooks.tools.shell is "
                f"{host.hooks['tools']['shell']!r}"]
    return []


def shell_problems(text, host, posix_known):
    """The statement says which shell runs a guide-run block, as #27 gives it for ``host``."""
    body = statement(text)
    problems = []
    if "host:" in body or "{{" in body:
        problems.append(f"{host.id}: a host marker or token survived the build")
    if body.count(STAMP_QUOTED) != 1:
        problems.append(f"{host.id}: the statement does not quote the line after a block once")
    want, other = ((POSIX_SENTENCE, UNVERIFIED_SENTENCE) if posix_known
                   else (UNVERIFIED_SENTENCE, POSIX_SENTENCE))
    if body.count(want) != 1:
        problems.append(f"{host.id}: the statement does not say once: {want!r}")
    if other in body:
        problems.append(f"{host.id}: the statement also says: {other!r}")
    if posix_known:
        if "Where the guide's shell is PowerShell" in body:
            problems.append(f"{host.id}: the statement gives a PowerShell rule for a POSIX shell")
        return problems
    for phrase, what in POWERSHELL_RULE:
        if phrase not in body:
            problems.append(f"{host.id}: the statement does not state {what}: {phrase!r}")
    if TABLE_HEADER not in text[:text.index(ANCHOR)]:
        problems.append(f"{host.id}: the 5.1 table the PowerShell rule points at is not above it")
    return problems


def unbacked_claims(text, host):
    """Each claim in ``text`` of the guide's own shell or shell tool that ``host`` does not declare."""
    declared = shell_tools(host)
    found = []
    for block, _ in collapsed_blocks(text):
        found += [match.group(0) for match in OWN_SHELL.finditer(block)]
        found += [match.group(0) for match in OWN_TOOL.finditer(block)
                  if match.group(1) in SHELL_TOOL_WORDS and match.group(1) not in declared]
    return found


def stamps(root):
    """``(file, wording, link)`` for each paragraph under ``root`` that links the statement."""
    found = []
    for path in markdown(root):
        for paragraph in re.split(r"\n[ \t]*\n", read(path)):
            link = STAMP_LINK.search(paragraph)
            if link:
                found.append((path, STAMP_LINK.sub("](<link>)", flat(paragraph)), link.group(1)))
    return found


def stamp_problems(root, target):
    """Every line that links the statement is the one wording, and its link reaches ``target``."""
    problems = []
    for path, wording, link in stamps(root):
        where = path.relative_to(root).as_posix()
        if wording != STAMP:
            problems.append(f"{where}: {wording[:110]!r}")
        if (path.parent / link).resolve() != Path(target).resolve():
            problems.append(f"{where}: the link {link!r} does not reach the statement")
    return problems


def fences(text):
    """``(heading, language, lines)`` for each fenced block in ``text``, in order."""
    found, heading, lines = [], None, text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("```"):
            language = lines[i][3:].strip().lower()
            close = next((j for j in range(i + 1, len(lines)) if lines[j].startswith("```")), len(lines))
            found.append((heading, language, [line for line in lines[i + 1:close] if line.strip()]))
            i = close + 1
            continue
        if lines[i].startswith("#"):
            heading = lines[i].strip()
        i += 1
    return found


def command_pairs(text):
    """``(heading, posix, powershell)`` for each POSIX command; ``powershell`` is None when the
    fence after it, under the same heading, is not a PowerShell one."""
    blocks = fences(text)
    pairs = []
    for at, (heading, language, lines) in enumerate(blocks):
        if language not in POSIX_LANGS:
            continue
        after = blocks[at + 1] if at + 1 < len(blocks) else (None, "", [])
        twin = after[2] if after[0] == heading and after[1] in POWERSHELL_LANGS else None
        pairs.append((heading, lines, twin))
    return pairs


def fallback_problems(text, host):
    """Every command in a ``host-rules.md`` has a POSIX form and a PowerShell 5.1 form."""
    problems = []
    blocks = fences(text)
    pairs = command_pairs(text)
    lone = (sum(1 for _, language, _ in blocks if language in POWERSHELL_LANGS)
            - sum(1 for _, _, twin in pairs if twin is not None))
    if lone:
        problems.append(f"{host.id}: {lone} PowerShell command(s) follow no POSIX form")
    for heading, posix, powershell in pairs:
        where = f"{host.id}: under {heading!r}"
        if len(posix) != 1:
            problems.append(f"{where}: the POSIX form is not one command: {posix!r}")
            continue
        script = SCRIPT.search(posix[0])
        if not script or f'"{host.vars["scripts_dir"]}/{script.group(1)}"' not in posix[0]:
            problems.append(f"{where}: the POSIX form does not run a script in the scripts directory")
            continue
        if powershell is None:
            problems.append(f"{where}: `{posix[0]}` rests on its POSIX form alone")
            continue
        if len(powershell) != 1:
            problems.append(f"{where}: the PowerShell form is not one command: {powershell!r}")
            continue
        command = powershell[0]
        if f'"{host.vars["scripts_dir_powershell"]}/{script.group(1)}"' not in command:
            problems.append(f"{where}: the PowerShell form does not run {script.group(1)} from "
                            f"{host.vars['scripts_dir_powershell']}")
        if "< /dev/null" in posix[0] and not command.startswith("$null | "):
            problems.append(f"{where}: the PowerShell form does not close the script's input")
        for pattern, what in POWERSHELL_BANNED:
            if pattern.search(command):
                problems.append(f"{where}: the PowerShell form carries {what}: `{command}`")
    return problems


# --- tests -----------------------------------------------------------------------------------


class TheHostValueIsTheProfilesOwnTool(unittest.TestCase):
    """Criterion: the tool a package names equals that assistant's `hooks.tools.shell`."""

    def test_every_profile(self):
        for host_id in HOSTS:
            with self.subTest(host=host_id):
                self.assertEqual(host_value_problems(load_host(host_id)), [])

    def test_the_profile_on_disk_holds_both_values(self):
        """Read as JSON, not through the loader, so the check does not rest on the loader."""
        for host_id in HOSTS:
            with self.subTest(host=host_id):
                data = json.loads(read(REPO_ROOT / "hosts" / host_id / "host.json"))
                self.assertEqual(data["vars"]["shell_tool"], data["hooks"]["tools"]["shell"])
                self.assertIn("$env:" + data["vars"]["plugin_root_var"],
                              data["vars"]["scripts_dir_powershell"])

    def test_negative_control_a_drifted_tool_name(self):
        for host_id in HOSTS:
            with self.subTest(host=host_id):
                host = load_host(host_id)
                drifted = dataclasses.replace(host, vars=dict(host.vars, shell_tool="some_other_tool"))
                self.assertTrue(host_value_problems(drifted))

    def test_negative_control_a_missing_value(self):
        host = load_host(HOSTS[0])
        without = {name: value for name, value in host.vars.items() if name != "shell_tool"}
        self.assertTrue(host_value_problems(dataclasses.replace(host, vars=without)))

    def test_negative_control_a_powershell_path_that_reads_a_bare_variable(self):
        host = load_host(UNVERIFIED[0])
        bare = dict(host.vars, scripts_dir_powershell=host.vars["scripts_dir"])
        self.assertTrue(host_value_problems(dataclasses.replace(host, vars=bare)))


class EachPackageStatesItsOwnToolAndShell(unittest.TestCase):
    """Criteria: the tool and the shell, per package, and the PowerShell rule where the shell is unverified."""

    def test_the_two_groups_cover_every_assistant(self):
        self.assertTrue(set(POSIX_SHELL_KNOWN) <= set(HOSTS))
        self.assertTrue(UNVERIFIED)
        self.assertEqual(sorted(POSIX_SHELL_KNOWN + UNVERIFIED), sorted(HOSTS))

    def test_each_package_names_its_own_tool(self):
        for host_id in HOSTS:
            with self.subTest(host=host_id):
                self.assertEqual(tool_problems(ground_rules(host_id), load_host(host_id)), [])

    def test_each_package_says_which_shell(self):
        for host_id in HOSTS:
            with self.subTest(host=host_id):
                self.assertEqual(shell_problems(ground_rules(host_id), load_host(host_id),
                                                host_id in POSIX_SHELL_KNOWN), [])

    def test_no_package_states_a_shell_or_tool_its_profile_does_not_declare(self):
        for host_id in UNVERIFIED:
            host = load_host(host_id)
            for path in markdown(built(host_id)):
                with self.subTest(host=host_id, file=path.relative_to(built(host_id)).as_posix()):
                    self.assertEqual(unbacked_claims(read(path), host), [])

    def test_the_scan_reads_the_statement_in_every_package(self):
        """A liveness check: the scan above passes on a package it never opened."""
        for host_id in HOSTS:
            with self.subTest(host=host_id):
                self.assertIn(onboarding(host_id) / "ground-rules.md", markdown(built(host_id)))
                self.assertTrue(TOOL_SENTENCE.search(statement(ground_rules(host_id))))

    def test_negative_control_the_posix_package_read_as_another_assistants(self):
        """Its statement is a claim the other profiles do not back, and it has no PowerShell rule."""
        for known in POSIX_SHELL_KNOWN:
            text = ground_rules(known)
            for host_id in UNVERIFIED:
                with self.subTest(text=known, read_as=host_id):
                    host = load_host(host_id)
                    self.assertTrue(any("POSIX shell" in claim for claim in unbacked_claims(text, host)))
                    self.assertTrue(any("Git Bash" in claim for claim in unbacked_claims(text, host)))
                    self.assertTrue(shell_problems(text, host, False))

    def test_negative_control_another_assistants_package_read_as_the_posix_one(self):
        for host_id in UNVERIFIED:
            with self.subTest(host=host_id):
                self.assertTrue(shell_problems(ground_rules(host_id), load_host(host_id), True))

    def test_negative_control_the_wording_before_27(self):
        old = ("- **A guide-run block** is one the guide runs itself with its Bash tool. It runs in "
               "the guide's\n  POSIX shell, which on Windows is Git Bash.\n\n```bash\nls\n```\n\n"
               "Guide-run in the guide's POSIX shell (Git Bash on Windows); unverified on Windows.\n")
        for host_id in UNVERIFIED:
            with self.subTest(host=host_id):
                claims = unbacked_claims(old, load_host(host_id))
                self.assertEqual(sum("POSIX shell" in claim for claim in claims), 2, claims)
                if "Bash" not in shell_tools(load_host(host_id)):
                    self.assertIn("its Bash tool", claims)

    def test_negative_control_a_tool_another_profile_declares(self):
        names = {host_id: load_host(host_id).hooks["tools"]["shell"] for host_id in HOSTS}
        for host_id in UNVERIFIED:
            host = load_host(host_id)
            foreign = sorted(set(names.values()) - shell_tools(host))
            self.assertTrue(foreign, "every profile declares every shell tool name")
            with self.subTest(host=host_id, tool=foreign[0]):
                text = ground_rules(host_id).replace(f"its `{names[host_id]}` tool",
                                                     f"its `{foreign[0]}` tool")
                self.assertTrue(tool_problems(text, host))
                self.assertTrue(unbacked_claims(text, host))

    def test_a_condition_is_not_a_claim(self):
        host = load_host(UNVERIFIED[0])
        for sentence in ("In a POSIX shell, `$!` names the server only when it is the sole job.",
                         "From a POSIX shell the guide runs it as one call.",
                         "Where the guide's shell is PowerShell, the guide translates the block.",
                         "Where your shell is PowerShell, run this form instead:",
                         "Git Bash on Windows has neither `lsof` nor `ss`.",
                         "Write generated files through Python or your file tools."):
            with self.subTest(sentence=sentence):
                self.assertEqual(unbacked_claims(sentence, host), [])

    def test_negative_control_the_powershell_rule_removed(self):
        for host_id in UNVERIFIED:
            text = ground_rules(host_id)
            for phrase, what in POWERSHELL_RULE:
                with self.subTest(host=host_id, phrase=what):
                    cut = with_statement(text, lambda body: body.replace(phrase, ""))
                    self.assertNotEqual(statement(cut), statement(text))
                    problems = shell_problems(cut, load_host(host_id), False)
                    self.assertTrue(any(what in problem for problem in problems), problems)

    def test_negative_control_the_table_moved_below_the_statement(self):
        host_id = UNVERIFIED[0]
        text = ground_rules(host_id)
        self.assertEqual(text.count(TABLE_HEADER), 1)
        moved = text.replace(TABLE_HEADER, "") + "\n" + TABLE_HEADER + "\n"
        problems = shell_problems(moved, load_host(host_id), False)
        self.assertTrue(any("5.1 table" in problem for problem in problems), problems)


class TheLineAfterABlockIsOneWordingEverywhere(unittest.TestCase):
    """Criterion: one wording, naming no shell and no tool, the same in every package."""

    def test_the_wording_names_no_shell_and_no_tool(self):
        words = STAMP.split(" ([")[0]
        names = "|".join(sorted(re.escape(name) for name in SHELL_TOOL_WORDS))
        self.assertIsNone(re.search(r"(?i)\b(?:%s|posix|git bash|pwsh|zsh|tool)\b" % names, words))
        self.assertIn("Guide-run", words)
        self.assertIn("unverified on Windows: no test runs it there", words)
        self.assertTrue(STAMP.endswith("([guide-run blocks](<link>))."))

    def test_every_site_in_every_package(self):
        for host_id in HOSTS:
            with self.subTest(host=host_id):
                self.assertEqual(stamp_problems(built(host_id), onboarding(host_id) / "ground-rules.md"), [])

    def test_every_package_carries_the_sites_the_source_has(self):
        """Derived from `source/`, never a literal count (INV-246)."""
        in_source = len(stamps(SOURCE))
        self.assertTrue(in_source)
        for host_id in HOSTS:
            with self.subTest(host=host_id):
                self.assertEqual(len(stamps(built(host_id))), in_source)

    def test_the_wording_is_the_same_in_every_package(self):
        wordings = {wording for host_id in HOSTS for _, wording, _ in stamps(built(host_id))}
        self.assertEqual(wordings, {STAMP})

    def test_negative_control_the_wording_before_27(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "ground-rules.md"
            target.write_text(ANCHOR + "\n", encoding="utf-8")
            old = Path(tmp) / "step.md"
            old.write_text("```bash\nls\n```\n\nGuide-run in the guide's POSIX shell (Git Bash on "
                           "Windows); unverified on Windows: no test runs it\nthere ([guide-run "
                           f"blocks](ground-rules.md#{ANCHOR_ID})).\n", encoding="utf-8")
            self.assertTrue(stamp_problems(tmp, target))

    def test_negative_control_a_link_that_misses_the_statement(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "ground-rules.md"
            target.write_text(ANCHOR + "\n", encoding="utf-8")
            site = Path(tmp) / "step.md"
            site.write_text(STAMP.replace("<link>", f"../ground-rules.md#{ANCHOR_ID}") + "\n",
                            encoding="utf-8")
            problems = stamp_problems(tmp, target)
            self.assertTrue(any("does not reach" in problem for problem in problems), problems)
            site.write_text(STAMP.replace("<link>", f"ground-rules.md#{ANCHOR_ID}") + "\n",
                            encoding="utf-8")
            self.assertEqual(stamp_problems(tmp, target), [])


class EveryFallbackCommandHasBothForms(unittest.TestCase):
    """Criterion: no command in a built `host-rules.md` rests on `< /dev/null` alone."""

    def test_each_package_outside_the_posix_group(self):
        for host_id in UNVERIFIED:
            with self.subTest(host=host_id):
                self.assertEqual(fallback_problems(host_rules(host_id), load_host(host_id)), [])

    def test_the_check_reads_commands_in_each_of_them(self):
        """A liveness check: a `host-rules.md` with no command would pass the test above."""
        for host_id in UNVERIFIED:
            with self.subTest(host=host_id):
                pairs = command_pairs(host_rules(host_id))
                self.assertTrue(pairs)
                self.assertTrue(any("< /dev/null" in posix[0] for _, posix, _ in pairs))

    def test_the_posix_group_carries_no_fallback_command(self):
        """So the criterion binds the other packages. A command arriving here needs its shell stated."""
        for host_id in POSIX_SHELL_KNOWN:
            with self.subTest(host=host_id):
                self.assertEqual(fences(host_rules(host_id)), [])

    def test_negative_control_the_powershell_forms_removed(self):
        for host_id in UNVERIFIED:
            with self.subTest(host=host_id):
                text = re.sub(r"(?ms)^```powershell\n.*?^```\n", "", host_rules(host_id))
                problems = fallback_problems(text, load_host(host_id))
                self.assertEqual(sum("rests on its POSIX form alone" in p for p in problems),
                                 len(command_pairs(host_rules(host_id))), problems)

    def test_negative_control_each_banned_shape(self):
        host_id = UNVERIFIED[0]
        host = load_host(host_id)
        good = command_pairs(host_rules(host_id))[0][2][0]
        script = SCRIPT.search(good).group(1)
        for bad, what in (
                (good.replace("$null | ", "") + " < /dev/null", "an input redirect"),
                (good.replace("$null | ", ""), "does not close the script's input"),
                (good.replace(host.vars["scripts_dir_powershell"], host.vars["scripts_dir"]),
                 "does not run " + script),
                (good.replace(host.vars["scripts_dir_powershell"], host.vars["scripts_dir"]),
                 "a bare `$NAME`"),
                ("cd . && " + good, "a chaining operator"),
                ("python3 -c \"print(1)\"; " + good, "inline `python -c`")):
            with self.subTest(what=what):
                text = host_rules(host_id).replace(good, bad, 1)
                self.assertNotEqual(text, host_rules(host_id))
                problems = fallback_problems(text, host)
                self.assertTrue(any(what in problem for problem in problems), problems)

    def test_negative_control_a_powershell_form_under_another_heading(self):
        host_id = UNVERIFIED[0]
        text = host_rules(host_id).replace("\nWhere your shell is PowerShell",
                                           "\n## Another section\n\nWhere your shell is PowerShell", 1)
        self.assertNotEqual(text, host_rules(host_id))
        problems = fallback_problems(text, load_host(host_id))
        self.assertTrue(any("rests on its POSIX form alone" in p for p in problems), problems)
        self.assertTrue(any("follow no POSIX form" in p for p in problems), problems)


def bootcamp_project(root):
    """A directory the hook scripts read as a bootcamp in progress."""
    project = Path(root) / "project"
    (project / "config").mkdir(parents=True)
    (project / "config" / "bootcamp_progress.json").write_text(json.dumps({
        "current_module": "module-04-data-collection", "current_step": 2, "modules_completed": [],
    }), encoding="utf-8")
    return project


def environment(host_id):
    """This process's environment, with the package's plugin-root variable set to the built package."""
    return dict(os.environ, **{load_host(host_id).vars["plugin_root_var"]: str(built(host_id))})


def run_with_open_input(argv, cwd, env, timeout):
    """Run ``argv`` with its input left open and unwritten, as a tool that never closes it does.

    Returns ``(exit code, stdout, stderr)``; the exit code is None when ``argv`` was still running
    at ``timeout`` seconds.
    """
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        # Its own session, so a command still waiting at the timeout is ended with its children.
        process = subprocess.Popen(argv, cwd=str(cwd), env=env, stdin=subprocess.PIPE,
                                   stdout=out, stderr=err, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            code = None
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        finally:
            process.stdin.close()
        out.seek(0)
        err.seek(0)
        return code, out.read().decode("utf-8", "replace"), err.read().decode("utf-8", "replace")


@unittest.skipUnless(shutil.which("sh") and os.name == "posix",
                     "needs a POSIX sh to run the POSIX fallback forms as written")
class ThePosixFormsRun(unittest.TestCase):
    """Each POSIX form, as its package writes it, in a throwaway bootcamp project."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = bootcamp_project(self.tmp.name)

    def test_each_posix_form_runs_as_written(self):
        for host_id in UNVERIFIED:
            for heading, posix, _ in command_pairs(host_rules(host_id)):
                with self.subTest(host=host_id, command=posix[0]):
                    code, out, err = run_with_open_input(["sh", "-c", posix[0]], self.project,
                                                         environment(host_id), 120)
                    self.assertEqual(code, 0, f"{heading}: {out}\n{err}")

    def test_the_commands_do_what_their_sections_say(self):
        """Not only exit 0: the resume command prints, and the checkpoint command leaves its file."""
        host_id = UNVERIFIED[0]
        commands = {SCRIPT.search(posix[0]).group(1): posix[0]
                    for _, posix, _ in command_pairs(host_rules(host_id))}
        code, out, _ = run_with_open_input(["sh", "-c", commands["session-start.py"]], self.project,
                                           environment(host_id), 120)
        self.assertEqual(code, 0)
        self.assertTrue(out.strip(), "the resume command printed nothing in a bootcamp project")
        code, _, err = run_with_open_input(["sh", "-c", commands["checkpoint-tick.py"]], self.project,
                                           environment(host_id), 120)
        self.assertEqual(code, 0, err)
        self.assertTrue((self.project / "docs" / "progress" / "recap_checkpoint.md").is_file())

    def test_negative_control_without_the_redirect_the_checkpoint_command_waits(self):
        """Why the input is closed in both forms: this script reads its input to the end."""
        host_id = UNVERIFIED[0]
        command = next(posix[0] for _, posix, _ in command_pairs(host_rules(host_id))
                       if "checkpoint-tick.py" in posix[0])
        self.assertIn(" < /dev/null", command)
        code, _, _ = run_with_open_input(["sh", "-c", command.replace(" < /dev/null", "")],
                                         self.project, environment(host_id), 3)
        self.assertIsNone(code, "the command ended with its input still open")

    def test_each_script_takes_the_input_powershell_hands_it(self):
        """No input, or one empty line: what `$null |` is expected to give. This runs the script,
        not PowerShell, so it does not show what PowerShell hands a script."""
        for host_id in UNVERIFIED:
            scripts = built(host_id) / load_host(host_id).layout["scripts"]
            for _, posix, _ in command_pairs(host_rules(host_id)):
                script = scripts / SCRIPT.search(posix[0]).group(1)
                for handed in (b"", b"\r\n", b"\n"):
                    with self.subTest(host=host_id, script=script.name, handed=handed):
                        self.assertTrue(script.is_file(), script)
                        got = subprocess.run([sys.executable, str(script)], input=handed,
                                             cwd=str(self.project), env=environment(host_id),
                                             capture_output=True, timeout=120)
                        self.assertEqual(got.returncode, 0, got.stderr.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main()
