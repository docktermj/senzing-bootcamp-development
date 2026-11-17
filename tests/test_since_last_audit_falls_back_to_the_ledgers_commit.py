"""`--since-last-audit` measures from the ledger's fallback commit when no audit entry resolves.

`conformance.py since --since-last-audit` and `reverse-check --since-last-audit` take their
range start from the newest audit entry in `specs/IMPLEMENTED.md` whose `Commit:` names a commit
in the repository. After the move to one development repository, no entry did: the newest audit
entry carried over reads `committed (hash not recorded)` and its commit is not in this history.
Both views stopped with exit 2, so the audit could not ask what a run had added (#10).

What this module fixes in place:

- **The fallback.** When no audit entry yields a commit, both views measure from the commit the
  ledger states on a `- **Fallback commit:**` line in its opening section, exit 0, and print one
  `FALLBACK` line naming the commit and the entries that were skipped. That includes a ledger
  with no audit entry at all, and a run that reports zero lines added.
- **One copy of the hash.** `conformance.py` holds no fallback hash. Changing the ledger's line
  changes the range, and the hash the live ledger states appears nowhere in the script.
- **An ordinary run.** From the `== ` header on, a fallback run prints exactly what the same
  view prints for `--ref <the fallback commit>`, the reverse check's verdict included.
- **An entry that resolves always wins**, an older one behind a newer `uncommitted` one included.
- **The refusal.** With no fallback stated, one that is not a hash, one that is not a commit, one
  stated below the first entry, or no ledger at all, both views exit 2, say on stderr what they
  read, and print no count.

Built on a throwaway git repository, so every case is exercised whatever this repository's own
ledger holds. The live ledger is checked once, for the property: it states a fallback, and both
views name where their range start came from.

**What this cannot establish:** that the commit the live ledger states is the right one to
measure from. That is the maintainer's choice, recorded in #10.

No phrase-level pattern (#10): its line reads parse a script's stdout and a fixture ledger.

Stdlib only; the maintainer script is loaded by path, never imported as a package.

Source issue: #10 (the since-last-audit views cannot run in this repository).

Enforces **INV-432** (registered 2026-11-16). It builds throwaway repositories, so it cannot
establish that the commit the live ledger states is the right one to measure from.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFORMANCE = REPO_ROOT / ".claude" / "skills" / "production-readiness-audit" / "conformance.py"
GUARD_PATH = REPO_ROOT / "tests" / "test_new_hard_rules_are_cited_or_deferred.py"
LIVE_LEDGER = REPO_ROOT / "specs" / "IMPLEMENTED.md"

VIEWS = ("since", "reverse-check")

#: A hash-shaped value that is no commit in the fixture repository.
NOT_A_COMMIT = "deadbeef" * 5

#: The ledger's opening section. `%s` is the fallback line, or nothing.
OPENING = """# Implementation ledger

Record of changes that have landed, newest first.

%s
<!-- New entries go directly below this line. -->
"""

#: One audit entry. `%s` are its date and its `Commit:` value.
AUDIT = """
## production-readiness-audit-%s

- **Implemented:** %s (**0 findings; no file modified by this audit**)
- **Summary:** fixture.
- **Commit:** %s
"""

#: An entry that is not an audit record. Its commit is never a range start.
NOT_AN_AUDIT = """
## some-implemented-issue

- **Implemented:** 2026-01-05
- **Summary:** fixture.
- **Commit:** %s
"""

#: Three audit entries, none of which yields a commit, one per way of not yielding one.
UNRESOLVED = (("2026-01-09", "uncommitted"),
              ("2026-01-05", "committed (hash not recorded)"),
              ("2026-01-02", NOT_A_COMMIT))


def fallback_line(value):
    return "- **Fallback commit:** %s\n" % value


def ledger(fallback=None, audits=(), tail=""):
    """A fixture ledger: the opening, with or without a fallback line, then the entries."""
    opening = OPENING % (fallback_line(fallback) if fallback is not None else "")
    return opening + "".join(AUDIT % (date, date, commit) for date, commit in audits) + tail


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def git(repo, *args):
    done = subprocess.run(["git"] + list(args), cwd=str(repo), capture_output=True, text=True)
    if done.returncode != 0:
        raise AssertionError("git %s failed in fixture: %s" % (" ".join(args), done.stderr))
    return done.stdout.strip()


def run_view(repo, *argv):
    return subprocess.run([sys.executable, str(CONFORMANCE), "--repo", str(repo)] + list(argv),
                          capture_output=True, text=True, cwd=str(repo))


def from_the_header(stdout):
    """A view's report from its `== ` header on, without the resolver's lines above it."""
    lines = stdout.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("== ")]
    return "\n".join(lines[starts[0]:]) if starts else None


def fallback_lines(stdout):
    """The resolver's own `FALLBACK` lines. A rule line that mentions the word is not one."""
    return [line for line in stdout.splitlines() if re.match(r"\s*⚠ FALLBACK:", line)]


def prints_a_count(stdout):
    """Whether a view's stdout carries any figure a reader could take for a result."""
    return bool(re.search(r"hard-rule line\(s\) added|TESTED|UNTESTED|VERDICT|^== ", stdout,
                          re.M))


class FixtureRepository(unittest.TestCase):
    """Four commits. Three hard rules arrive after the root, one per commit.

    - `root`: the ledger and a plain shipped file. No rule.
    - `first`: a shipped rule that cites an invariant at its line.
    - `second`: a shipped rule that cites nothing.
    - `third`: a rule on the maintainer surface, which the reverse check cannot test.

    So a range from `root` holds 3 rules, from `first` 2, from `second` 1 and from `third` 0,
    and the reverse check's three buckets each hold one line somewhere in that sequence.
    """

    @classmethod
    def setUpClass(cls):
        if not shutil.which("git"):
            raise unittest.SkipTest("git is required to build the fixture repository")
        cls.tmp = tempfile.mkdtemp(prefix="since-fallback-")
        repo = Path(cls.tmp)
        cls.repo = repo
        git(repo, "init", "--quiet", "--initial-branch", "main")
        git(repo, "config", "user.email", "fixture@example.invalid")
        git(repo, "config", "user.name", "fixture")
        git(repo, "config", "commit.gpgsign", "false")

        (repo / "specs").mkdir()
        (repo / "specs" / "IMPLEMENTED.md").write_text(ledger(), encoding="utf-8")
        shipped = repo / "source" / "skills" / "demo"
        shipped.mkdir(parents=True)
        (shipped / "notes.md").write_text("Plain prose, no rule.\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "--quiet", "-m", "chore: the ledger and a plain file")
        cls.root = git(repo, "rev-parse", "--short", "HEAD")

        (shipped / "SKILL.md").write_text(
            "- ⛔ **(INV-308) Never report a count without what it could not check.**\n",
            encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "--quiet", "-m", "feat(demo): a cited rule")
        cls.first = git(repo, "rev-parse", "--short", "HEAD")

        with (shipped / "SKILL.md").open("a", encoding="utf-8") as handle:
            handle.write("\nA paragraph between the two rules, citing nothing.\n\n"
                         "- ⛔ **Always say which range a figure was measured over.**\n")
        git(repo, "add", "-A")
        git(repo, "commit", "--quiet", "-m", "feat(demo): an uncited rule")
        cls.second = git(repo, "rev-parse", "--short", "HEAD")

        surface = repo / ".claude" / "skills" / "demo"
        surface.mkdir(parents=True)
        (surface / "SKILL.md").write_text(
            "- ⛔ **A rule on the maintainer surface, counted and never tested.**\n",
            encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "--quiet", "-m", "feat(demo): a maintainer-surface rule")
        cls.third = git(repo, "rev-parse", "--short", "HEAD")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def write_ledger(self, text):
        (self.repo / "specs" / "IMPLEMENTED.md").write_text(text, encoding="utf-8")

    def view(self, name, text):
        """Run one view with `--since-last-audit` against a ledger holding `text`."""
        self.write_ledger(text)
        return run_view(self.repo, name, "--since-last-audit")

    def assert_measured_from(self, out, commit, view):
        self.assertEqual(0, out.returncode,
                         "%s refused where the ledger states a usable fallback:\n%s"
                         % (view, out.stderr))
        self.assertRegex(out.stdout, r"(?m)^== .*since %s\b" % commit,
                         "%s did not measure from %s:\n%s" % (view, commit, out.stdout))


class TheFixtureHoldsWhatTheTestsAssume(FixtureRepository):
    """A fixture with no rule in a range proves nothing about that range."""

    def test_each_range_holds_the_rules_the_tests_count(self):
        module = load(CONFORMANCE, "conformance_fallback_fixture")
        for commit, expected in ((self.root, 3), (self.first, 2), (self.second, 1),
                                 (self.third, 0)):
            with self.subTest(since=commit):
                added = module.added_rule_lines(self.repo, commit)
                self.assertIsNotNone(added, "the fixture range could not be diffed")
                self.assertEqual(expected, sum(len(rows) for rows in added.values()))

    def test_the_value_that_is_not_a_commit_really_is_not_one(self):
        done = subprocess.run(["git", "rev-parse", "--verify", "%s^{commit}" % NOT_A_COMMIT],
                              cwd=str(self.repo), capture_output=True, text=True)
        self.assertNotEqual(0, done.returncode)

    def test_a_view_with_an_explicit_ref_runs_in_the_fixture(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = run_view(self.repo, view, "--ref", self.first)
                self.assertEqual(0, out.returncode, out.stderr)
                self.assertIsNotNone(from_the_header(out.stdout),
                                     "%s printed no `== ` header" % view)


class NoAuditEntryYieldsACommit(FixtureRepository):
    """`uncommitted`, `committed (hash not recorded)` and a hash that is no commit here."""

    def test_both_views_measure_from_the_fallback(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.first, UNRESOLVED))
                self.assert_measured_from(out, self.first, view)

    def test_one_fallback_line_names_the_commit_and_every_skipped_entry(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.first, UNRESOLVED))
                lines = fallback_lines(out.stdout)
                self.assertEqual(1, len(lines),
                                 "%s must print exactly one FALLBACK line on stdout:\n%s"
                                 % (view, out.stdout))
                self.assertIn(self.first, lines[0],
                              "the FALLBACK line does not name the commit: %s" % lines[0])
                for date, commit in UNRESOLVED:
                    self.assertIn("production-readiness-audit-%s" % date, lines[0],
                                  "the FALLBACK line does not name a skipped entry: %s"
                                  % lines[0])
                    self.assertIn(commit, lines[0],
                                  "the FALLBACK line does not say why %s was skipped: %s"
                                  % (date, lines[0]))

    def test_a_fallback_run_names_no_ledger_entry_as_its_source(self):
        """The `(ref … from ledger entry …)` line belongs to an entry that resolved."""
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.first, UNRESOLVED))
                self.assertNotIn("from ledger entry", out.stdout)

    def test_the_fallback_is_measured_from_as_stated(self):
        """`second` carries shipped work. A fallback is not an audit record, so it is not widened."""
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.second, UNRESOLVED))
                self.assert_measured_from(out, self.second, view)
                self.assertNotIn("SUSPECT-REF", out.stdout)

    def test_the_boundary_is_still_reported_as_a_first_range(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.first, UNRESOLVED))
                self.assertIn("BOUNDARY", out.stdout)
                self.assertNotRegex(out.stdout, r"carrying \d+ hard-rule line\(s\)",
                                    "a fallback range has no earlier audit record to measure "
                                    "back to, so any retired count is invented")


class ALedgerWithNoAuditEntryAtAll(FixtureRepository):
    def test_both_views_measure_from_the_fallback(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.first))
                self.assert_measured_from(out, self.first, view)
                lines = fallback_lines(out.stdout)
                self.assertEqual(1, len(lines), out.stdout)
                self.assertIn(self.first, lines[0])
                self.assertIn("no audit entry", lines[0],
                              "with nothing skipped, the FALLBACK line must say so: %s"
                              % lines[0])

    def test_an_entry_that_is_not_an_audit_record_is_never_the_range_start(self):
        text = ledger(self.first, tail=NOT_AN_AUDIT % self.second)
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, text)
                self.assert_measured_from(out, self.first, view)
                self.assertEqual(1, len(fallback_lines(out.stdout)), out.stdout)


class TheLedgerHoldsTheOnlyCopyOfTheHash(FixtureRepository):
    def test_changing_the_ledgers_line_changes_the_commit_the_resolver_uses(self):
        module = load(CONFORMANCE, "conformance_fallback_resolver")
        import contextlib
        import io
        resolved = []
        for stated in (self.root, self.first, self.second, self.third):
            self.write_ledger(ledger(stated, UNRESOLVED))
            with contextlib.redirect_stdout(io.StringIO()):
                resolved.append(module.last_audit_ref(self.repo))
        self.assertEqual([self.root, self.first, self.second, self.third], resolved,
                         "the resolver did not follow the ledger's fallback line")

    def test_changing_the_ledgers_line_changes_what_each_view_counts(self):
        for stated, count in ((self.root, 3), (self.first, 2), (self.second, 1)):
            with self.subTest(fallback=stated):
                out = self.view("since", ledger(stated, UNRESOLVED))
                self.assert_measured_from(out, stated, "since")
                self.assertIn("%d hard-rule line(s) added since %s" % (count, stated),
                              out.stdout)

    def test_a_hash_in_backticks_is_read_too(self):
        out = self.view("since", ledger("`%s`" % self.first, UNRESOLVED))
        self.assert_measured_from(out, self.first, "since")

    def test_the_script_holds_no_copy_of_the_live_ledgers_fallback(self):
        module = load(CONFORMANCE, "conformance_fallback_field")
        opening = re.split(r"(?m)^## ", LIVE_LEDGER.read_text(encoding="utf-8"), maxsplit=1)[0]
        stated = module.FALLBACK_FIELD.search(opening)
        self.assertIsNotNone(stated, "the live ledger states no fallback in its opening "
                                     "section, so there is no hash to look for")
        value = stated.group(1).strip().strip("`")
        self.assertRegex(value, r"^[0-9a-f]{7,40}$",
                         "the live ledger's fallback is not a commit hash: %r" % value)
        self.assertNotIn(value[:7], CONFORMANCE.read_text(encoding="utf-8"),
                         "conformance.py carries the fallback hash %s itself. The ledger's "
                         "line is the one copy; a second one disagrees the first time the "
                         "maintainer moves either" % value[:7])


class AFallbackRunIsAnOrdinaryRun(FixtureRepository):
    def test_each_view_prints_what_it_prints_for_the_same_explicit_ref(self):
        """From the `== ` header on, byte for byte. That includes the reverse check's verdict."""
        for stated in (self.root, self.first, self.second, self.third):
            for view in VIEWS:
                with self.subTest(view=view, fallback=stated):
                    fallen = self.view(view, ledger(stated, UNRESOLVED))
                    explicit = run_view(self.repo, view, "--ref", stated)
                    self.assertEqual(0, fallen.returncode, fallen.stderr)
                    self.assertEqual(0, explicit.returncode, explicit.stderr)
                    report = from_the_header(explicit.stdout)
                    self.assertIsNotNone(report)
                    self.assertEqual(report, from_the_header(fallen.stdout))

    def test_the_reverse_check_reaches_both_verdicts_on_a_fallback_range(self):
        """Derived above; pinned here so the equality is not two empty reports agreeing."""
        not_clean = self.view("reverse-check", ledger(self.first, UNRESOLVED))
        self.assertIn("VERDICT: NOT CLEAN", not_clean.stdout)
        self.assertRegex(not_clean.stdout, r"TESTED\s+1 line\(s\) in source, hosts -- 0 cited "
                                           r"at the line, 1 NOT cited")
        self.assertRegex(not_clean.stdout, r"UNTESTED 1 line\(s\)")
        clean = self.view("reverse-check", ledger(self.third, UNRESOLVED))
        self.assertIn("VERDICT: clean", clean.stdout)

    def test_a_fallback_run_that_adds_nothing_still_prints_the_line(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.third, UNRESOLVED))
                self.assert_measured_from(out, self.third, view)
                self.assertEqual(1, len(fallback_lines(out.stdout)),
                                 "a FALLBACK line printed only on a non-zero run makes its "
                                 "absence ambiguous:\n%s" % out.stdout)
        zero = self.view("since", ledger(self.third, UNRESOLVED))
        self.assertIn("0 hard-rule line(s) added since %s" % self.third, zero.stdout)

    def test_the_gate_reads_a_fallback_report_as_it_reads_any_other(self):
        """`tests/test_new_hard_rules_are_cited_or_deferred.py` parses this stdout."""
        guard = load(GUARD_PATH, "reverse_contract_guard_for_the_fallback")
        out = self.view("since", ledger(self.first, UNRESOLVED))
        parsed = guard.parse_since(out.stdout)
        self.assertEqual(2, parsed.reported,
                         "the gate's parser did not find the two rules of the fallback range")
        self.assertEqual([], parsed.unknown_headings,
                         "a resolver line parsed as a file heading: %s" % parsed.unknown_headings)
        self.assertEqual([], parsed.unresolved)
        for line in fallback_lines(out.stdout):
            stripped = line.strip()
            self.assertFalse(stripped.startswith("+ "), "the FALLBACK line parses as a rule")
            self.assertFalse(stripped.endswith(".md") and " " not in stripped,
                             "the FALLBACK line parses as a file heading")


class AnEntryThatResolvesAlwaysWins(FixtureRepository):
    def test_a_resolving_entry_is_used_and_the_fallback_is_not(self):
        audits = (("2026-01-09", self.third),)
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.root, audits))
                self.assert_measured_from(out, self.third, view)
                self.assertIn("(ref %s from ledger entry production-readiness-audit-2026-01-09)"
                              % self.third, out.stdout)
                self.assertEqual([], fallback_lines(out.stdout),
                                 "an audit entry resolved and the run still printed FALLBACK")

    def test_an_older_entry_behind_a_newer_uncommitted_one_still_wins(self):
        audits = (("2026-01-09", "uncommitted"), ("2026-01-02", self.root))
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(self.third, audits))
                self.assert_measured_from(out, self.root, view)
                self.assertIn("(ref %s from ledger entry production-readiness-audit-2026-01-02)"
                              % self.root, out.stdout)
                self.assertIn("skipped production-readiness-audit-2026-01-09", out.stdout)
                self.assertEqual([], fallback_lines(out.stdout))

    def test_the_output_is_unchanged_by_stating_a_fallback(self):
        """Not breaking where an audit entry resolves: with and without the line, same bytes."""
        audits = (("2026-01-09", "uncommitted"), ("2026-01-02", self.first))
        for view in VIEWS:
            with self.subTest(view=view):
                without = self.view(view, ledger(None, audits))
                with_line = self.view(view, ledger(self.third, audits))
                self.assertEqual(0, without.returncode, without.stderr)
                self.assertEqual(without.stdout, with_line.stdout)


class NoUsableFallbackRefuses(FixtureRepository):
    """Exit 2, stderr says what was read, and stdout carries no count."""

    def assert_refused(self, out, view, *read):
        self.assertEqual(2, out.returncode,
                         "%s must refuse with exit 2; stdout:\n%s\nstderr:\n%s"
                         % (view, out.stdout, out.stderr))
        self.assertFalse(prints_a_count(out.stdout),
                         "%s refused and still printed a figure:\n%s" % (view, out.stdout))
        self.assertEqual([], fallback_lines(out.stdout))
        for expected in read:
            self.assertIn(expected, out.stderr,
                          "the refusal does not say what it read (%r):\n%s"
                          % (expected, out.stderr))

    def test_the_ledger_states_no_fallback(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(None, UNRESOLVED))
                self.assert_refused(out, view, "no fallback",
                                    "production-readiness-audit-2026-01-09 (uncommitted)",
                                    "production-readiness-audit-2026-01-05 "
                                    "(committed (hash not recorded))",
                                    NOT_A_COMMIT)

    def test_no_audit_entry_and_no_fallback(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(None))
                self.assert_refused(out, view, "no audit entry found in the ledger",
                                    "no fallback")

    def test_the_fallback_is_not_a_commit_in_the_repository(self):
        for view in VIEWS:
            with self.subTest(view=view):
                out = self.view(view, ledger(NOT_A_COMMIT, UNRESOLVED[:2]))
                self.assert_refused(out, view, NOT_A_COMMIT, "is not a commit here",
                                    "production-readiness-audit-2026-01-09 (uncommitted)")

    def test_the_fallback_is_not_a_hash(self):
        for stated in ("none yet", "", "HEAD"):
            for view in VIEWS:
                with self.subTest(view=view, fallback=stated):
                    out = self.view(view, ledger(stated, UNRESOLVED))
                    self.assert_refused(out, view, "is not a commit hash", repr(stated))

    def test_a_fallback_line_below_the_first_entry_is_not_the_ledgers_fallback(self):
        """The opening section states it. A line inside an entry is that entry's prose."""
        text = ledger(None, UNRESOLVED, tail="\n" + fallback_line(self.first))
        for view in VIEWS:
            with self.subTest(view=view):
                self.assert_refused(self.view(view, text), view, "no fallback")

    def test_a_repository_with_no_ledger_still_refuses(self):
        (self.repo / "specs" / "IMPLEMENTED.md").unlink()
        try:
            for view in VIEWS:
                with self.subTest(view=view):
                    out = run_view(self.repo, view, "--since-last-audit")
                    self.assert_refused(out, view, "no specs/IMPLEMENTED.md")
        finally:
            self.write_ledger(ledger())


class ThisRepositorysLedger(unittest.TestCase):
    """The live ledger, checked for the property. Its hashes are read, never pinned here."""

    AUDIT_ENTRY = re.compile(r"(?m)^## (production-readiness-audit\S*)\n(.*?)(?=\n## |\Z)", re.S)
    COMMIT = re.compile(r"(?m)^\s*-\s+\*\*Commit:\*\*\s*`?([0-9a-f]{7,40})`?\s*$")

    @staticmethod
    def is_a_commit(ref):
        done = subprocess.run(["git", "rev-parse", "--verify", "%s^{commit}" % ref],
                              cwd=str(REPO_ROOT), capture_output=True, text=True)
        return done.returncode == 0

    def setUp(self):
        if not shutil.which("git"):
            self.skipTest("git is required to resolve the ledger's commits")
        shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                                 cwd=str(REPO_ROOT), capture_output=True, text=True)
        if shallow.returncode != 0 or shallow.stdout.strip() != "false":
            self.skipTest("not a full git history, so the ledger's commits cannot be resolved")
        self.text = LIVE_LEDGER.read_text(encoding="utf-8")
        self.module = load(CONFORMANCE, "conformance_fallback_live")

    def stated_fallback(self):
        opening = re.split(r"(?m)^## ", self.text, maxsplit=1)[0]
        stated = self.module.FALLBACK_FIELD.search(opening)
        return stated.group(1).strip().strip("`") if stated else None

    def test_the_opening_section_states_a_fallback_that_is_a_commit_here(self):
        stated = self.stated_fallback()
        self.assertIsNotNone(stated, "specs/IMPLEMENTED.md states no fallback commit above its "
                                     "first entry, so the views refuse when no audit resolves")
        self.assertTrue(self.is_a_commit(stated),
                        "the ledger's fallback commit %r is not a commit in this repository"
                        % stated)

    def test_both_views_run_here_and_name_where_the_range_start_came_from(self):
        resolving = None
        for name, body in self.AUDIT_ENTRY.findall(self.text):
            recorded = self.COMMIT.search(body)
            if recorded and self.is_a_commit(recorded.group(1)):
                resolving = (name, recorded.group(1))
                break
        for view in VIEWS:
            with self.subTest(view=view):
                out = subprocess.run(
                    [sys.executable, str(CONFORMANCE), view, "--since-last-audit"],
                    capture_output=True, text=True, cwd=str(REPO_ROOT))
                self.assertEqual(0, out.returncode,
                                 "%s --since-last-audit cannot run in this repository:\n%s"
                                 % (view, out.stderr))
                if resolving:
                    self.assertIn("(ref %s from ledger entry %s)" % (resolving[1], resolving[0]),
                                  out.stdout,
                                  "%s did not name the newest audit entry that resolves" % view)
                    self.assertEqual([], fallback_lines(out.stdout),
                                     "an audit entry resolves and %s fell back" % view)
                else:
                    lines = fallback_lines(out.stdout)
                    self.assertEqual(1, len(lines), out.stdout)
                    self.assertIn(self.stated_fallback(), lines[0])


if __name__ == "__main__":
    unittest.main()
