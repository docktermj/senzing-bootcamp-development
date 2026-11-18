"""The packaging flow's consent rules ship: measure, then ask, then write.

An archive is a distribution channel, so what the Bootcamper consents to is precisely **which of
their files travel**. Two rules make that consent informed, and both were shipped on 2026-08-26
with no invariant covering them:

- ⛔ **Run the dry run first. The question quotes a measured size, never an estimate.**
- ⛔ **Option 3 writes nothing at all.**

⚠️ **They were not overlooked; they were mis-accounted.** The implementing run followed
`implement-spec` Step 5's deferral path and pointed at the spec's pre-existing drafted invariant —
which covers the archive's *contents* and *verification* and was written **before the
conversational layer existed**, so it is silent on the gate. `production-readiness-audit-2026-08-26`
found it by reading all 36 hard-rule lines that run added. The lesson, worth more than the fix: a
deferral written against a draft inherits the draft's blind spots, so it must be written against
the diff.

⛔ **What this guard CANNOT check, said plainly rather than implied away.** Whether a given run
actually measures before asking, asks exactly once, and writes nothing on cancel is a property of
the conversation, not of the files. No static test reaches it — `dry-run` phase 3 owns it. What is
asserted here is that the rules **ship**, in the flow and in the command, and that the script they
depend on genuinely supports measuring without writing (which *is* testable, and is tested in
`tests/test_package_bootcamp.py`).

Issue #46 added the last three classes: option 2 of the pinned question names the saved
bootcamp feedback and the in-progress recap, which only `transfer` carries, and Step 4 and the
command say which profile carries them and state the packager's link and UTF-16 behavior.
They read the shipped wording; what the script does is tested in
`tests/test_package_bootcamp.py`, where the rule is stated.

Stdlib only; shipped markdown read as text (INV-108).

Source spec: `specs/the-packaging-consent-gate-is-an-unregistered-guarantee.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "source"
FLOW = PLUGIN / "skills" / "bootcamp-onboarding" / "packaging.md"
COMMAND = PLUGIN / "commands" / "package-bootcamp.md"
# One-repository migration, 2026-11-14: `TheDraftedInvariantCoversTheGate` (five cases) was
# retired with its `SPEC` path; it read the archived spec
# `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`, which is not carried here.


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class Base(unittest.TestCase):
    def has(self, text, pattern, msg):
        self.assertTrue(re.search(pattern, text), msg)


class TheMeasureBeforeAskingRuleShips(Base):
    def setUp(self):
        self.text = flat(FLOW)

    def test_the_dry_run_precedes_the_question(self):
        self.has(self.text, r"(?i)Run the dry run first",
                 "the flow does not require the dry run before the question, so the consent "
                 "question can quote a number nobody measured")

    def test_it_forbids_an_estimate_explicitly(self):
        self.has(self.text, r"(?i)quotes a measured size, never an estimate",
                 "the flow does not forbid an estimated size; 'run the dry run' alone permits "
                 "asking with a guessed figure anyway")

    def test_the_dry_run_is_stated_to_write_nothing(self):
        self.has(self.text, r"(?i)\*\*writes nothing\*\*|writes \*\*nothing\*\*",
                 "the flow does not say the dry run writes nothing, so a reader cannot tell it "
                 "is safe to run before consent")

    def test_the_question_comes_before_any_write(self):
        """Ordering, as far as file order can carry it: the ask precedes the write step."""
        raw = FLOW.read_text(encoding="utf-8")
        ask = raw.index("👉 **What should the package contain?")
        write = raw.index("## Step 4: Write it")
        measure = raw.index("Run the dry run first")
        self.assertLess(measure, ask, "the dry-run step is documented after the question")
        self.assertLess(ask, write, "the question is documented after the write step")


class TheCancelOptionWritesNothing(Base):
    def setUp(self):
        self.text = flat(FLOW)

    def test_a_cancel_option_exists(self):
        self.has(self.text, r"(?i)3\.\s*\*\*Cancel",
                 "the consent question has no cancel option, so a bootcamper who wants neither "
                 "profile has no answer that declines")

    def test_cancel_is_stated_to_write_nothing(self):
        self.has(self.text, r"(?i)Option 3 writes nothing at all",
                 "the flow does not state that cancel writes nothing, which is the half a "
                 "reader cannot infer from the option label")


class TheQuestionIsSingularPinnedAndNumbered(Base):
    """INV-051/INV-056/INV-251 — one pinned, numbered question."""

    def setUp(self):
        self.raw = FLOW.read_text(encoding="utf-8")

    def test_exactly_one_question_is_asked(self):
        """Counts questions, not marker occurrences.

        ⚠️ A bare `.count("👉")` reads 2 here, and the second is the trigger paragraph's prose
        reference to "one 👉 question per yielding turn (INV-251)" -- a citation of the rule,
        not a question. INV-251 governs questions asked; only a marker that OPENS a line is one.
        Line-scoped by design for that reason (#424): a question opens on one line however it
        wraps after that.
        """
        asked = [line for line in self.raw.splitlines() if line.lstrip().startswith("👉")]
        self.assertEqual(
            1, len(asked),
            "the packaging flow asks %d questions; it must ask exactly one (INV-251): %r"
            % (len(asked), [a[:60] for a in asked]),
        )

    def test_the_question_is_numbered(self):
        self.has(" ".join(self.raw.split()), r"(?i)Reply with a number",
                 "the question does not ask for a numbered reply")
        for option in ("1. ", "2. ", "3. "):
            with self.subTest(option=option):
                self.assertIn(option, self.raw)

    def test_it_is_marked_pinned_verbatim(self):
        self.has(" ".join(self.raw.split()), r"(?i)Pin this verbatim \(INV-051/INV-056\)",
                 "the question is not marked pinned-verbatim, so its wording may be improvised "
                 "and the size figures rephrased away")


class TheCommandDoesNotLetAnArgumentStandInForConsent(Base):
    """An argument names a profile; it does not consent to what the archive carries."""

    def test_the_command_still_requires_the_dry_run_and_the_question(self):
        text = flat(COMMAND)
        self.has(text, r"(?i)still run the dry run and still ask the question",
                 "the command lets a profile argument skip the gate; the size and the "
                 "exclusions are what the bootcamper is consenting to")


def between(text, start, end):
    """`text` from `start` up to `end`; a missing anchor is a failure, never an empty read."""
    begin = text.index(start)
    return text[begin:text.index(end, begin + len(start))]


class OptionTwoNamesWhatOnlyTransferCarries(Base):
    """#46 — option 2 names the saved feedback and the in-progress recap; nothing else moved."""

    OPTION_1 = (
        "1. **Results to share** — your recap PDF, keepsake documents, visualizations, the "
        "exports written for the systems you named (`data/exports/`) and your `production/` "
        "project (~<n> MB). No database, no source data, no credentials.")
    OPTION_2 = (
        "2. **Everything to continue elsewhere** — the above plus your database backup, saved "
        "bootcamp feedback, in-progress recap, config and mappings, so you can pick the bootcamp "
        "back up on another machine (~<n> MB{, which excludes your database backup — choosing "
        "this creates it, and it is the largest part}).")
    #: Option 2's last two physical lines. `tests/test_quoted_sizes_say_what_they_missed.py`
    #: anchors three controls on them, so they stay byte for byte.
    LAST_TWO_LINES = (
        "\n   and mappings, so you can pick the bootcamp back up on another machine (~<n> MB{, "
        "which\n   excludes your database backup — choosing this creates it, and it is the "
        "largest part}).\n3. **Cancel.**\n")

    def setUp(self):
        self.raw = FLOW.read_text(encoding="utf-8")
        self.text = flat(FLOW)

    def test_option_2_reads_as_the_issue_gives_it(self):
        self.assertEqual(self.OPTION_2,
                         between(self.text, "2. **Everything to continue", " 3. **Cancel.**"))

    def test_the_two_new_items_come_before_config(self):
        option = between(self.text, "2. **Everything to continue", " 3. **Cancel.**")
        self.assertLess(option.index("saved bootcamp feedback"), option.index("in-progress recap"))
        self.assertLess(option.index("in-progress recap"), option.index("config"))

    def test_its_last_two_physical_lines_are_unchanged(self):
        self.assertEqual(1, self.raw.count(self.LAST_TWO_LINES))

    def test_options_1_and_3_are_unchanged(self):
        self.assertEqual(self.OPTION_1,
                         between(self.text, "1. **Results to share**", " 2. **Everything"))
        self.assertIn(" 3. **Cancel.** ", self.text)


class TheGuaranteeListStatesWhatTheScriptNowDoes(Base):
    """#46 — Step 4 says which profile carries the two paths, and states the link and UTF-16
    behavior. What the script does is tested in `tests/test_package_bootcamp.py`."""

    def setUp(self):
        self.step = between(flat(FLOW), "## Step 4: Write it", "## Step 5:")

    def test_the_two_paths_are_dropped_by_share_and_carried_by_transfer(self):
        bullet = between(self.step, "**Never packaged on `share`, on top of that:**",
                         "- **Content-scanned")
        for path in ("`docs/feedback/`", "`docs/progress/`"):
            with self.subTest(path=path):
                self.assertIn(path, bullet)
        self.has(bullet, r"`transfer` carries those last two",
                 "Step 4 does not say that `transfer` carries the two paths `share` drops")

    def test_a_symlinked_directory_is_never_followed_and_is_named(self):
        bullet = between(self.step, "- **Symlinks resolved, then compared:**",
                         "- **Verified before it is announced:**")
        self.has(bullet, r"A symlinked directory is never followed",
                 "Step 4 does not say a symlinked directory is never followed")
        self.has(bullet, r"the manifest names it as a symlinked directory that was not followed",
                 "Step 4 does not say the manifest names a symlinked directory")

    def test_a_symlinked_file_is_checked_by_its_resolved_path(self):
        bullet = between(self.step, "- **Symlinks resolved, then compared:**",
                         "- **Verified before it is announced:**")
        self.has(bullet, r"A symlinked file .* is also checked against the exclusion rules by "
                         r"the path it resolves to",
                 "Step 4 does not say a symlinked file is checked by its resolved path")

    def test_the_content_scan_reads_utf16_text(self):
        bullet = between(self.step, "- **Content-scanned, every member",
                         "- **Symlinks resolved, then compared:**")
        self.has(bullet, r"as UTF-16 text, little-endian and big-endian, with or without a "
                         r"byte-order mark",
                 "Step 4 does not say the content scan reads UTF-16 text")


class TheCommandSaysWhichProfileCarriesTheWorkingNotes(Base):
    def test_the_profile_summary_names_both_paths(self):
        text = flat(COMMAND)
        summary = between(text, "Two profiles:", "If this command was invoked")
        self.has(summary, r"`docs/feedback/`\) and the in-progress recap \(`docs/progress/`\) are "
                          r"dropped by `share` and carried by `transfer`",
                 "the command's profile summary does not say which profile carries the saved "
                 "feedback and the in-progress recap")


if __name__ == "__main__":
    unittest.main()
