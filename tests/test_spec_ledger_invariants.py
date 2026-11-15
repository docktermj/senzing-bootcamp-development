"""An implemented spec's guarantee must end up in INVARIANTS.md, or say it doesn't.

`specs/INVARIANTS.md` opens by describing itself as machine-extended: "as specs are
implemented, the guarantee a spec establishes becomes an invariant that all future work
must maintain." Nothing enforced that, and one spec slipped through.

`bootcamp-prep-name-never-asked` decided that the Bootcamper's name is detected silently
and never asked. It was implemented and ledgered in `specs/IMPLEMENTED.md` — and
registered no invariant. The guarantee therefore had no address, so two places reached for
the closest-looking ID and cited **INV-076**, which governs the Core-vs-Customized path
choice and says nothing about the name: INVARIANTS.md's own INV-113 parenthetical, and
`graduation/SKILL.md`. A wrong citation in the invariants file is worse than a missing
one, because it looks authoritative. Filed as INV-134 during the 2026-07-26 audit.

Two directions are pinned:

1. **Forward** — a spec implemented on or after the cutoff must either be cited as a
   `Source:` in INVARIANTS.md, name the invariant it established, or state plainly that
   it established none. Any of the three is fine; silence is not.
2. **Backward** — every `Source:` in INVARIANTS.md must name a spec that actually
   exists, so an invariant can never cite a phantom.

Entries before the cutoff are grandfathered deliberately: ~145 specs predate this test
and many are fixes that correctly establish nothing, so retrofitting a marker onto all of
them would be churn with no signal. The gate is forward-looking on purpose.

Also enforces **INV-207** (a claim about this repo's own reference graph is verified AFTER it
is recorded, never before; and evidence for "identifier X is unused" must not quote X), which
names this file as its enforcer. `TestTheLedgerIsVerifiedAfterItIsWritten` pins the three
things `implement-spec`'s Step 4 must say: that `citations.py verify` runs after the entry is
written, *why* (the ledger is inside the corpus the scan reads), and that a test count is not
a verdict. (⚠️ **Dated note, 2026-10-02 (#395): the section is now the implement overlay's
"## Phase 6: Record the implementation".** It was "## Step 4", a step the governing copy does not
have; the overlay now names the governing copy's phases, and the class also pins the order
against them: entry before the Phase 6 commit, the scan in Phase 7, again after any later
ledger edit before Gate 2. The three things above are unchanged.) The detection itself belongs to `citations.py verify`, which caught all three
instances; what this file guards is that the ordering instruction cannot be quietly dropped.

⚠️ **Named by INV-307, and the reason its deletion direction exists.** The backward check
below accepts a `Source:` citation that resolves to **either** a file under `specs/` **or** an
entry in `IMPLEMENTED.md`. That tolerance is deliberate and correct -- many ledger entries have
no spec file -- but it means deleting a spec that happens to be ledgered passes this guard while
destroying the reasoning the invariant points at. `tests/test_specs_are_frozen.py` is what
closes that, by pinning the archive's filenames; some citations already resolve through the
ledger alone. ⛔ Do not "tighten" the either/or above to require a file: that would fail every
legitimately file-less entry. The two guards are complementary, not redundant.

Run:  python3 -m unittest discover -s tests
"""
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "specs"
IMPLEMENTED = SPECS / "IMPLEMENTED.md"
INVARIANTS = SPECS / "INVARIANTS.md"

# Entries implemented on or after this date must account for their invariants.
CUTOFF = "2026-07-26"

# Any of these in an entry's body discharges the obligation explicitly.
NO_INVARIANT_PHRASES = (
    "no new invariant",
    "establishes no invariant",
    "established no invariant",
)
ESTABLISHED_MARKERS = (
    "invariant established:",
    "new invariant inv-",
    "**invariant established**",
)

# The third state, and the one `implement-spec` Step 5 mandates when the maintainer is
# unavailable: a hard rule SHIPPED, its invariant drafted but not registered, because
# only the maintainer may sign off on invariant wording. Without this vocabulary a run
# following the skill has to either claim "establishes no invariant" -- false, and exactly
# the silence the reverse contract forbids -- or leave the suite red. Both are worse than
# recording the deferral.
#
# It is deliberately STRICTER than the other two states: a deferral counts only when the
# entry also carries the drafted wording, so the marker cannot become a bare label that
# retires the obligation. `test_a_deferral_must_carry_its_drafted_wording` pins that.
#: Matched only in the BOLDED form a real deferral uses -- `**DEFERRED INVARIANT ...` or
#: `**... invariant deferred ...**`. ⚠️ An audit record that *discusses* deferrals in prose
#: (e.g. "covered by a recorded `DEFERRED INVARIANT` bullet") is not itself deferring one, and
#: an unbolded substring match reported exactly that as an unaccounted entry on 2026-08-26.
#: The distinction is making a deferral versus mentioning the concept.
DEFERRED_MARKERS = (
    "**deferred invariant",
    "**invariant deferred",
    "— invariant deferred",
)
DRAFT_MARKERS = (
    "drafted wording",
    "draft wording",
    "drafted invariant wording",
)

# Placeholder headings inside each file's own format comment, not real entries.
TEMPLATE_NAMES = {"<spec-name>"}

# Entries landed on the cutoff date itself, BEFORE this test existed. They are named
# individually rather than covered by a looser cutoff, so the exemption is auditable and
# cannot quietly widen. Each was reviewed as part of the 2026-07-26 audit; none is
# claimed here to have established an invariant either way. Do not add to this set —
# a new entry states its own answer instead.
# Adapted (one-repository migration, 2026-11-14): emptied. Its five entries are in the archived
# ledger, and this repository's ledger starts after the cutoff, so none can be named here.
GRANDFATHERED = frozenset()

# The day this repository's ledger starts. A `Source:` cited before it resolves in the archive
# (`specs/README.md`, "The archive").
LEDGER_STARTS = "2026-11-14"


def flatten(text):
    """Collapse whitespace so a marker phrase still matches when prose wraps.

    Ledger bodies are hand-wrapped Markdown, so "establishes no new\\n  invariant" is the
    normal shape rather than the exception — matching raw substrings against it produced a
    false failure on the very first entry that used the phrase.
    """
    return re.sub(r"\s+", " ", text).lower()


def entries():
    """Yield (name, iso_date_or_None, body_text) for each ## entry in IMPLEMENTED.md."""
    text = IMPLEMENTED.read_text(encoding="utf-8")
    chunks = re.split(r"^## (?=\S)", text, flags=re.MULTILINE)[1:]
    for chunk in chunks:
        name, _, body = chunk.partition("\n")
        name = name.strip()
        if name in TEMPLATE_NAMES:
            continue
        m = re.search(r"\*\*Implemented:\*\*\s*(\d{4}-\d{2}-\d{2})", body)
        yield name, (m.group(1) if m else None), body


def invariant_sources():
    """Every spec name cited as a `Source:` by an invariant."""
    text = INVARIANTS.read_text(encoding="utf-8")
    return set(re.findall(r"Source:\s*`([^`]+)`", text)) - TEMPLATE_NAMES


def phantom_sources(invariants_text, ledgered):
    """Spec names cited as a `Source:` that resolve nowhere: not here, and not in the archive.

    A source with a spec file or a ledger entry in this repository resolves here. Any other
    source is an archived one, unless a citation of it is dated on or after ``LEDGER_STARTS``:
    the archive was pinned that day, so such a source can only be an entry in this ledger.
    """
    newest = {}
    for name, rest in re.findall(r"Source:\s*`([^`]+)`([^)]{0,120})", invariants_text):
        date = re.search(r"\d{4}-\d{2}-\d{2}", rest)
        newest[name] = max(newest.get(name, ""), date.group(0) if date else "")
    return sorted(
        name for name, date in newest.items()
        if name not in TEMPLATE_NAMES and date >= LEDGER_STARTS
        and not (SPECS / f"{name}.md").exists() and name not in ledgered)


class TestForwardCoverage(unittest.TestCase):
    """A newly implemented spec accounts for the invariant it established."""

    def test_recent_entries_account_for_their_invariants(self):
        sources = invariant_sources()
        unaccounted = []
        for name, date, body in entries():
            if date is None or date < CUTOFF:
                continue
            if name in GRANDFATHERED or name in sources:
                continue
            flat = flatten(body)
            if any(flatten(p) in flat for p in NO_INVARIANT_PHRASES):
                continue
            if any(flatten(p) in flat for p in ESTABLISHED_MARKERS):
                continue
            if any(flatten(p) in flat for p in DEFERRED_MARKERS) and any(
                flatten(p) in flat for p in DRAFT_MARKERS
            ):
                continue
            unaccounted.append(
                f"{name} (implemented {date}) is neither cited as a `Source:` in "
                "INVARIANTS.md, nor names the invariant it established, nor states "
                "that it established none, nor defers one with its drafted wording"
            )
        self.assertEqual(
            [],
            unaccounted,
            "IMPLEMENTED.md entries whose guarantee has no recorded address — the "
            "defect that left the name-detection design citing INV-076:\n  "
            + "\n  ".join(unaccounted),
        )

    def test_a_deferral_must_carry_its_drafted_wording(self):
        """A bare "deferred" label must not retire the obligation it defers.

        The deferral state exists so a run that ships a hard rule it cannot register
        still records the rule. An entry that says "deferred" and stops has recorded
        nothing a later reader can act on, so it stays unaccounted-for.
        """
        for name, date, body in entries():
            if date is None or date < CUTOFF:
                continue
            flat = flatten(body)
            if not any(flatten(p) in flat for p in DEFERRED_MARKERS):
                continue
            self.assertTrue(
                any(flatten(p) in flat for p in DRAFT_MARKERS),
                f"{name} defers an invariant without recording its drafted wording, so "
                "the rule it shipped has no address a later run can pick up",
            )

    def test_the_cutoff_actually_covers_something(self):
        """A cutoff past the newest entry would make this test vacuous."""
        dated = [d for _, d, _ in entries() if d]
        self.assertTrue(dated, "no dated entries parsed — the parser has drifted")
        self.assertGreaterEqual(
            max(dated), CUTOFF, "CUTOFF is in the future; the forward gate checks nothing"
        )
        covered = [
            n for n, d, _ in entries() if d and d >= CUTOFF and n not in GRANDFATHERED
        ]
        self.assertTrue(
            covered,
            "every post-cutoff entry is grandfathered, so the gate checks nothing — "
            "grandfathering is for entries that predate this test, not new ones",
        )

    def test_grandfather_list_matches_real_entries(self):
        """A stale exemption silently widens the gate; a typo'd one does nothing."""
        names = {n for n, _, _ in entries()}
        self.assertEqual(
            set(),
            GRANDFATHERED - names,
            "GRANDFATHERED names an entry that no longer exists in IMPLEMENTED.md",
        )


class TestBackwardCoverage(unittest.TestCase):
    """An invariant may not cite a spec that does not exist."""

    def test_every_invariant_source_names_a_real_spec(self):
        # Adapted (one-repository migration, 2026-11-14): a source cited before this ledger
        # started resolves in the archive, so only a source dated since must resolve here.
        ledgered = {name for name, _, _ in entries()}
        phantoms = phantom_sources(INVARIANTS.read_text(encoding="utf-8"), ledgered)
        self.assertEqual(
            [],
            phantoms,
            f"INVARIANTS.md cites spec(s) dated on or after {LEDGER_STARTS} with no file "
            f"under specs/ and no entry in IMPLEMENTED.md: {phantoms}",
        )

    def test_only_a_source_cited_before_the_ledger_started_is_archived(self):
        """The negative control: the archive cannot hold a source cited after it was pinned."""
        archived = "- **INV-001** — A rule. (Source: `an-archived-spec`, 2026-07-24.)\n"
        phantom = "- **INV-002** — A rule. (Source: `a-phantom-spec`, %s.)\n" % LEDGER_STARTS
        self.assertEqual([], phantom_sources(archived, set()))
        self.assertEqual(["a-phantom-spec"], phantom_sources(archived + phantom, set()))
        self.assertEqual([], phantom_sources(archived + phantom, {"a-phantom-spec"}))

    def test_inv_134_is_traceable_to_its_spec(self):
        """The specific hole this test was written for stays closed."""
        text = INVARIANTS.read_text(encoding="utf-8")
        self.assertRegex(text, r"\*\*INV-134\*\*", "INV-134 is missing")
        self.assertIn("bootcamp-prep-name-never-asked", invariant_sources())
        self.assertNotIn(
            "never asked (INV-076)",
            text,
            "the name-detection design is citing INV-076 again",
        )


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------------------
# Ledger-claim hygiene (deep-dive-audit-2026-07-29-minor-fixes, items 3 and 4).
#
# Two failures of the ledger AS EVIDENCE, both found by the 2026-07-29 audit:
#
#   Item 3 — 66 of 199 entries said `Commit: uncommitted` against a clean tree, so the
#   field could not answer the one question it exists for. They were backfilled from a
#   derived rule (the commit that added the entry's heading); this pins the field's shape
#   so free text cannot creep back in and staleness has a fixed vocabulary.
#
#   Item 4 — two specs were recorded as implemented with an acceptance criterion unmet
#   (`relocate-integration-deployment-questions-to-module1`, whose criterion named
#   graduation as a reader, and `defer-commonmark-to-graduation`, whose criterion named
#   the generated `production/*.md`). Both left an invariant standing unimplemented for
#   weeks. The commonest visible symptom is a spec predicting a file its ledger entry
#   never records changing, so that is what is gated here — forward-only.
#
# The affected-files gate is FORWARD-ONLY on purpose, exactly as TestForwardCoverage above
# is. A spec's `## Affected files` is a prediction and the entry's `Files changed:` is the
# outcome, so a gap is frequently legitimate (the change turned out not to need the file).
# 38 pre-cutoff entries carry one. Gating them retroactively would be a gate that cannot
# represent a legitimate input — the shape INV-144/INV-173 forbid — so the whole corpus is
# reported instead, by `.claude/skills/dry-run/coverage_reports.py affected`.
# ---------------------------------------------------------------------------------------

# Retired (one-repository migration, 2026-11-14): the affected-files gate described above
# (`AFFECTED_CUTOFF`, `AFFECTED_GRANDFATHERED`, `predicted_paths` and the three cases of
# `TestAffectedFilesAccounting`). It compared a ledger entry with its spec file's
# `## Affected files`, and the spec files stayed in the archive, so it had no input here.

COMMIT_FIELD = re.compile(r"^- \*\*Commit:\*\*(.*)$", re.M)
HASH = re.compile(r"`?\b[0-9a-f]{7,40}\b`?")


class TestCommitFieldHygiene(unittest.TestCase):
    """`Commit:` carries a hash, `uncommitted`, or `committed (hash not recorded)`."""

    def test_every_entry_has_a_commit_field(self):
        missing = [n for n, _, body in entries() if not COMMIT_FIELD.search(body)]
        self.assertEqual(
            [], missing, "IMPLEMENTED.md entries with no `Commit:` field:\n  "
            + "\n  ".join(missing)
        )

    def test_commit_fields_use_the_fixed_vocabulary(self):
        bad = []
        for name, _, body in entries():
            m = COMMIT_FIELD.search(body)
            if not m:
                continue
            value = m.group(1).strip()
            if HASH.search(value):
                continue
            if value in ("uncommitted", "`uncommitted`", "committed (hash not recorded)"):
                continue
            bad.append(f"{name}: {value!r}")
        self.assertEqual(
            [],
            bad,
            "`Commit:` must be a hash, `uncommitted`, or `committed (hash not "
            "recorded)` — free text makes the field unreadable:\n  " + "\n  ".join(bad),
        )

    def test_every_recorded_hash_resolves_to_a_real_commit(self):
        """Hash-*shaped* is not hash-*valid*, and the difference hid for two weeks.

        `test_commit_fields_use_the_fixed_vocabulary` accepts any 7–40 hex run, so a
        hash that resolves to nothing passes it while answering the one question the
        field exists for with a lie — and unlike `uncommitted`, it looks answered. On
        2026-07-31, 22 of 228 entries recorded commits from a 2026-07-15/16 history
        rewrite that no longer exist in the object store or any reflog. They were
        repaired to the post-rewrite commits, but nothing would have caught them.

        Skipped rather than failed when history is unavailable (shallow clone, no git,
        not a work tree) — a partial clone must not read as a corrupt ledger.
        """
        if not (REPO_ROOT / ".git").exists():
            self.skipTest("not a git work tree")
        if subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--is-shallow-repository"],
            capture_output=True, text=True,
        ).stdout.strip() == "true":
            self.skipTest("shallow clone — pre-rewrite history is not present")

        dangling, checked = [], 0
        for name, _, body in entries():
            m = COMMIT_FIELD.search(body)
            if not m:
                continue
            value = m.group(1).strip()
            if value.startswith("uncommitted") or "hash not recorded" in value:
                continue
            found = HASH.search(value)
            if not found:
                continue
            # The primary hash is the first one; a repaired entry also cites the dead
            # pre-rewrite hash in a trailing "(was `…`)" note, which must not be checked.
            digest = found.group(0).strip("`")
            checked += 1
            if subprocess.run(
                ["git", "-C", str(REPO_ROOT), "cat-file", "-e", digest + "^{commit}"],
                capture_output=True,
            ).returncode:
                dangling.append("%s: %s" % (name, digest))

        # Adapted (one-repository migration, 2026-11-14): the ledger starts fresh, so the
        # floor of 100 checked hashes is dropped. Every hash it does record is still resolved.
        self.assertTrue(list(entries()), "no entry parsed, so the scan is vacuous")
        self.assertEqual(
            [], dangling,
            "%d recorded commit hash(es) resolve to nothing — the field cannot answer "
            "what it exists for. Find the surviving commit (its subject usually names "
            "the spec, or it is the commit that added the entry's `## heading`) and "
            "record it as `<new>` (was `<old>`, …):\n  %s"
            % (len(dangling), "\n  ".join(dangling)),
        )


class TestTheLedgerIsVerifiedAfterItIsWritten(unittest.TestCase):
    """A clean citation scan recorded *before* the entry exists measured a different repo.

    The ledger is inside the corpus `citations.py verify` reads. An entry whose evidence
    sentence wrote out an unminted `INV-NNN` created two citations of an undefined
    invariant and turned the whole suite red — after that same run had recorded the scan
    as clean. Ordering is the fix, so the ordering instruction is what gets pinned.
    """

    SKILL = REPO_ROOT / ".claude" / "skill-overlays" / "implement-github-issue.md"

    def setUp(self):
        self.assertTrue(self.SKILL.is_file(), "implement-github-issue.md moved — re-point this guard")
        self.body = self.SKILL.read_text(encoding="utf-8")

    HEADING = "## Phase 6: Record the implementation"

    def phase_six(self):
        """The ledger section only: the instruction has to live in the section that writes the entry.

        Named for the governing copy's Phase 6, which writes the tests and makes the commit. It
        was "## Step 4", residue of the command file the overlay replaced (#395).
        """
        start = self.body.index(self.HEADING)
        end = self.body.index("## Declining an issue instead of implementing it", start)
        return re.sub(r"\s+", " ", self.body[start:end]).replace("**", "")

    def test_the_overlay_names_no_step_the_governing_copy_lacks(self):
        """The governing copy is organized as Phases 0-9; a "Step 4" places nothing (#395)."""
        self.assertIn(self.HEADING, self.body,
                      "the overlay's ledger section is not headed %r" % self.HEADING)
        self.assertNotRegex(
            self.body, r"\bStep 4\b",
            "the overlay still names a 'Step 4'. The governing copy has Phases 0-9 and no Step 4, "
            "so a worker cannot place the ledger write against Phase 7 or Gate 2")
        self.assertIn('see "Phase 6: Record the implementation"', self.body,
                      "the CI section no longer points at the renamed ledger section")

    def test_phase_six_requires_the_scan_after_the_entry(self):
        section = self.phase_six()
        self.assertIn(
            "citations.py verify", section,
            "Phase 6 never names the citation scan, so nothing tells a run to re-check the "
            "corpus its own entry just joined")
        self.assertRegex(
            section, r"(?i)AFTER the entry is written|after the ledger entry is written",
            "Phase 6 must say the scan runs AFTER the entry is written. Naming the command "
            "without the ordering is what already failed: the scan ran during the criterion "
            "walk, the entry was written afterwards, and the entry was what broke it.")

    def test_phase_six_places_the_entry_and_the_scan_in_the_governing_phases(self):
        """Entry before the Phase 6 commit; scan in Phase 7; again after a later edit (#395)."""
        section = self.phase_six()
        for pattern, why in (
                (r"(?i)Phase 6: write the entry [^.]*before the Phase 6 commit",
                 "the entry is not placed before the Phase 6 commit"),
                (r"(?i)in the same commit as the change",
                 "the entry is not put in the same commit as the change"),
                (r"(?i)Phase 7: run `citations\.py verify`[^.]*after the entry exists",
                 "the scan is not placed in Phase 7, after the entry exists"),
                (r"(?i)after any later edit to the ledger, run `citations\.py verify` again "
                 r"before Gate 2",
                 "the scan is not re-run after a later ledger edit, before Gate 2"),
                (r"(?i)a clean scan from before that edit does not count",
                 "nothing says a scan taken before a later ledger edit does not count")):
            with self.subTest(pattern=pattern):
                self.assertRegex(section, pattern, why)
        order = [section.index(s) for s in ("Phase 6: write the entry",
                                             "Phase 7: run `citations.py verify`",
                                             "run `citations.py verify` again before Gate 2")]
        self.assertEqual(sorted(order), order,
                         "the three placements are not stated in phase order")

    def test_phase_six_says_why_the_ordering_matters(self):
        """Without the reason, the ordering reads as ceremony and gets optimized away."""
        section = self.phase_six()
        self.assertRegex(
            section, r"(?i)ledger is (\*\*)?inside(\*\*)? the corpus|inside the corpus",
            "the ordering must carry its reason — that the ledger is part of what the scan "
            "reads — or a later editor will reasonably move it back next to the other checks")

    def test_phase_six_warns_that_a_count_is_not_a_result(self):
        """The same run also read `Ran N tests` and missed `FAILED` on the next line."""
        section = self.phase_six()
        self.assertRegex(
            section, r"(?i)A count is not a result|read the runner's verdict",
            "Phase 6 must warn that a test count is not a verdict. The run that recorded a "
            "red suite as '1792 passed' took the number off the `Ran 1792 tests` line while "
            "`FAILED (failures=1, skipped=3)` sat directly beneath it")
