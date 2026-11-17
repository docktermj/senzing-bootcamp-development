"""Each package names a bootcamp operation only in the form its assistant offers (issue #28).

The bootcamp has five operations, one per file in `source/commands/`. The Claude package ships
them as slash commands. The other packages carry no `commands/` directory: the build turns each
command into a skill of the same name, and their install pages tell the bootcamper to ask for
an operation in plain English ("there is nothing to memorize"). Until issue #28 the shared text
named the slash commands on every assistant, so four packages told the bootcamper to type a
command that nobody had checked exists there, 28 times each.

What holds now, and what this file checks:

1. **No slash form in a package that ships no commands.** Every file of every such package is
   read, with no exceptions list. The names come from `source/commands/`, so a command added
   later is covered without a change here. A name inside a path
   (`skills/package-bootcamp/SKILL.md`) is not a mention; the pattern that tells the two apart
   is the one `test_documented_commands_match_the_shipped_set.py` already holds.
2. **Each assistant's form is its own host value.** `hosts/<assistant>/host.json` declares
   `invoke_<command>` for each operation. Claude's values are the slash commands. Every other
   assistant's value is the phrase in the "Say" column of its own built install page, in the
   row for the same operation. The page writes the phrase in curly quotes and the value in
   straight ones; the words are compared and the style of the quotation marks is not.
   `command_prefix`, which nothing read, is in no profile.
3. **The closing line of graduation is pinned in both forms**, and the finished-bootcamp reply
   uses the same sentence (INV-057; the amendment that says so is drafted for
   `/review-invariants`, and `specs/INVARIANTS.md` is not read here).
4. **The message `session-start.py` prints for a finished bootcamp stays ASCII-only** on every
   assistant. It is printed from a double-quoted string in the script, so the request is
   written there in straight single quotes, from a host value of its own.

How the source says it: a sentence the bootcamper is shown, or one whose wording must differ,
sits in a `host:only` / `host:except` block; an inline mention and every site in a script takes
the host value. This file reads the built packages, where either mechanism has to come out
right.

⚠️ **What this cannot establish.** Whether saying a phrase, or typing a slash form, reaches
the operation on a real assistant. That is a run on the assistant, recorded in
`hosts/<assistant>/checks.json`; this change records none.

Stdlib only; each package is built from the current source by `_built.built` (INV-108).

Run:  python3 -m unittest discover -s tests
"""
import functools
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _built import SOURCE_DIR, built, load_host  # noqa: E402
from _invocations import (  # noqa: E402
    COMMAND_HOSTS, HOSTS, PACKAGE_IN_STRING, PACKAGE_LINE_COMMAND, PACKAGE_LINE_REQUEST,
    REQUEST_HOSTS, command_names, invocation, mention, package_line, package_path, package_text,
    scripts_dir, value_name)
from test_documented_commands_match_the_shipped_set import (  # noqa: E402
    COMMAND, SITE_DIR, commands_tip, visible)
from tools.bootcamp_build.model import HOSTS_DIR, load_declaration, load_hosts  # noqa: E402
from tools.bootcamp_build.site import build_site  # noqa: E402

GRADUATION = "skills/graduation/SKILL.md"
ONBOARDING = "skills/bootcamp-onboarding/SKILL.md"
DISCOVER = "skills/module-07-query-visualize-discover/phase2b-discover.md"
SESSION_START = "scripts/session-start.py"

#: Every quotation mark a phrase is written in: straight, and the curly ones the page uses.
QUOTATION_MARKS = "\"'“”‘’"

#: One row of the install page's "Bootcamp requests" table: what to say, and what it does.
ROW = re.compile(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", re.S)

#: The word every operation's name shares, which therefore tells no two of them apart.
SHARED_WORD = "bootcamp"

#: The finished-bootcamp reply's opening, which the closing line's sentence follows.
FINISHED_LEAD = "Your Senzing bootcamp is complete. "

#: The Module 7 line the bootcamper is shown when generated data lacks what was promised.
REPORT_LINE_COMMAND = "You can report it with `/bootcamp-feedback`.\""
REPORT_LINE_REQUEST = "You can report it by saying \"Bootcamp feedback\".\""


def flat(text):
    return " ".join(text.split())


def slash_forms(text, names=None):
    """Every slash form of a command name in ``text``; a name inside a path is not one."""
    names = set(command_names() if names is None else names)
    return [found for found in COMMAND.findall(text) if found[1:] in names]


def package_files(host_id):
    """``(relative path, text)`` for every file in ``host_id``'s built package, none left out.

    A file that is not UTF-8 is read with the undecodable bytes replaced, so it is still
    searched.
    """
    root = built(host_id)
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path.relative_to(root).as_posix(), path.read_bytes().decode("utf-8", "replace")


def slash_forms_in_package(host_id):
    """``path:line: form`` for every slash form of a command name in ``host_id``'s package."""
    return ["%s:%d: %s" % (relative, number, form)
            for relative, text in package_files(host_id)
            for number, line in enumerate(text.splitlines(), start=1)
            for form in slash_forms(line)]


def words(text):
    """``text`` without its quotation marks, whatever their style, and with spaces collapsed."""
    return " ".join("".join(" " if ch in QUOTATION_MARKS else ch for ch in text).split())


@functools.lru_cache(maxsize=None)
def install_pages():
    """``{assistant: HTML}``: every assistant's install page, built from the current site."""
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch) / "site"
        build_site(SITE_DIR, load_hosts(), load_declaration(SOURCE_DIR), out)
        return {host: (out / host / "index.html").read_text(encoding="utf-8") for host in HOSTS}


def say_rows(page):
    """``[(phrase, row text)]`` for the page's "Bootcamp requests" table, header left out."""
    return [(visible(say), visible(say + " " + does)) for say, does in ROW.findall(commands_tip(page))]


def own_words(command):
    """The words of a command's name that tell it from the others."""
    return [word for word in command.split("-") if word != SHARED_WORD]


def rows_for(command, rows):
    """The rows whose text names every one of ``command``'s own words, as whole words."""
    return [phrase for phrase, text in rows
            if all(re.search(r"(?i)(?<![\w/])%s(?![\w/])" % re.escape(word), text)
                   for word in own_words(command))]


def value_problems(host_id, variables, page):
    """What is wrong with how ``variables`` name each operation, against ``page``'s table."""
    rows = say_rows(page)
    problems = []
    claimed = []
    for command in command_names():
        name = value_name(command)
        if name not in variables:
            problems.append("hosts/%s/host.json declares no %s" % (host_id, name))
            continue
        found = rows_for(command, rows)
        if len(found) != 1:
            problems.append("%d rows of %s's install page are for %s; one is needed"
                            % (len(found), host_id, command))
            continue
        claimed.append(found[0])
        if words(variables[name]) != words(found[0]):
            problems.append("%s is %r on %s, and its install page says %r"
                            % (name, variables[name], host_id, found[0]))
    unclaimed = [phrase for phrase, _ in rows if phrase not in claimed]
    if unclaimed and not problems:
        problems.append("%s's install page has rows no command claims: %s"
                        % (host_id, ", ".join(unclaimed)))
    return problems


def finished_project(test):
    """A scratch project whose bootcamp graduation has ended."""
    scratch = tempfile.TemporaryDirectory()
    test.addCleanup(scratch.cleanup)
    root = Path(scratch.name)
    (root / "config").mkdir()
    (root / "config" / "bootcamp_preferences.yaml").write_text(
        "name: Ada\nbootcamp_complete: true\n", encoding="utf-8")
    return root


def finished_message(test, host_id):
    """What ``host_id``'s built ``session-start.py`` prints on a finished project, as bytes."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run([sys.executable, str(scripts_dir(host_id) / "session-start.py")],
                          input=b"{}", capture_output=True, cwd=str(finished_project(test)),
                          env=env, timeout=60)
    test.assertEqual(0, proc.returncode, proc.stderr.decode("utf-8", "replace"))
    return proc.stdout


class TheSetsAreNotEmpty(unittest.TestCase):
    """INV-265: a check over an empty set of names, assistants or rows passes on nothing."""

    def test_the_commands_were_found(self):
        self.assertIn("start-bootcamp", command_names())
        self.assertGreaterEqual(len(command_names()), 3)

    def test_one_assistant_ships_commands_and_the_others_do_not(self):
        self.assertEqual(("claude",), COMMAND_HOSTS,
                         "another assistant's package now ships commands: decide which form its "
                         "host values and the source's host blocks give it")
        self.assertGreaterEqual(len(REQUEST_HOSTS), 2)
        self.assertEqual(set(HOSTS), set(COMMAND_HOSTS) | set(REQUEST_HOSTS))

    def test_every_install_page_has_a_row_for_each_command(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual(len(command_names()), len(say_rows(install_pages()[host])))


class NoRequestPackageNamesASlashCommand(unittest.TestCase):
    """Criterion 1: no slash form of a command name, in any file, with no exceptions list."""

    def test_no_file_names_one(self):
        for host in REQUEST_HOSTS:
            with self.subTest(host=host):
                self.assertGreater(len(list(package_files(host))), 50, "the package was not read")
                self.assertEqual([], slash_forms_in_package(host))

    def test_the_same_scan_finds_every_command_in_a_package_that_ships_them(self):
        """Control: the scan reads what it claims to. The Claude package names all five, in its
        Markdown and in its scripts, and the scan reports each."""
        for host in COMMAND_HOSTS:
            with self.subTest(host=host):
                found = slash_forms_in_package(host)
                self.assertEqual({"/" + name for name in command_names()},
                                 {line.rsplit(": ", 1)[1] for line in found})
                self.assertTrue(any(".py:" in line for line in found), "no script was read")
                self.assertTrue(any(".md:" in line for line in found), "no Markdown was read")

    def test_a_planted_slash_form_is_found_wherever_it_is_written(self):
        for text in ("Run `/package-bootcamp` anytime.", "name /package-bootcamp, and end",
                     "# reachable by `/bootcamp-note` and", "suggest /bootcamp-feedback.",
                     "name ``/graduate`` and ask", "(/start-bootcamp)"):
            with self.subTest(text=text):
                self.assertEqual(1, len(slash_forms(text)))

    def test_a_name_inside_a_path_is_not_a_mention(self):
        """Must-not-flag (INV-282): a skill's directory and a command's file carry the name."""
        for text in ("skills/package-bootcamp/SKILL.md", "commands/graduate.md",
                     "`../graduate/SKILL.md`", "${PLUGIN_ROOT}/skills/start-bootcamp",
                     "https://example.com/graduate/now", "/graduate.md", "/graduated",
                     "/bootcamp-notes", "docs/bootcamp-feedback"):
            with self.subTest(text=text):
                self.assertEqual([], slash_forms(text))

    def test_a_command_added_later_is_covered(self):
        """The names are read from ``source/commands/``; a sixth needs no change here."""
        self.assertEqual(["/bootcamp-status"],
                         slash_forms("Try `/bootcamp-status`.", command_names() + ("bootcamp-status",)))
        self.assertEqual([], slash_forms("Try `/bootcamp-status`."))


class EveryAssistantDeclaresEachOperation(unittest.TestCase):
    """Criterion 2: the invocation of each operation is a host value on every assistant."""

    def test_every_profile_declares_each_operation_and_no_other(self):
        expected = {value_name(command) for command in command_names()} | {PACKAGE_IN_STRING}
        for host in HOSTS:
            with self.subTest(host=host):
                declared = {name for name in load_host(host).vars if name.startswith("invoke_")}
                self.assertEqual(expected, declared)

    def test_a_package_that_ships_commands_names_the_slash_commands(self):
        for host in COMMAND_HOSTS:
            for command in command_names():
                with self.subTest(host=host, command=command):
                    self.assertEqual("/" + command, invocation(host, command))

    def test_every_other_assistant_names_the_phrase_its_install_page_says(self):
        for host in REQUEST_HOSTS:
            with self.subTest(host=host):
                self.assertEqual([], value_problems(host, load_host(host).vars,
                                                    install_pages()[host]))

    def test_the_issues_table_is_what_the_values_say(self):
        """The five requests, as the issue's Goal lists them, in straight double quotes."""
        requests = {"start-bootcamp": "\"Start the bootcamp\"",
                    "bootcamp-feedback": "\"Bootcamp feedback\"",
                    "bootcamp-note": "\"Make a note\"", "graduate": "\"Graduate\"",
                    "package-bootcamp": "\"Back up the bootcamp\""}
        for host in REQUEST_HOSTS:
            for command, request in requests.items():
                with self.subTest(host=host, command=command):
                    self.assertEqual(request, invocation(host, command))

    def test_the_marks_are_ignored_and_the_words_are_not(self):
        self.assertEqual(words("\"Back up the bootcamp\""), words("“Back up the bootcamp”"))
        self.assertEqual(words("'Make a note'"), words("“Make a note”"))
        self.assertNotEqual(words("\"Back up a bootcamp\""), words("“Back up the bootcamp”"))
        self.assertNotEqual(words("\"back up the bootcamp\""), words("“Back up the bootcamp”"))

    def test_control_a_value_for_another_operation_is_reported(self):
        """Two values swapped still name phrases the page says, each for the wrong operation."""
        host = REQUEST_HOSTS[0]
        variables = dict(load_host(host).vars)
        note, graduate = value_name("bootcamp-note"), value_name("graduate")
        variables[note], variables[graduate] = variables[graduate], variables[note]
        self.assertEqual(2, len(value_problems(host, variables, install_pages()[host])))

    def test_control_a_slash_command_or_a_missing_value_is_reported(self):
        host = REQUEST_HOSTS[0]
        page = install_pages()[host]
        variables = dict(load_host(host).vars, **{value_name("graduate"): "/graduate"})
        self.assertEqual(1, len(value_problems(host, variables, page)))
        del variables[value_name("graduate")]
        self.assertEqual(1, len(value_problems(host, variables, page)))

    def test_control_a_row_no_command_claims_is_reported(self):
        host = REQUEST_HOSTS[0]
        page = install_pages()[host].replace(
            "</tbody>", "<tr><td>“Show my progress”</td><td>Show the journey map.</td></tr></tbody>", 1)
        self.assertNotEqual(install_pages()[host], page, "the control planted nothing")
        self.assertEqual(1, len(value_problems(host, load_host(host).vars, page)))

    def test_the_form_a_script_prints_is_the_same_request_in_single_quotes(self):
        """A double quote would end the string the script prints it from."""
        for host in HOSTS:
            with self.subTest(host=host):
                variables = load_host(host).vars
                self.assertEqual(variables[value_name("package-bootcamp")].replace("\"", "'"),
                                 variables[PACKAGE_IN_STRING])
                self.assertNotRegex(variables[PACKAGE_IN_STRING], r"[\"\\]")
                self.assertTrue(variables[PACKAGE_IN_STRING].isascii())

    def test_no_profile_declares_command_prefix(self):
        seen = 0
        for path in sorted(HOSTS_DIR.glob("*/host.json")):
            seen += 1
            with self.subTest(profile=path.parent.name):
                self.assertNotIn("command_prefix", path.read_text(encoding="utf-8"))
                json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(HOSTS), seen)


class TheClosingLineIsPinnedInBothForms(unittest.TestCase):
    """Criterion 3: the request form, word for word, wherever the package ships no commands."""

    def test_the_two_forms_differ_only_in_how_the_operation_is_named(self):
        tail = " anytime to bundle your bootcamp results into one zip you can archive, move to " \
               "another machine, or share with others."
        self.assertEqual("Run `/package-bootcamp`" + tail, PACKAGE_LINE_COMMAND)
        self.assertEqual("Say \"Back up the bootcamp\"" + tail, PACKAGE_LINE_REQUEST)

    def test_graduation_shows_its_own_form_once_as_a_line_of_its_own(self):
        for host in HOSTS:
            with self.subTest(host=host):
                lines = [line.strip() for line in package_text(host, GRADUATION).splitlines()]
                self.assertEqual(1, lines.count(package_line(host)))

    def test_no_package_carries_the_other_form(self):
        for host in HOSTS:
            other = PACKAGE_LINE_REQUEST if host in COMMAND_HOSTS else PACKAGE_LINE_COMMAND
            for relative in (GRADUATION, ONBOARDING, "commands/graduate.md"):
                with self.subTest(host=host, file=relative):
                    self.assertNotIn(other[:other.index(" anytime")],
                                     flat(package_text(host, relative)))

    def test_the_line_names_the_assistants_own_value(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIn(invocation(host, "package-bootcamp"), package_line(host))

    def test_the_finished_reply_uses_the_same_sentence(self):
        for host in HOSTS:
            with self.subTest(host=host):
                reply = flat(re.sub(r"(?m)^\s*>[ \t]?", "", package_text(host, ONBOARDING)))
                self.assertEqual(1, reply.count(FINISHED_LEAD + package_line(host)))

    def test_the_graduate_operation_quotes_the_same_line(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIn("verbatim: \"%s\"" % package_line(host),
                              flat(package_text(host, "commands/graduate.md")))


class TheFinishedMessageIsAscii(unittest.TestCase):
    """Criterion 6: the message for a finished bootcamp, from each package's own script."""

    def test_it_is_ascii_and_names_the_operation_in_the_assistants_form(self):
        for host in HOSTS:
            with self.subTest(host=host):
                out = finished_message(self, host)
                self.assertTrue(out.isascii(), "a Windows console code page can break it")
                text = out.decode("ascii")
                self.assertIn("say the bootcamp is complete, name %s, and end on the one open "
                              "question it pins" % load_host(host).vars[PACKAGE_IN_STRING], text)
                self.assertNotIn("{{", text)

    def test_a_request_is_printed_in_straight_single_quotes(self):
        for host in REQUEST_HOSTS:
            with self.subTest(host=host):
                self.assertIn(b"name 'Back up the bootcamp', and end", finished_message(self, host))
        for host in COMMAND_HOSTS:
            with self.subTest(host=host):
                self.assertIn(b"name /package-bootcamp, and end", finished_message(self, host))

    def test_every_script_that_takes_a_value_still_parses(self):
        """A value is placed in a script as written, so one with a double quote in it, placed
        inside a double-quoted string, would leave a script that does not parse."""
        takers = sorted(path.name for path in (SOURCE_DIR / "scripts").glob("*.py")
                        if "{{host.invoke_" in path.read_text(encoding="utf-8"))
        self.assertIn("session-start.py", takers)
        for host in HOSTS:
            for name in takers:
                with self.subTest(host=host, script=name):
                    path = package_path(host, "scripts/" + name)
                    compile(path.read_text(encoding="utf-8"), str(path), "exec")

    def test_control_a_double_quoted_request_would_break_the_script(self):
        source = (SOURCE_DIR / SESSION_START).read_text(encoding="utf-8")
        token = "{{host.%s}}" % PACKAGE_IN_STRING
        self.assertEqual(1, source.count(token))
        with self.assertRaises(SyntaxError):
            compile(source.replace(token, "\"Back up the bootcamp\""), "session-start.py", "exec")


class AChangedSentenceReadsWhole(unittest.TestCase):
    """Criterion 5: where the wording had to differ, each form is a sentence of its own."""

    def test_the_module_7_line(self):
        for host in HOSTS:
            mine, other = ((REPORT_LINE_COMMAND, REPORT_LINE_REQUEST) if host in COMMAND_HOSTS
                           else (REPORT_LINE_REQUEST, REPORT_LINE_COMMAND))
            with self.subTest(host=host):
                text = flat(package_text(host, DISCOVER))
                self.assertEqual(1, text.count(mine))
                self.assertNotIn(other, text)

    def test_no_request_is_called_a_command(self):
        """`the "Make a note" command` names a command that a request package does not have."""
        for host in REQUEST_HOSTS:
            values = [invocation(host, command) for command in command_names()]
            for relative, text in package_files(host):
                if not relative.endswith(".md"):
                    continue
                collapsed = flat(text)
                for value in values:
                    with self.subTest(host=host, file=relative, value=value):
                        self.assertNotRegex(collapsed, re.escape(value) + r"`? command\b")

    def test_an_inline_mention_is_the_value_in_backticks(self):
        """The same line on every assistant, with the operation taken from its host value."""
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIn("name %s, and end on one open question"
                              % mention(host, "package-bootcamp"),
                              flat(package_text(host, ONBOARDING)))
                self.assertIn("and suggest %s. Then continue below."
                              % mention(host, "bootcamp-feedback"),
                              flat(package_text(host, DISCOVER)))


if __name__ == "__main__":
    unittest.main()
