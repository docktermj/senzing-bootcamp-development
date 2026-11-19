"""The cited-or-deferred gate checks every reported line, `+` or `!`, at its source line.

Enforces **INV-455** (registered 2026-11-19); it cannot establish that a cited invariant governs
the rule beside it.

`conformance.py since` reports a hard rule inside the Markdown corpus with `+`, and one outside
it with `!`: in `docs/`, in `tools/bootcamp_build/`, or in a non-`.md` file under a scanned
root. `tests/test_new_hard_rules_are_cited_or_deferred.py` is the gate that reads the report.
Until #49 it had three defects, and the live range showed none of them:

- a `!` line was tested against `since`'s 110-character display text, because the reader
  dropped the file heading and so could not find the source line. A citation past the cut was
  invisible, as it is for the location note in `hosts/kiro/host.json`;
- the source-line lookup compared the raw line with text `since` had stripped, so an indented
  line never matched, in either population;
- `!` lines were checked only in a range holding no `+` line, so an uncited rule in
  `host.json` passed whenever the range also added a Markdown rule.

This module is the fixtures (INV-282): what the gate must decide whatever the live range
holds. The gate's own parser, lookup, predicate and test method are imported and run; none is
copied here. Each fixture is a throwaway tree the gate is pointed at, with a ledger of its own,
and a `since` report over it. `TheSyntheticReportIsTheProducersShape` runs `conformance.py`
itself over one such tree, so the hand-built reports are held to the shape the view prints.

- **Not flagged:** a rule on an indented source line whose only citation is past column
  110, as a `!` line and as a `+` line; a `!` rule quoted in a `DEFERRED INVARIANT` block; the
  hard-rule lines of the real `hosts/kiro/host.json`.
- **Flagged:** an uncited `!` rule, in a range holding only `!` lines, in one that also
  holds `+` lines, and in one whose ref was widened; an uncited rule that a longer, cited line
  starts with.
- **Tested as displayed:** a line whose file is missing, whose file holds no matching line,
  whose report carries no heading, or whose text opens more than one distinct line. A cited
  rule can be flagged that way. An uncited rule never passes.

**What this cannot establish.** That a cited invariant governs the rule beside it: the gate's
own caveat stands. That the live range is clean: the gate decides that on each run. That
`since` reports every rule a range adds: `tests/test_since_states_its_corpus.py` holds that.

Line-scoped by design (#49): the gate's contract is a citation on the rule's own line
(INV-183), and `since` reports source lines, so each line read here is one source line or one
line of the report.

Stdlib only; the gate and the producer are imported by path (INV-108).

Source issue: #49 (the cited-or-deferred gate checks outside-the-corpus lines against
truncated text).

Run:  python3 -m unittest discover -s tests
"""
import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFORMANCE = REPO_ROOT / ".claude" / "skills" / "production-readiness-audit" / "conformance.py"
GATE_PATH = REPO_ROOT / "tests" / "test_new_hard_rules_are_cited_or_deferred.py"
GATE_TEST = "test_each_rule_added_since_the_last_audit_is_cited_or_deferred"

#: Where `since` cuts the text it displays.
CUT = 110


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GATE = _load(GATE_PATH, "gate_for_issue_49")
PRODUCER = _load(CONFORMANCE, "conformance_for_issue_49")
unaccounted = GATE.EveryNewHardRuleIsAccountedFor._unaccounted

#: Words enough to push whatever follows them past the cut.
FILLER = ("The sentence goes on for long enough that anything written after it sits well past "
          "the column where the display is cut.")

#: The rules. Each `LATE` one carries its only citation after the filler.
CITED_LATE = "⛔ **Never read a fixture file outside the fixture tree.** %s (INV-252)" % FILLER
UNCITED_LONG = "⛔ **Never write a fixture file outside the fixture tree.** %s No id." % FILLER
UNCITED = "⛔ **Never delete a fixture file the test did not write.**"
CITED_EARLY = "⛔ **(INV-252) Never rename a fixture file while a test reads it.**"
DEFERRED = "⛔ **Never keep a fixture tree after the test that built it ends.**"
MARKDOWN_CITED = "⛔ **(INV-183) Name the governing rule at the step that writes the file.**"

#: One file per place `since` reports with `!`, each holding its rule on an INDENTED line.
#: `%s` is the rule. The Markdown one is a nested list item, so the text `since` reports
#: starts with `- `.
OUTSIDE_HOMES = {
    "hosts/kiro/host.json": '{\n    "note": "%s"\n}\n',
    "hosts/_shared/fixture_49.py": 'def note():\n    #: %s\n    return None\n',
    "tools/bootcamp_build/fixture_49.py": 'NOTE = (\n    "%s "\n)\n',
    "docs/fixture-49.md": "- A list item.\n  - %s\n",
}
IN_CORPUS = "source/skills/fixture-49/SKILL.md"
INDENTED_MARKDOWN = "1. A numbered step.\n\n   - %s\n"

LEDGER = """# Implementation ledger

## fixture-49

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** The rule already
  shipping:
    - %s — in `docs/fixture-49.md` — **cite INV-NNN**

  **INV-NNN** — A fixture rule, drafted so the block carries wording.
""" % DEFERRED


def rule_line(shape, rule):
    """The one line of `shape % rule` that holds the rule, as it sits in the file."""
    lines = [line for line in (shape % rule).split("\n") if rule in line]
    assert len(lines) == 1, lines
    return lines[0]


def printed(source_line):
    """What `since` prints for a source line: stripped, then cut."""
    return source_line.strip()[:CUT]


def displayed(source_line):
    """The display text as the gate reads it off the report: a cut that ends on a space loses it."""
    return printed(source_line).strip()


def report(plus=(), bang=(), suspect=False):
    """A `since` report shaped as `cmd_since` prints it.

    `plus` and `bang` are `(heading, [source line, …])` pairs; a `bang` heading of None prints
    its lines with no file heading above them.
    """
    out = []
    if suspect:
        out.append("   ⛔ SUSPECT-REF: deadbee is an audit record committed WITH shipped work")
    out += ["== hard-rule lines added since deadbee (shipped markdown + the .claude/ "
            "maintainer surface)", ""]
    for heading, lines in plus:
        out.append("   %s" % heading)
        out += ["     + %s" % printed(line) for line in lines]
    out += ["",
            "   %d hard-rule line(s) added since deadbee, across %d file(s)"
            % (sum(len(lines) for _heading, lines in plus), len(plus)),
            "   ^ read every one. This is the set a run is answerable for; the corpus-wide",
            "",
            "   CORPUS: %s — and `.md` only." % ", ".join(GATE.SCAN_ROOTS)]
    if bang:
        out.append("   ⛔ OUTSIDE the corpus, and therefore NOT counted above: %d line(s) in %d "
                   "file(s)." % (sum(len(lines) for _heading, lines in bang), len(bang)))
        for heading, lines in bang:
            if heading is not None:
                out.append("      %s  (%d)" % (heading, len(lines)))
            out += ["        ! %s" % printed(line) for line in lines]
        out += ["      These shipped a hard rule where this corpus does not look. A zero above",
                "      is 'nothing to check HERE', never 'nothing was added'."]
    else:
        out.append("   OUTSIDE the corpus: 0 — no rule shipped in docs/, tools/bootcamp_build/ "
                   "or in a non-`.md` file under the roots.")
    out.append("   ⚠ Line-level: a rule MOVED between files shows as added here. That is the")
    return "\n".join(out) + "\n"


class FixtureTree(unittest.TestCase):
    """A throwaway tree the gate reads in place of the repository, with its own ledger."""

    def setUp(self):
        self.tree = Path(self.enterContext(tempfile.TemporaryDirectory()))
        ledger = self.tree / "specs" / "IMPLEMENTED.md"
        ledger.parent.mkdir()
        ledger.write_text(LEDGER, encoding="utf-8")
        self.enterContext(mock.patch.object(GATE, "REPO_ROOT", self.tree))
        self.enterContext(mock.patch.object(GATE, "IMPLEMENTED", ledger))

    def write(self, relpath, text):
        path = self.tree / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def place(self, relpath, shape, rule):
        """Write `shape % rule` at `relpath`; return the source line that holds the rule."""
        self.write(relpath, shape % rule)
        return rule_line(shape, rule)

    def outside(self, since):
        return [line for _heading, line in GATE.outside_lines(since)]

    def run_gate(self, since):
        """Run the gate's own test method over `since`; return (result, the stderr notice)."""
        case = GATE.EveryNewHardRuleIsAccountedFor(GATE_TEST)
        result = unittest.TestResult()
        with mock.patch.object(GATE, "conformance", lambda *args: since), \
                contextlib.redirect_stderr(io.StringIO()) as notice:
            case.run(result)
        self.assertEqual([], result.errors, "the gate's test raised instead of deciding")
        return result, notice.getvalue()


class TheFixturesAreWhatTheyClaim(unittest.TestCase):
    """INV-265 — a citation that is not late, or a rule `since` skips, proves nothing."""

    def test_the_late_citation_is_past_the_cut_in_every_home(self):
        for relpath, shape in list(OUTSIDE_HOMES.items()) + [(IN_CORPUS, INDENTED_MARKDOWN)]:
            with self.subTest(file=relpath):
                line = rule_line(shape, CITED_LATE)
                self.assertNotEqual(line, line.lstrip(), "the fixture line is not indented")
                self.assertNotIn("INV-", displayed(line),
                                 "the citation is inside the displayed text, so reading the "
                                 "display would clear this rule too")
                self.assertIn("INV-252", line)

    def test_every_fixture_rule_is_one_the_producer_reports(self):
        rules = (CITED_LATE, UNCITED_LONG, UNCITED, CITED_EARLY, DEFERRED, MARKDOWN_CITED)
        for relpath, shape in list(OUTSIDE_HOMES.items()) + [(IN_CORPUS, INDENTED_MARKDOWN)]:
            for rule in rules:
                with self.subTest(file=relpath, rule=rule[:40]):
                    self.assertIsNotNone(PRODUCER.classify(rule_line(shape, rule)))

    def test_every_outside_home_is_one_the_producer_reports_with_a_bang(self):
        for relpath in OUTSIDE_HOMES:
            with self.subTest(file=relpath):
                under_a_root = relpath.startswith(tuple(PRODUCER.SCAN_ROOTS))
                self.assertTrue(
                    relpath.startswith(tuple(PRODUCER.UNCOUNTED_RULE_HOMES))
                    or (under_a_root and not relpath.endswith(".md")),
                    "%s is not a place `since` reports outside the corpus" % relpath)
        self.assertTrue(IN_CORPUS.startswith(tuple(PRODUCER.SCAN_ROOTS)))


class TheSyntheticReportIsTheProducersShape(FixtureTree):
    """`conformance.py since` itself, run over a fixture tree that is a git repository."""

    def git(self, *args):
        done = subprocess.run(["git", *args], cwd=str(self.tree), capture_output=True, text=True)
        self.assertEqual(0, done.returncode, done.stderr)
        return done.stdout.strip()

    def setUp(self):
        super().setUp()
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        # `--repo` is refused without a `source/` directory, so the seed commit carries one.
        self.write("source/seed.md", "# seed\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "seed")
        self.base = self.git("rev-parse", "HEAD")
        self.markdown = self.place(IN_CORPUS, INDENTED_MARKDOWN, CITED_LATE)
        self.late = {relpath: self.place(relpath, shape, CITED_LATE)
                     for relpath, shape in OUTSIDE_HOMES.items()}
        self.git("add", "-A")
        self.git("commit", "-qm", "the rules")

    def since(self):
        done = subprocess.run(
            [sys.executable, str(CONFORMANCE), "--repo", str(self.tree), "since", "--ref",
             self.base], cwd=str(self.tree), capture_output=True, text=True)
        self.assertEqual(0, done.returncode, done.stderr)
        return done.stdout

    def test_the_view_cuts_each_line_before_its_citation(self):
        """The premise: the report alone cannot show these rules are cited."""
        real = self.since()
        self.assertIn("NOT counted above: %d line(s) in %d file(s)"
                      % (len(self.late), len(self.late)), real)
        for line in real.splitlines():
            if line.strip().startswith(("+ ", "! ")):
                self.assertNotIn("INV-", line)

    def test_each_outside_line_keeps_its_heading_and_resolves_to_its_source_line(self):
        got = GATE.outside_lines(self.since())
        self.assertEqual(sorted(self.late), sorted(heading for heading, _line in got))
        for heading, line in got:
            with self.subTest(file=heading):
                self.assertEqual(self.late[heading].strip(), line)

    def test_the_indented_markdown_rule_resolves_to_its_source_line(self):
        parsed = GATE.parse_since(self.since())
        self.assertEqual([(IN_CORPUS, self.markdown.strip())], parsed.checked)

    def test_the_gate_reads_the_hand_built_report_exactly_as_it_reads_the_real_one(self):
        real = self.since()
        built = report(plus=[(IN_CORPUS, [self.markdown])],
                       bang=[(relpath, [line]) for relpath, line in self.late.items()])
        self.assertEqual(GATE.parse_since(real), GATE.parse_since(built))
        self.assertEqual(sorted(GATE.outside_lines(real)), sorted(GATE.outside_lines(built)))
        self.assertEqual(GATE.outside_count(real), GATE.outside_count(built))

    def test_the_gate_passes_on_the_real_report(self):
        """A mixed range, every line cited past the cut: no failure and no skip."""
        result, notice = self.run_gate(self.since())
        self.assertEqual(([], []), (result.failures, result.skipped))
        self.assertIn("1 checked", notice)
        self.assertIn("%d outside the corpus, checked the same way" % len(self.late), notice)


class TheLookupNamesOneSourceLine(FixtureTree):
    """`_full_source_line`, the one lookup the `+` and the `!` lines share."""

    def lookup(self, relpath, source_line):
        return GATE._full_source_line(relpath, displayed(source_line))

    def test_an_indented_line_is_found_in_every_home(self):
        for relpath, shape in list(OUTSIDE_HOMES.items()) + [(IN_CORPUS, INDENTED_MARKDOWN)]:
            with self.subTest(file=relpath):
                line = self.place(relpath, shape, CITED_LATE)
                self.assertEqual(line.strip(), self.lookup(relpath, line))

    def test_a_line_that_is_not_indented_is_still_found(self):
        self.write(IN_CORPUS, "# A heading\n\n%s\n" % CITED_LATE)
        self.assertEqual(CITED_LATE, self.lookup(IN_CORPUS, CITED_LATE))

    def test_a_missing_file_gives_the_display_text(self):
        self.assertEqual(displayed(CITED_LATE), self.lookup("hosts/kiro/gone.json", CITED_LATE))

    def test_a_directory_gives_the_display_text(self):
        (self.tree / "hosts" / "kiro").mkdir(parents=True)
        self.assertEqual(displayed(CITED_LATE), self.lookup("hosts/kiro", CITED_LATE))

    def test_a_file_that_is_not_text_gives_the_display_text(self):
        path = self.tree / "hosts" / "kiro" / "blob.bin"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"\xff\xfe\x00 not utf-8 \xff\n")
        self.assertEqual(displayed(CITED_LATE), self.lookup("hosts/kiro/blob.bin", CITED_LATE))

    def test_no_heading_gives_the_display_text(self):
        self.assertEqual(displayed(CITED_LATE), self.lookup(None, CITED_LATE))

    def test_a_file_with_no_matching_line_gives_the_display_text(self):
        relpath, shape = "hosts/kiro/host.json", OUTSIDE_HOMES["hosts/kiro/host.json"]
        self.place(relpath, shape, CITED_EARLY)
        self.assertEqual(displayed(rule_line(shape, CITED_LATE)),
                         self.lookup(relpath, rule_line(shape, CITED_LATE)))

    def test_two_distinct_matching_lines_give_the_display_text(self):
        """The display is the same for both, so neither can be named."""
        self.write(IN_CORPUS, "  - %s\n  - %s Unless a later rule says so.\n"
                   % (CITED_LATE, CITED_LATE))
        self.assertEqual(displayed("- " + CITED_LATE), self.lookup(IN_CORPUS, "- " + CITED_LATE))

    def test_the_same_line_twice_is_one_line(self):
        """Not distinct: the two copies differ only in indentation, and decide the same way."""
        self.write(IN_CORPUS, "- %s\n\nMore.\n\n  - %s\n" % (CITED_LATE, CITED_LATE))
        self.assertEqual("- " + CITED_LATE, self.lookup(IN_CORPUS, "- " + CITED_LATE))


class ACitedOutsideRuleIsNotFlagged(FixtureTree):
    def test_an_indented_rule_cited_past_the_cut_is_not_flagged_in_any_home(self):
        for relpath, shape in OUTSIDE_HOMES.items():
            with self.subTest(file=relpath):
                line = self.place(relpath, shape, CITED_LATE)
                since = report(bang=[(relpath, [line])])
                self.assertEqual([line.strip()], self.outside(since),
                                 "the `!` line was not resolved to its source line")
                self.assertEqual([], unaccounted(self.outside(since)))

    def test_a_range_holding_only_that_line_does_not_fail_the_gate(self):
        """It ends as it did before #49: a skip that says what was and was not established."""
        relpath = "hosts/kiro/host.json"
        line = self.place(relpath, OUTSIDE_HOMES[relpath], CITED_LATE)
        result, notice = self.run_gate(report(bang=[(relpath, [line])]))
        self.assertEqual([], result.failures)
        self.assertEqual(1, len(result.skipped))
        self.assertIn("Accounted for, NOT verified", result.skipped[0][1])
        self.assertIn("0 checked", notice)
        self.assertIn("1 outside the corpus, checked the same way", notice)

    def test_a_rule_cited_inside_the_display_is_not_flagged_either(self):
        relpath = "tools/bootcamp_build/fixture_49.py"
        line = self.place(relpath, OUTSIDE_HOMES[relpath], CITED_EARLY)
        self.assertEqual([], unaccounted(self.outside(report(bang=[(relpath, [line])]))))

    def test_a_rule_quoted_in_a_deferral_is_not_flagged(self):
        relpath = "docs/fixture-49.md"
        line = self.place(relpath, OUTSIDE_HOMES[relpath], DEFERRED)
        self.assertEqual([], unaccounted(self.outside(report(bang=[(relpath, [line])]))))

    def test_the_deferral_clears_only_the_rule_it_quotes(self):
        relpath, shape = "docs/fixture-49.md", "- A list item.\n  - %s\n  - %s\n"
        self.write(relpath, shape % (DEFERRED, UNCITED))
        lines = ["  - " + DEFERRED, "  - " + UNCITED]
        self.assertEqual(["- " + UNCITED],
                         unaccounted(self.outside(report(bang=[(relpath, lines)]))))


class AnUncitedOutsideRuleFailsTheGate(FixtureTree):
    def setUp(self):
        super().setUp()
        self.markdown = self.place(IN_CORPUS, INDENTED_MARKDOWN, MARKDOWN_CITED)

    def failure(self, since):
        result, _notice = self.run_gate(since)
        self.assertEqual(1, len(result.failures),
                         "the gate did not fail (skipped: %s)" % result.skipped)
        return result.failures[0][1]

    def test_in_a_range_holding_only_outside_lines(self):
        for relpath, shape in OUTSIDE_HOMES.items():
            for rule in (UNCITED, UNCITED_LONG):
                with self.subTest(file=relpath, rule=rule[:40]):
                    line = self.place(relpath, shape, rule)
                    message = self.failure(report(bang=[(relpath, [line])]))
                    self.assertIn(displayed(line), message, "the message does not name the line")
                    self.assertIn("where the checked corpus does not look", message)

    def test_in_a_range_that_also_holds_an_accounted_for_markdown_rule(self):
        """Until #49 the `+` line switched the outside check off."""
        for relpath, shape in OUTSIDE_HOMES.items():
            with self.subTest(file=relpath):
                line = self.place(relpath, shape, UNCITED)
                message = self.failure(report(plus=[(IN_CORPUS, [self.markdown])],
                                              bang=[(relpath, [line])]))
                self.assertIn(displayed(line), message)
                self.assertNotIn(MARKDOWN_CITED, message,
                                 "the accounted-for Markdown rule was named as a failure")

    def test_in_a_range_whose_ref_was_widened(self):
        """`SUSPECT-REF` changes the skip message for an empty range, never the check."""
        relpath = "hosts/kiro/host.json"
        line = self.place(relpath, OUTSIDE_HOMES[relpath], UNCITED)
        self.assertIn(displayed(line), self.failure(report(bang=[(relpath, [line])], suspect=True)))

    def test_beside_a_cited_rule_in_the_same_file(self):
        relpath = "hosts/kiro/host.json"
        self.write(relpath, '{\n    "one": "%s",\n    "two": "%s"\n}\n' % (CITED_LATE, UNCITED))
        lines = ['    "one": "%s",' % CITED_LATE, '    "two": "%s"' % UNCITED]
        message = self.failure(report(bang=[(relpath, lines)]))
        self.assertIn(displayed(lines[1]), message)
        self.assertNotIn(displayed(lines[0]), message)

    def test_one_failure_names_the_unaccounted_lines_of_both_populations(self):
        relpath = "hosts/kiro/host.json"
        outside = self.place(relpath, OUTSIDE_HOMES[relpath], UNCITED)
        inside = self.place(IN_CORPUS, INDENTED_MARKDOWN, UNCITED_LONG)
        message = self.failure(report(plus=[(IN_CORPUS, [inside])], bang=[(relpath, [outside])]))
        self.assertIn(displayed(outside), message)
        self.assertIn(displayed(inside), message)
        self.assertIn("a hard rule added since the last audit cites no invariant", message)
        self.assertIn("where the checked corpus does not look", message)


class AMixedRangeThatIsAccountedForPasses(FixtureTree):
    def setUp(self):
        super().setUp()
        self.markdown = self.place(IN_CORPUS, INDENTED_MARKDOWN, MARKDOWN_CITED)

    def test_plus_lines_and_a_cited_outside_line_pass(self):
        for relpath, shape in OUTSIDE_HOMES.items():
            with self.subTest(file=relpath):
                line = self.place(relpath, shape, CITED_LATE)
                result, notice = self.run_gate(report(plus=[(IN_CORPUS, [self.markdown])],
                                                      bang=[(relpath, [line])]))
                self.assertEqual(([], []), (result.failures, result.skipped))
                self.assertTrue(result.wasSuccessful())
                self.assertIn("[new-hard-rules] 1 line(s) reported since the last audit: 1 "
                              "checked", notice)
                self.assertIn("0 unresolved; 1 outside the corpus, checked the same way",
                              notice, "the breakdown does not count the outside line (INV-308)")

    def test_plus_lines_and_a_deferred_outside_line_pass(self):
        relpath = "docs/fixture-49.md"
        line = self.place(relpath, OUTSIDE_HOMES[relpath], DEFERRED)
        result, _notice = self.run_gate(report(plus=[(IN_CORPUS, [self.markdown])],
                                               bang=[(relpath, [line])]))
        self.assertEqual(([], []), (result.failures, result.skipped))

    def test_a_range_with_no_outside_line_says_zero(self):
        result, notice = self.run_gate(report(plus=[(IN_CORPUS, [self.markdown])]))
        self.assertEqual(([], []), (result.failures, result.skipped))
        self.assertIn("0 outside the corpus, checked the same way", notice)


class AnIndentedMarkdownRuleIsReadWhole(FixtureTree):
    """The `+` path: the same lookup, so the same repair and the same fallback."""

    def checked(self, since):
        parsed = GATE.parse_since(since)
        self.assertEqual(([], []), (parsed.unresolved, parsed.unknown_headings))
        return [line for _heading, line in parsed.checked]

    def test_a_rule_cited_past_the_cut_is_not_flagged(self):
        line = self.place(IN_CORPUS, INDENTED_MARKDOWN, CITED_LATE)
        since = report(plus=[(IN_CORPUS, [line])])
        self.assertEqual([line.strip()], self.checked(since))
        self.assertEqual([], unaccounted(self.checked(since)))
        result, _notice = self.run_gate(since)
        self.assertEqual(([], []), (result.failures, result.skipped))

    def test_an_uncited_indented_rule_is_still_flagged(self):
        line = self.place(IN_CORPUS, INDENTED_MARKDOWN, UNCITED_LONG)
        self.assertEqual([displayed(line)],
                         unaccounted(self.checked(report(plus=[(IN_CORPUS, [line])]))))

    def test_an_uncited_rule_is_not_cleared_by_a_longer_cited_line_that_starts_with_it(self):
        """Until #49 the first match was taken, and here the first match is the cited line."""
        self.write(IN_CORPUS, "- %s Unless a registered rule says so (INV-252).\n- %s\n"
                   % (UNCITED, UNCITED))
        since = report(plus=[(IN_CORPUS, ["- " + UNCITED])])
        self.assertEqual(["- " + UNCITED], self.checked(since),
                         "the lookup named a line although two distinct lines match")
        self.assertEqual(["- " + UNCITED], unaccounted(self.checked(since)))
        result, _notice = self.run_gate(since)
        self.assertEqual(1, len(result.failures))


class ALineThatCannotBeResolvedIsTestedAsDisplayed(FixtureTree):
    """A cited rule can be flagged this way. An uncited rule never passes."""

    RELPATH = "hosts/kiro/host.json"
    SHAPE = OUTSIDE_HOMES["hosts/kiro/host.json"]

    def cases(self, rule):
        """{why it cannot be resolved: a report holding `rule` as one unresolvable `!` line}."""
        line = rule_line(self.SHAPE, rule)
        longer = '    "note": "%s Unless a later rule says so."' % rule
        cases = {}
        cases["the file is missing"] = report(bang=[("hosts/kiro/gone.json", [line])])
        self.write("hosts/kiro/other.json", self.SHAPE % MARKDOWN_CITED)
        cases["no line in the file matches"] = report(bang=[("hosts/kiro/other.json", [line])])
        cases["the report carries no heading"] = report(bang=[(None, [line])])
        self.write("hosts/kiro/twice.json", "{\n%s\n%s,\n}\n" % (line, longer))
        cases["two distinct lines match"] = report(bang=[("hosts/kiro/twice.json", [line])])
        return line, cases

    def test_an_uncited_rule_is_flagged(self):
        for rule in (UNCITED, UNCITED_LONG):
            line, cases = self.cases(rule)
            for why, since in cases.items():
                with self.subTest(why=why, rule=rule[:40]):
                    self.assertEqual([displayed(line)], self.outside(since))
                    self.assertEqual([displayed(line)], unaccounted(self.outside(since)))
                    result, _notice = self.run_gate(since)
                    self.assertEqual(1, len(result.failures))
                    self.assertIn(displayed(line), result.failures[0][1])

    def test_a_rule_cited_past_the_cut_is_flagged_too(self):
        """The stated cost of the fallback: the display text holds no citation to find."""
        line, cases = self.cases(CITED_LATE)
        for why, since in cases.items():
            with self.subTest(why=why):
                self.assertEqual([displayed(line)], unaccounted(self.outside(since)))

    def test_a_rule_cited_inside_the_display_is_not_flagged(self):
        """The display text is still tested, not failed outright."""
        _line, cases = self.cases(CITED_EARLY)
        for why, since in cases.items():
            with self.subTest(why=why):
                self.assertEqual([], unaccounted(self.outside(since)))

    def test_a_rule_quoted_in_a_deferral_is_not_flagged(self):
        line = "  - " + DEFERRED
        since = report(bang=[("docs/gone-49.md", [line])])
        self.assertEqual([displayed(line)], self.outside(since))
        self.assertEqual([], unaccounted(self.outside(since)))


class EachOutsideLineKeepsItsHeading(FixtureTree):
    def test_lines_under_several_files_each_get_their_own(self):
        placed = {relpath: self.place(relpath, shape, CITED_LATE)
                  for relpath, shape in OUTSIDE_HOMES.items()}
        got = GATE.outside_lines(report(bang=[(r, [line]) for r, line in placed.items()]))
        self.assertEqual([(relpath, line.strip()) for relpath, line in placed.items()], got)

    def test_two_lines_under_one_file_share_its_heading(self):
        relpath = "hosts/kiro/host.json"
        self.write(relpath, '{\n    "one": "%s",\n    "two": "%s"\n}\n' % (CITED_LATE, UNCITED))
        lines = ['    "one": "%s",' % CITED_LATE, '    "two": "%s"' % UNCITED]
        self.assertEqual([(relpath, line.strip()) for line in lines],
                         GATE.outside_lines(report(bang=[(relpath, lines)])))

    def test_a_path_holding_a_space_is_kept_whole(self):
        relpath = "docs/fixture 49 notes.md"
        line = self.place(relpath, OUTSIDE_HOMES["docs/fixture-49.md"], CITED_LATE)
        self.assertEqual([(relpath, line.strip())],
                         GATE.outside_lines(report(bang=[(relpath, [line])])))

    def test_a_line_with_no_heading_above_it_has_none(self):
        self.assertEqual([(None, UNCITED)], GATE.outside_lines(report(bang=[(None, [UNCITED])])))

    def test_a_plus_line_is_never_read_as_an_outside_line(self):
        line = self.place(IN_CORPUS, INDENTED_MARKDOWN, CITED_LATE)
        self.assertEqual([], GATE.outside_lines(report(plus=[(IN_CORPUS, [line])])))


class ARangeWithNothingInItStillSkips(FixtureTree):
    """Out of scope for #49 and unchanged by it: how the gate ends when it has nothing to fail."""

    def skip_message(self, since):
        result, _notice = self.run_gate(since)
        self.assertEqual([], result.failures)
        self.assertEqual(1, len(result.skipped), "the gate did not skip")
        return result.skipped[0][1]

    def test_an_empty_range_skips_as_an_empty_range(self):
        self.assertIn("this is an empty range", self.skip_message(report()))

    def test_an_empty_widened_range_says_it_was_widened(self):
        self.assertIn("widened past it", self.skip_message(report(suspect=True)))

    def test_a_widened_range_of_accounted_for_outside_lines_says_so_too(self):
        relpath = "hosts/kiro/host.json"
        line = self.place(relpath, OUTSIDE_HOMES[relpath], CITED_LATE)
        self.assertIn("widened past it",
                      self.skip_message(report(bang=[(relpath, [line])], suspect=True)))


class TheRealHostJsonLinesAreNotFlagged(unittest.TestCase):
    """The file the issue names, read where it lies: `hosts/kiro/host.json` in this repository.

    Every hard-rule line in it today cites an invariant somewhere on the line. A range holding
    only those lines must come out with none unaccounted for, whatever column the citation is
    in. The ledger is replaced by one holding no deferral, so only a citation can clear a line.
    """

    RELPATH = "hosts/kiro/host.json"

    def setUp(self):
        text = (REPO_ROOT / self.RELPATH).read_text(encoding="utf-8")
        self.rules = [line for line in text.split("\n") if PRODUCER.classify(line) is not None]
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        ledger = tmp / "IMPLEMENTED.md"
        ledger.write_text("# Implementation ledger\n\n## an-entry-with-no-deferral\n",
                          encoding="utf-8")
        self.enterContext(mock.patch.object(GATE, "IMPLEMENTED", ledger))

    def late(self):
        """The lines whose citations all sit past the cut: the case #49 was filed for."""
        return [line for line in self.rules
                if "INV-" in line and "INV-" not in displayed(line)]

    def test_a_range_holding_only_its_hard_rule_lines_reports_none_unaccounted(self):
        if not self.late():
            self.skipTest(
                "no hard-rule line in %s is cited only past column %d today, so the live file "
                "no longer shows the #49 case; the fixture classes above carry it"
                % (self.RELPATH, CUT))
        since = report(bang=[(self.RELPATH, self.rules)])
        got = GATE.outside_lines(since)
        self.assertEqual(len(self.rules), len(got))
        for line in self.late():
            with self.subTest(line=displayed(line)[:50]):
                self.assertIn((self.RELPATH, line.strip()), got,
                              "the line was not resolved to its source line. If two distinct "
                              "lines in the file now open with the same %d characters, the "
                              "gate tests both as displayed, as designed" % CUT)
        cited = [line for line in self.rules if "INV-" in line]
        self.assertEqual(
            [displayed(line) for line in self.rules if line not in cited],
            unaccounted(line for _heading, line in got),
            "a rule in %s that cites an invariant on its line was flagged" % self.RELPATH)

    def test_the_gate_s_own_test_does_not_fail_on_its_late_cited_lines(self):
        late = self.late()
        if not late:
            self.skipTest("no hard-rule line in %s is cited only past column %d today"
                          % (self.RELPATH, CUT))
        since = report(bang=[(self.RELPATH, late)])
        case = GATE.EveryNewHardRuleIsAccountedFor(GATE_TEST)
        result = unittest.TestResult()
        with mock.patch.object(GATE, "conformance", lambda *args: since), \
                contextlib.redirect_stderr(io.StringIO()):
            case.run(result)
        self.assertEqual(([], []), (result.failures, result.errors))
        self.assertEqual(1, len(result.skipped))
        self.assertIn("Accounted for, NOT verified", result.skipped[0][1])


if __name__ == "__main__":
    unittest.main()
