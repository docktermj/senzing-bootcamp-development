"""Tests that what the bootcamp says about models and effort levels stays consistent.

Two things here are point-in-time or stated twice, and nothing else couples them:

1. **Model names.** The welcome names one model (`{{host.model_capable}}`), and the Claude
   install pages and `docs/model-selection.md` name models and IDs. A superseded name would
   point a bootcamper at a model one generation back, and the pair drifted that far once
   before a bootcamper reported it.
2. **The per-stage effort table.** `skills/bootcamp-onboarding/ground-rules.md` → "Working
   depth by stage" is the copy the guide loads; `docs/model-selection.md` carries a derived
   copy beside the reasoning for each level.

These tests are the enforcement:

1. No superseded model name or ID survives anywhere in the shipped plugin.
2. The two per-stage tables, and the instruction for each level, agree.
3. Every stage the bootcamp can run has exactly one row, with one level.

Named as its enforcer by **INV-114** (model guidance names only current models and IDs, with
`ground-rules.md` authoritative and `docs/model-selection.md` derived and dated) and by
**INV-140** (every stage the bootcamp can run has exactly one row in the per-stage table,
including the apparatus-exempt setup stages). ⚠️ Issue #4 changed what that table holds: it
was a model and effort recommendation the bootcamper was asked to set, and is now an effort
level the guide works to by instruction, with no model column. Both invariants' registered
wording still describes the old table; the parts checked here are the parts that survive.
`tests/test_working_depth_by_stage.py` checks the table against every assistant's package.

⚠️ **Dated note, 2026-11-16 (#12): `docs/model-selection.md` is read from this repository, not
from the Claude package.** It is a maintainer page, moved from `source/docs/` to `docs/`, and
no package carries it. The superseded-name scan used to reach it by walking the package; it
is now named in `shipped_markdown()`, and `test_the_maintainer_page_is_in_the_scan` fails if
it drops out. Every other check reads the same page at its new path. No case was retired.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest
from _built import built  # the Claude package, built from source/

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(str(built("claude")))
GROUND_RULES = os.path.join(PLUGIN, "skills", "bootcamp-onboarding", "ground-rules.md")
# The maintainer page: in this repository under docs/, in no package (#12).
MODEL_SELECTION = os.path.join(REPO_ROOT, "docs", "model-selection.md")

# Model names/IDs that have been superseded. A hit means the bootcamp would name a
# model one generation back — the defect this guards. Add a row whenever a model is superseded; the last element of each pair
# is the current replacement, quoted in the failure message.
SUPERSEDED = [
    ("Opus 4.8", "Opus 5.5"),
    ("claude-opus-4-8", "claude-opus-5-5"),
    ("Opus 5", "Opus 5.5"),
    ("Sonnet 5", "Sonnet 5.5"),
    ("Fable 5", "Fable 5.1"),
    ("claude-opus-5", "claude-opus-5-5"),
    ("claude-sonnet-5", "claude-sonnet-5-5"),
    ("claude-fable-5", "claude-fable-5-1"),
]


def superseded_pattern(stale):
    """Match `stale` only where it ends at a version boundary.

    A plain substring test cannot hold a row like ("Opus 5", "Opus 5.5"): the stale
    name is a prefix of its own replacement, as `claude-opus-5` is of
    `claude-opus-5-5`. So a display name must not be followed by `.<digit>` or a
    digit ("Opus 5" is not "Opus 5.5", but is "Opus 5," "Opus 5 /" and a
    sentence-final "Opus 5."), and an ID must not be followed by `-<digit>` or a
    digit (`claude-opus-5` is not `claude-opus-5-5`, but is `claude-opus-5[1m]`).
    """
    if stale.startswith("claude-"):
        return re.compile(r"(?<![\w-])" + re.escape(stale) + r"(?!-?\d)")
    return re.compile(r"\b" + re.escape(stale) + r"(?!\.?\d)")


# The one block allowed to name a superseded model: the staleness note in
# docs/model-selection.md deliberately cites the prior models to explain the
# supersession. Only that blockquote is exempt, never the rest of the file: a
# whole-file exemption is how that file's tier table kept naming Fable 5, Opus 5
# and Sonnet 5 after they were superseded.
STALENESS_NOTE_FILE = MODEL_SELECTION
STALENESS_NOTE_MARKER = "> **Point-in-time data"


def without_staleness_note(text):
    """`text` with the staleness-note blockquote removed, and nothing else.

    The block is the run of `>` lines that starts at STALENESS_NOTE_MARKER. With
    no marker nothing is removed, so a missing note exempts nothing.

    Line-scoped by design (#424): a `>` marker opens each line of a blockquote.
    """
    lines = text.splitlines(keepends=True)
    kept, in_note = [], False
    for line in lines:
        if line.startswith(STALENESS_NOTE_MARKER):
            in_note = True
        elif in_note and not line.startswith(">"):
            in_note = False
        if not in_note:
            kept.append(line)
    return "".join(kept)


def superseded_offenders(rel, text, exempt_note=False):
    """Every superseded name or ID in `text`, as failure-message lines."""
    if exempt_note:
        text = without_staleness_note(text)
    return [
        f"{rel}: '{stale}' should be '{current}'"
        for stale, current in SUPERSEDED
        if superseded_pattern(stale).search(text)
    ]


TABLE_HEADER = "| Stage | Effort |"


# Repo-level user-facing docs. Included because a rename or model refresh that
# lands only inside plugins/ leaves these contradicting it — the exact
# "renamed in one place" defect. `specs/`, `SENZING_BOOTCAMP_FEEDBACK_*.md`,
# and `specs/IMPLEMENTED.md` are deliberately NOT scanned: they are historical
# records and must keep naming what was true when written.
# Adapted (one-repository migration, 2026-11-14): `docs/README.md`, the old Claude user doc,
# was deleted. The user-facing docs that name a model are now the public README and the Claude
# install fragments (`Opus 5.5` and `claude --model claude-opus-5-5` are in
# `site-install.html` and `site-tips.html`), so those are read in its place. The fragments are
# HTML; the names and IDs sit in their text as written, so they are matched as text. A listed
# file that is missing now fails (`test_every_repo_doc_exists_and_one_names_a_model`) where
# the old loop skipped it silently.
CLAUDE_FRAGMENTS = os.path.join(REPO_ROOT, "hosts", "claude", "fragments")
REPO_DOCS = [
    os.path.join(REPO_ROOT, "README.md"),
    os.path.join(REPO_ROOT, "public", "README.md"),
    os.path.join(CLAUDE_FRAGMENTS, "site-before.html"),
    os.path.join(CLAUDE_FRAGMENTS, "site-install.html"),
    os.path.join(CLAUDE_FRAGMENTS, "site-tips.html"),
]


def shipped_markdown():
    """Every Markdown file under the shipped plugin, plus repo-level user docs and the
    maintainer page (which no package carries, so the walk does not reach it; #12)."""
    for dirpath, dirnames, filenames in os.walk(PLUGIN):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)
    for path in REPO_DOCS:
        yield path
    yield MODEL_SELECTION


def stage_table(path):
    """Extract the per-stage effort table as a list of cell-tuples.

    Tolerates leading indentation: the ground-rules copy is nested inside a
    bullet, the model-selection copy sits at column zero.

    Line-scoped by design (#424): a table row is one line.
    """
    with open(path, encoding="utf-8") as fh:
        lines = [line.strip() for line in fh]
    if TABLE_HEADER not in lines:
        raise AssertionError(f"per-stage table header not found in {path}")
    start = lines.index(TABLE_HEADER)
    rows = []
    for line in lines[start + 2:]:  # skip header + separator
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":"}:  # a second separator row
            continue
        rows.append(tuple(cells))
    if not rows:
        raise AssertionError(f"per-stage table in {path} has no rows")
    return rows


class NoSupersededModelReferences(unittest.TestCase):
    """A superseded model name points a bootcamper one generation back — never ship one."""

    def test_no_superseded_names_or_ids(self):
        offenders = []
        for path in shipped_markdown():
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            rel = os.path.relpath(path, REPO_ROOT)
            offenders += superseded_offenders(
                rel, text, exempt_note=(path == STALENESS_NOTE_FILE)
            )
        self.assertEqual(
            offenders, [], "superseded model references found:\n  " + "\n  ".join(offenders)
        )

    def test_the_maintainer_page_is_in_the_scan(self):
        """#12: the page left the package, so the scan must name it or it goes unread."""
        scanned = list(shipped_markdown())
        self.assertEqual(1, scanned.count(STALENESS_NOTE_FILE))
        self.assertTrue(os.path.isfile(STALENESS_NOTE_FILE))
        self.assertFalse(STALENESS_NOTE_FILE.startswith(PLUGIN + os.sep),
                         "the maintainer page is being read from a package again")

    def test_every_repo_doc_exists_and_one_names_a_model(self):
        """INV-265: the repo-level half of the scan reads real files that carry its subject."""
        # Added with the adaptation (one-repository migration, 2026-11-14).
        naming = []
        for path in REPO_DOCS:
            rel = os.path.relpath(path, REPO_ROOT)
            with self.subTest(path=rel):
                self.assertTrue(os.path.isfile(path), "%s is listed in REPO_DOCS and missing" % rel)
            if os.path.isfile(path):
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                if "Opus 5.5" in text and "claude-opus-5-5" in text:
                    naming.append(rel)
        self.assertIn("hosts/claude/fragments/site-install.html", naming,
                      "no repo-level user doc names the current model and its ID, so the "
                      "repo-level half of the superseded-name scan reads nothing it could fail on")

    def test_a_superseded_name_in_the_install_fragment_is_reported(self):
        """Negative control: the walkthrough's own model step, one generation back."""
        path = os.path.join(CLAUDE_FRAGMENTS, "site-install.html")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        self.assertEqual([], superseded_offenders("fragment", text))
        stale = text.replace("<strong>Opus 5.5</strong>", "<strong>Opus 5</strong>").replace(
            "claude-opus-5-5", "claude-opus-5")
        self.assertNotEqual(text, stale, "the control changed nothing")
        self.assertEqual(
            ["fragment: 'Opus 5' should be 'Opus 5.5'",
             "fragment: 'claude-opus-5' should be 'claude-opus-5-5'"],
            superseded_offenders("fragment", stale))

    def test_the_staleness_note_is_found_and_names_what_it_supersedes(self):
        """The exemption is earned: the note exists and is what explains the supersession."""
        with open(STALENESS_NOTE_FILE, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn(STALENESS_NOTE_MARKER, text)
        removed = len(text) - len(without_staleness_note(text))
        self.assertGreater(removed, 0, "the staleness-note block was not found")
        self.assertNotEqual(
            superseded_offenders("note", text), [],
            "the staleness note no longer names the superseded models, so the "
            "exemption is not exercised",
        )

    def test_the_welcome_names_a_current_model(self):
        """The one model the bootcamp names to the bootcamper, as the package renders it."""
        flow = os.path.join(PLUGIN, "skills", "bootcamp-onboarding", "onboarding-flow.md")
        with open(flow, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("Opus 5.5 suits it well", " ".join(text.split()))
        self.assertEqual([], superseded_offenders("onboarding-flow.md", text))


class SupersededMatcherRespectsVersionBoundaries(unittest.TestCase):
    """Negative controls for the matcher and the exemption, on synthetic text.

    Both directions are proven: the current names must pass, and each stale name
    must fail in every position a sentence can put it. A plain `stale in text`
    check fails the first half ("Opus 5" is inside "Opus 5.5"); a whole-file
    exemption fails the second half for model-selection.md.
    """

    def hits(self, text):
        return [stale for stale, _ in SUPERSEDED if superseded_pattern(stale).search(text)]

    def test_current_names_and_ids_do_not_match(self):
        for text in (
            "Opus 5.5, high effort", "Sonnet 5.5 / medium", "Fable 5.1 sits above",
            "`claude-opus-5-5`", "/model claude-sonnet-5-5", "claude-fable-5-1",
            "claude-opus-5-5[1m]", "anthropic.claude-opus-5-5",
        ):
            with self.subTest(text=text):
                self.assertEqual([], self.hits(text))

    def test_stale_display_names_match_at_every_boundary(self):
        for name in ("Opus 5", "Sonnet 5", "Fable 5"):
            for text in (f"{name}, high", f"{name} / high", f"run {name}.",
                         f"on {name}\n", f"**{name}**", f"({name})"):
                with self.subTest(text=text):
                    self.assertIn(name, self.hits(text))

    def test_stale_ids_match_at_every_boundary(self):
        for model_id in ("claude-opus-5", "claude-sonnet-5", "claude-fable-5"):
            for text in (f"`{model_id}`", f"/model {model_id} ", f"{model_id}[1m]",
                         f"--model {model_id}\n", f"{model_id}."):
                with self.subTest(text=text):
                    self.assertIn(model_id, self.hits(text))

    def test_the_old_substring_check_could_not_hold_the_new_rows(self):
        """Why the matcher changed: the substring test flags the current names."""
        current = "Opus 5.5 and Sonnet 5.5, `claude-opus-5-5`, Fable 5.1"
        self.assertTrue(any(stale in current for stale, _ in SUPERSEDED))
        self.assertEqual([], self.hits(current))

    def test_older_rows_still_match(self):
        self.assertIn("Opus 4.8", self.hits("Opus 4.8 at high"))
        self.assertIn("claude-opus-4-8", self.hits("`claude-opus-4-8`"))

    def test_the_exemption_covers_only_the_staleness_note(self):
        note = (
            f"{STALENESS_NOTE_MARKER} — re-verify.** Opus 5.5 superseded Opus 5\n"
            "> (`claude-opus-5`), now legacy.\n"
        )
        clean = "| Opus 5.5 (`claude-opus-5-5`) | High |\n\n" + note + "\nAfter the note.\n"
        self.assertEqual([], superseded_offenders("m.md", clean, exempt_note=True))
        for stale in ("Opus 5", "`claude-sonnet-5`"):
            for where in ("before", "after"):
                text = (f"{stale} row\n\n" + note) if where == "before" else (note + f"\n{stale} row\n")
                with self.subTest(stale=stale, where=where):
                    self.assertNotEqual(
                        [], superseded_offenders("m.md", text, exempt_note=True),
                        "a superseded name outside the staleness note must fail the guard",
                    )

    def test_a_missing_note_exempts_nothing(self):
        text = "> Opus 5 is mentioned in some other quote.\n"
        self.assertNotEqual([], superseded_offenders("m.md", text, exempt_note=True))

    def test_the_live_model_selection_file_fails_with_a_stale_tier_row(self):
        """The real file, with one superseded row put back into its tier table."""
        with open(MODEL_SELECTION, encoding="utf-8") as fh:
            text = fh.read()
        self.assertEqual([], superseded_offenders("m.md", text, exempt_note=True))
        stale = text.replace("| Opus 5.5 (`claude-opus-5-5`) |", "| Opus 5 (`claude-opus-5`) |", 1)
        self.assertNotEqual(stale, text, "the tier-table row was not found")
        self.assertNotEqual([], superseded_offenders("m.md", stale, exempt_note=True))


INSTRUCTION = re.compile(r"^\s*- \*\*([a-z]+):\*\* (.+)$", re.M)


def instructions(path):
    """``[(level, instruction)]`` as a file states them, one line each.

    Line-scoped by design (#4): each instruction is written on one line.
    """
    with open(path, encoding="utf-8") as fh:
        return INSTRUCTION.findall(fh.read())


class StageTablesAgree(unittest.TestCase):
    """The operational table and the maintainer reference must not drift."""

    def test_tables_are_identical(self):
        self.assertEqual(
            stage_table(GROUND_RULES),
            stage_table(MODEL_SELECTION),
            "the per-stage effort tables in ground-rules.md and "
            "docs/model-selection.md have drifted — update both",
        )

    def test_every_row_names_one_effort_level_and_nothing_else(self):
        for row in stage_table(GROUND_RULES):
            self.assertEqual(2, len(row), f"{row!r}: a row is a stage and its level")
            stage, level = row
            self.assertTrue(stage, "a stage row has an empty stage name")
            self.assertIn(level, ("medium", "high"), f"{stage!r}: {level!r} is not a level")

    def test_the_instruction_for_each_level_is_identical(self):
        found = instructions(GROUND_RULES)
        self.assertEqual(["medium", "high"], [level for level, _text in found])
        self.assertEqual(found, instructions(MODEL_SELECTION))

    def test_the_table_names_no_model_and_no_command(self):
        """The model column and the CLI column went with the question that used them."""
        for path in (GROUND_RULES, MODEL_SELECTION):
            for row in stage_table(path):
                with self.subTest(path=os.path.basename(path), stage=row[0]):
                    self.assertNotRegex(" | ".join(row), r"(?i)opus|sonnet|fable|haiku|/model|/effort")


class EveryStageHasExactlyOneRecommendation(unittest.TestCase):
    """Total coverage, single-valued cells.

    The guide reads its stage's row at the stage's start and works to that level's
    instruction, so a stage missing from the table has no instruction at all — Entity
    Resolution Concepts was absent this way from the table's earlier form. And a cell
    offering two answers ("high (medium if no bespoke load code)") names a condition the
    guide cannot resolve at the stage's start.
    """

    def setUp(self):
        self.rows = stage_table(GROUND_RULES)
        self.stages = [stage for stage, _ in self.rows]

    def test_every_canonical_module_has_a_row(self):
        # Parsed from bootcamp-preparation's module table — the one place display
        # names are canonical (INV-079) — so adding a module fails this until it
        # is rated.
        prep = os.path.join(PLUGIN, "skills", "bootcamp-preparation", "SKILL.md")
        with open(prep, encoding="utf-8") as fh:
            canonical = [
                m.group(1).strip()
                for m in re.finditer(
                    r"^\|\s*\d+\s*\|\s*([^|]+?)\s*\|\s*[^|]+?\s*\|\s*`[a-z_]+`", fh.read(), re.M
                )
            ]
        self.assertTrue(canonical, "could not parse the canonical module table")
        missing = [name for name in canonical if name not in self.stages]
        self.assertEqual(
            [],
            missing,
            f"module(s) with no effort row: {missing}. Every stage the bootcamp "
            "can run needs one, including apparatus-exempt stages, so the guide "
            "always has an instruction to work to.",
        )

    def test_no_stage_has_two_rows(self):
        doubled = sorted({stage for stage in self.stages if self.stages.count(stage) > 1})
        self.assertEqual([], doubled, f"stage(s) with more than one row: {doubled}")

    def test_onboarding_is_rated_too(self):
        """Not in the prep table, but it is a stage the bootcamp runs."""
        self.assertIn("Onboarding", self.stages)

    def test_no_row_offers_a_conditional_level(self):
        offenders = [
            f"{stage}: {level!r}"
            for stage, level in self.rows
            if "(" in level or re.search(r"\bif\b|\bor\b", level)
        ]
        self.assertEqual(
            [],
            offenders,
            f"conditional level(s): {offenders}. A row must name exactly one "
            "level — the guide cannot resolve a condition at the stage's start.",
        )

    def test_one_stage_per_row(self):
        """Grouped rows hid the sequence; the order is now readable down the column."""
        offenders = [stage for stage in self.stages if ";" in stage]
        self.assertEqual(
            [], offenders, f"row(s) still group several stages: {offenders}"
        )


class StalenessNotePresent(unittest.TestCase):
    """Point-in-time data must say so, with the date it was checked."""

    def test_note_carries_a_verification_date(self):
        with open(MODEL_SELECTION, encoding="utf-8") as fh:
            text = fh.read()
        self.assertRegex(
            text,
            r"last verified \d{4}-\d{2}-\d{2}",
            "docs/model-selection.md must carry a dated 'last verified' note",
        )


if __name__ == "__main__":
    unittest.main()
