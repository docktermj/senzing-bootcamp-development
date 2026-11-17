"""`since` names the corpus it counted, and counts what shipped where it does not look.

⛔ **A zero was ambiguous and nothing said so.** `added_rule_lines` filters twice -- to
`SCAN_ROOTS`, and to `.md` -- so a run that shipped a ⛔ rule in `docs/` or in a `.py` file under
those very roots was reported as having added **none**. The consumer,
`test_new_hard_rules_are_cited_or_deferred`, then read that zero as an empty range and skipped:
**green by not running**. Four runs in one session did exactly that (#108).

⛔ **The corpus stays narrow, and that is the answer rather than an omission.** Measured
2026-09-23 over the whole repository: **862** hard-rule lines inside it, against **1,360** in
`specs/`, **615** in `tests/`, **141** in non-`.md` files inside the scanned roots and **18**
under `docs/`. Widening to `specs/` would count the invariant register and the ledger entry each
run is about to write; `tests/` docstrings state rules *about* rules. A figure dominated by the
records that describe the rules answers nothing.

⚠️ **So the defect was SILENCE, not under-counting**, and the fix is disclosure: the report names
its roots and its `.md` filter on every run, and counts hard-rule lines added in
`UNCOUNTED_RULE_HOMES` -- `docs/`, and non-`.md` files under the scanned roots -- so a reader
sees `0 counted, N outside` instead of a bare `0`.

⚠️ **`specs/` and `tests/` are deliberately NOT in that outside count.** Including them would
make it non-zero on every run and therefore worth ignoring, which is how a signal becomes noise.
`RecordsAboutRulesAreNotRuleHomes` pins both exclusions.

⚠️ **What this does NOT establish:** that a rule found outside the corpus was registered or
deferred, or that the corpus boundary is the right one. It establishes that a zero can no longer
be read as "nothing was added" when something was.

⚠️ **Dated note (#9): the host-side inputs joined.** `hosts` is a scanned root, so a rule in
a Markdown file under it is counted with `+`, and a rule in its `.json`, `.html` or `.py`
files is outside with `!`, as a non-`.md` file under any scanned root is.
`tools/bootcamp_build/` is an uncounted rule home beside `docs/`.
`HostSideInputsAreReportedWithTheRightMarker` runs the view itself over both.

No phrase-level pattern (#9): its line reads are of `conformance.py`'s stdout, where the unit is
the report line the view prints, and of no Markdown prose.

Source issues: #108, #9.

Stdlib only; the producer is loaded by path (INV-108).

Enforces **INV-431** (registered 2026-11-16): the audit and review tools read every directory
the build takes package text from. This module holds its own tool's part of that rule on
fixture trees; it cannot establish that a directory added later has joined the roots.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFORMANCE = REPO_ROOT / ".claude" / "skills" / "production-readiness-audit" / "conformance.py"


def producer():
    spec = importlib.util.spec_from_file_location("conformance", CONFORMANCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def consumer_helpers():
    spec = importlib.util.spec_from_file_location(
        "new_hard_rules", REPO_ROOT / "tests" / "test_new_hard_rules_are_cited_or_deferred.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


class TheCorpusIsStatedOnEveryReport(unittest.TestCase):
    def test_the_report_names_its_roots_and_its_file_filter(self):
        out = subprocess.run([sys.executable, str(CONFORMANCE), "since", "--ref", "HEAD"],
                             cwd=str(REPO_ROOT), capture_output=True, text=True).stdout
        self.assertIn("CORPUS:", out,
                      "`since` does not state the corpus it counted over, so a zero cannot be "
                      "told from 'nothing was looked at'")
        for root in producer().SCAN_ROOTS:
            with self.subTest(root=root):
                self.assertIn(root, out, "the corpus line omits the root %r" % root)
        self.assertIn("`.md` only", out,
                      "the corpus line omits the file-type filter, which is half the exclusion")

    def test_it_reports_the_outside_count_even_when_it_is_zero(self):
        """A line that appears only on drift is a line nobody learns to look for."""
        out = subprocess.run([sys.executable, str(CONFORMANCE), "since", "--ref", "HEAD"],
                             cwd=str(REPO_ROOT), capture_output=True, text=True).stdout
        self.assertIn("OUTSIDE the corpus", out)


class RuleHomesAreClassifiedCorrectly(unittest.TestCase):
    """The fixtures, derived from the claim rather than from today's diff (INV-282)."""

    def setUp(self):
        self.mod = producer()
        self.repo = Path(self.enterContext(tempfile.TemporaryDirectory()))
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "seed")
        self.base = git(self.repo, "rev-parse", "HEAD").stdout.strip()

    def add(self, relpath, text):
        p = self.repo / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "add %s" % relpath)

    def outside(self):
        got = self.mod.added_rules_outside_the_corpus(self.repo, self.base)
        return sorted(got) if got else []

    RULE = "⛔ **A rule that must be counted.**\n"

    def test_a_rule_in_docs_is_an_uncounted_rule_home(self):
        self.add("docs/development.md", self.RULE)
        self.assertEqual(["docs/development.md"], self.outside())

    def test_a_rule_in_a_py_file_under_a_scanned_root_is_one_too(self):
        """The second axis: inside SCAN_ROOTS, but the corpus takes `.md` only."""
        self.add(".claude/skills/x/tool.py", "#: " + self.RULE)
        self.assertEqual([".claude/skills/x/tool.py"], self.outside())

    def test_a_rule_in_a_scanned_markdown_file_is_NOT_outside(self):
        """It is counted by `added_rule_lines`; reporting it here would double-count it."""
        self.add(".claude/skills/x/SKILL.md", self.RULE)
        self.assertEqual([], self.outside())

    def test_a_rule_in_host_json_is_an_uncounted_rule_home(self):
        """#9: under a scanned root, and not Markdown."""
        self.add("hosts/kiro/host.json", '{"note": "%s"}\n' % self.RULE.strip())
        self.assertEqual(["hosts/kiro/host.json"], self.outside())

    def test_a_rule_in_the_build_tool_is_an_uncounted_rule_home(self):
        """#9: the build appends package text from string constants in its own source."""
        self.add("tools/bootcamp_build/emit.py", 'NOTE = (\n    "%s "\n)\n' % self.RULE.strip())
        self.assertEqual(["tools/bootcamp_build/emit.py"], self.outside())

    def test_a_rule_under_tools_but_outside_the_build_tool_is_not_counted(self):
        """The rule home is `tools/bootcamp_build/`, not everything under `tools/`."""
        self.add("tools/elsewhere/helper.py", "#: " + self.RULE)
        self.assertEqual([], self.outside())

    def test_a_rule_in_host_markdown_is_NOT_outside(self):
        """#9: host Markdown is in the corpus, so it is counted once, by `added_rule_lines`."""
        self.add("hosts/chatgpt/fragments/hooks-setup.md", self.RULE)
        self.add("hosts/kiro/files/skills/x/SKILL.md", self.RULE)
        self.assertEqual([], self.outside())
        self.assertEqual(
            ["hosts/chatgpt/fragments/hooks-setup.md", "hosts/kiro/files/skills/x/SKILL.md"],
            sorted(self.mod.added_rule_lines(self.repo, self.base)))


class RecordsAboutRulesAreNotRuleHomes(RuleHomesAreClassifiedCorrectly):
    """⛔ The exclusions that keep the count a signal rather than noise."""

    def test_specs_is_not_counted(self):
        """It is the invariant register and the ledger every run writes into."""
        self.add("specs/IMPLEMENTED.md", self.RULE)
        self.assertEqual(
            [], self.outside(),
            "a ⛔ line in specs/ was counted as a rule shipped outside the corpus. That file "
            "is the ledger; this count would then be non-zero on every run and ignored")

    def test_tests_is_not_counted(self):
        """Docstrings there state rules ABOUT rules."""
        self.add("tests/test_x.py", '"""' + self.RULE + '"""\n')
        self.assertEqual([], self.outside())


class HostSideInputsAreReportedWithTheRightMarker(unittest.TestCase):
    """#9 — the view itself, run over a range that adds a rule to each host-side input.

    A Markdown file under `hosts/` is in the corpus and its rule prints with `+`; `host.json`
    and the build tool's `emit.py` are outside it and their rules print with `!`. Both
    parsers that read this report are run over it too, because the markers exist for them.
    """

    RULE = "⛔ **A host-side rule that must be listed.**"
    MARKDOWN = ("hosts/chatgpt/fragments/hooks-setup.md",
                "hosts/kiro/files/skills/bootcamp-hooks-setup/SKILL.md")
    OUTSIDE = {"hosts/kiro/host.json": '{"note": "%s"}\n',
               "tools/bootcamp_build/emit.py": 'NOTE = (\n    "%s "\n)\n'}

    def setUp(self):
        self.mod = producer()
        self.repo = Path(self.enterContext(tempfile.TemporaryDirectory()))
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        # `--repo` is refused without a `source/` directory, so the fixture carries one.
        (self.repo / "source").mkdir()
        (self.repo / "source" / "seed.md").write_text("# seed\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "seed")
        self.base = git(self.repo, "rev-parse", "HEAD").stdout.strip()

    def add(self, relpath, text):
        path = self.repo / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "add %s" % relpath)

    def since(self):
        done = subprocess.run(
            [sys.executable, str(CONFORMANCE), "--repo", str(self.repo), "since", "--ref",
             self.base], cwd=str(self.repo), capture_output=True, text=True)
        self.assertEqual(0, done.returncode, done.stderr)
        return done.stdout

    def halves(self, report):
        """(the in-corpus block, the block from the `CORPUS:` line on)."""
        cut = report.index("CORPUS:")
        return report[:cut], report[cut:]

    def test_a_rule_in_host_markdown_is_reported_with_a_plus(self):
        for relpath in self.MARKDOWN:
            self.add(relpath, self.RULE + "\n")
        counted, outside = self.halves(self.since())
        for relpath in self.MARKDOWN:
            with self.subTest(file=relpath):
                self.assertIn("   %s\n     + %s" % (relpath, self.RULE), counted,
                              "a hard rule added to a Markdown file under `hosts/` is not "
                              "listed in the corpus block with `+`:\n%s" % counted)
                self.assertNotIn(relpath, outside,
                                 "the same rule is also listed outside the corpus, so it is "
                                 "counted twice:\n%s" % outside)
        self.assertIn("2 hard-rule line(s) added", counted)

    def test_a_rule_in_host_json_and_in_the_build_tool_is_reported_with_a_bang(self):
        for relpath, shape in self.OUTSIDE.items():
            self.add(relpath, shape % self.RULE)
        counted, outside = self.halves(self.since())
        self.assertIn("0 hard-rule line(s) added", counted,
                      "a non-Markdown file was counted inside the `.md`-only corpus:\n%s"
                      % counted)
        self.assertIn("NOT counted above: 2 line(s) in 2 file(s)", outside)
        for relpath in self.OUTSIDE:
            with self.subTest(file=relpath):
                self.assertRegex(
                    outside, r"(?m)^ +%s  \(1\)\n +! .*A host-side rule" % re.escape(relpath),
                    "a hard rule added to %s is not listed in the outside-the-corpus block "
                    "with `!`:\n%s" % (relpath, outside))
                self.assertNotIn(relpath, counted)

    def test_the_other_file_types_under_hosts_are_reported_with_a_bang_too(self):
        """`.html` and `.py`: the corpus is `.md` only under every scanned root."""
        self.add("hosts/kiro/fragments/site-tips.html", "<p>%s</p>\n" % self.RULE)
        self.add("hosts/_shared/hook_adapter.py", "#: %s\n" % self.RULE)
        counted, outside = self.halves(self.since())
        self.assertIn("0 hard-rule line(s) added", counted)
        self.assertIn("NOT counted above: 2 line(s) in 2 file(s)", outside)

    def test_both_consumers_place_the_two_populations(self):
        """The gate's parser reads the `+` lines and its outside reader the `!` lines."""
        self.add(self.MARKDOWN[0], self.RULE + "\n")
        self.add("hosts/kiro/host.json", self.OUTSIDE["hosts/kiro/host.json"] % self.RULE)
        report = self.since()
        helpers = consumer_helpers()
        parsed = helpers.parse_since(report)
        self.assertEqual([], parsed.unknown_headings,
                         "the gate does not recognize a heading under `hosts/` as a scanned "
                         "root, so the rule under it is checked by nothing")
        self.assertEqual([self.MARKDOWN[0]], [heading for heading, _line in parsed.checked])
        self.assertEqual(1, helpers.outside_count(report))
        # (#49) Each `!` line comes back with the file heading `since` printed above it.
        outside = helpers.outside_lines(report)
        self.assertEqual(["hosts/kiro/host.json"], [heading for heading, _line in outside])
        self.assertIn("A host-side rule", outside[0][1])

    def test_a_range_that_adds_nothing_still_names_the_new_roots(self):
        """A zero: the roots are stated as read on a run that found nothing in them."""
        report = self.since()
        self.assertIn("0 hard-rule line(s) added", report)
        corpus = next(line for line in report.splitlines() if "CORPUS:" in line)
        self.assertIn("hosts", corpus, "the corpus line of an empty run omits `hosts`")
        zero = next(line for line in report.splitlines() if "OUTSIDE the corpus: 0" in line)
        for home in self.mod.UNCOUNTED_RULE_HOMES:
            with self.subTest(home=home):
                self.assertIn(home, zero, "the zero line does not name the rule home %r" % home)
        self.assertIn("tools/bootcamp_build/", self.mod.UNCOUNTED_RULE_HOMES)


class TheConsumerReadsTheOutsideCount(unittest.TestCase):
    def test_it_parses_the_producer_s_line(self):
        helpers = consumer_helpers()
        report = ("   0 hard-rule line(s) added since main, across 0 file(s)\n"
                  "   ⛔ OUTSIDE the corpus, and therefore NOT counted above: 7 line(s) in 2 "
                  "file(s).\n")
        self.assertEqual(7, helpers.outside_count(report))

    def test_a_report_with_no_such_line_reads_as_zero(self):
        self.assertEqual(0, consumer_helpers().outside_count("   0 hard-rule line(s) added\n"))

    def test_the_pattern_is_not_satisfied_by_the_word_alone(self):
        """⚠️ 'OUTSIDE the corpus: 0' must not parse as a count."""
        self.assertEqual(0, consumer_helpers().outside_count("   OUTSIDE the corpus: 0 — none\n"))

    def test_an_empty_range_needs_BOTH_counts_to_be_zero(self):
        """⛔ The decision the consumer makes, exercised directly.

        Its own branch runs only when the live range happens to be empty, so the assertion
        there can sit unexercised for months. This tests the function it calls, against both
        answers, on every run.
        """
        empty = consumer_helpers().is_an_empty_range
        self.assertTrue(empty(0, 0), "nothing reported and nothing outside IS an empty range")
        self.assertFalse(
            empty(0, 5),
            "a range that added 5 rules where the corpus does not look was called empty -- "
            "that is the #108 defect: green by not running")
        self.assertFalse(empty(3, 0), "rules were reported; the range is not empty")


if __name__ == "__main__":
    unittest.main()
