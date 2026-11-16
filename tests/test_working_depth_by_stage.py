"""Effort follows the task by instruction: one level per stage, one instruction per level (#4).

The bootcamp used to recommend a model and a reasoning effort per stage and ask the
bootcamper to set them. Issue #4 replaced that with an instruction to the guide:
`ground-rules.md` → "Working depth by stage" gives every stage one effort level, and gives
each level one fixed instruction about how carefully to work. The guide applies it silently
and changes no setting. This file replaces `test_model_effort_nudge_edges.py`, which pinned
the edges of the retired question.

What must hold:

1. **Every stage has exactly one row.** The stages are derived, not listed here: the
   canonical module table in Bootcamp preparation (INV-079) plus Onboarding, which runs
   before that table applies. Adding a module fails this until it has a level (INV-246).
2. **Every row has exactly one level,** and the levels are the ones issue #4 settled.
3. **Every level maps to exactly one instruction,** and no instruction is left for a level
   no stage uses.
4. **The guide applies it silently and changes no setting.** The block says so, and the
   module-start reminder points at the instruction without asking for anything.
5. **Every assistant gets the same bytes.** The block is identical in all five packages and
   names no assistant, no model and no control.

⚠️ **What this cannot establish:** that a guide works more carefully on a `high` stage. An
instruction is guidance; whether it changes the work is observable only in a live run.

Line-scoped by design (#4): a Markdown table row is one line, and each instruction is
written on one line so that it is the same bytes wherever it appears.

Run:  python3 -m unittest discover -s tests
"""
import re
import sys
import unittest

from _built import REPO_ROOT, built
from _model_effort import (GROUND_RULES, HOSTS, capable_model, depth_block, depth_instructions,
                           depth_rows, flat, skill_text)

#: The levels issue #4 settled, stage by stage, in the order the bootcamp runs them.
SETTLED = (
    ("Onboarding", "medium"),
    ("Bootcamp preparation", "medium"),
    ("Entity Resolution Concepts", "medium"),
    ("Discover the Business Problem", "medium"),
    ("SDK setup", "high"),
    ("System verification", "high"),
    ("Truth Set visualization", "high"),
    ("Data collection", "medium"),
    ("Data Quality, Mapping, and Transformation", "high"),
    ("Data processing", "high"),
    ("Query, Visualize and Discover", "high"),
    ("Bootcamp graduation", "high"),
)

#: The one instruction each level stands for.
INSTRUCTIONS = {
    "medium": "Move briskly: work from what the step and the Senzing MCP server give you, "
              "and do not re-derive what is already settled.",
    "high": "Work carefully: before you write code or state a result, check it against the "
            "MCP server's answer and the bootcamper's own files, and re-read the step's rules "
            "before each action.",
}

#: A row of Bootcamp preparation's module table: number, display name, kind, state token.
CANONICAL_MODULE = re.compile(r"^\|\s*\d+\s*\|\s*([^|]+?)\s*\|\s*[^|]+?\s*\|\s*`[a-z_]+`", re.M)


def block(host="claude"):
    return depth_block(skill_text(host, GROUND_RULES))


def canonical_stages(host="claude"):
    """Every stage the bootcamp can run: Onboarding, then Bootcamp preparation's table."""
    modules = CANONICAL_MODULE.findall(skill_text(host, "bootcamp-preparation/SKILL.md"))
    return ["Onboarding"] + [name.strip() for name in modules]


class EveryStageHasExactlyOneRow(unittest.TestCase):
    def test_the_canonical_stages_are_found(self):
        stages = canonical_stages()
        self.assertGreaterEqual(len(stages), 12, "the canonical module table was not parsed")
        self.assertIn("Bootcamp graduation", stages)

    def test_each_stage_the_bootcamp_can_run_has_one_row(self):
        rows = [stage for stage, _level in depth_rows(block())]
        for stage in canonical_stages():
            with self.subTest(stage=stage):
                self.assertEqual(1, rows.count(stage),
                                 "%r has %d rows in the working-depth table; every stage the "
                                 "bootcamp can run has exactly one" % (stage, rows.count(stage)))

    def test_no_row_is_for_a_stage_the_bootcamp_cannot_run(self):
        extra = [stage for stage, _level in depth_rows(block()) if stage not in canonical_stages()]
        self.assertEqual([], extra)

    def test_the_rows_are_in_the_order_the_bootcamp_runs_them(self):
        self.assertEqual(canonical_stages(), [stage for stage, _level in depth_rows(block())])

    def test_a_missing_and_a_doubled_row_are_both_seen(self):
        """Negative controls (INV-265), on the shipped block with one row changed."""
        text = block()
        row = "  | Data collection | medium |\n"
        self.assertIn(row, text)
        without = [stage for stage, _level in depth_rows(text.replace(row, ""))]
        self.assertEqual(0, without.count("Data collection"))
        doubled = [stage for stage, _level in depth_rows(text.replace(row, row + row))]
        self.assertEqual(2, doubled.count("Data collection"))


class EveryRowHasExactlyOneLevel(unittest.TestCase):
    def test_the_levels_are_the_ones_settled(self):
        self.assertEqual(list(SETTLED), depth_rows(block()))

    def test_no_row_is_conditional_or_names_a_model(self):
        for stage, level in depth_rows(block()):
            with self.subTest(stage=stage):
                self.assertRegex(level, r"\A[a-z]+\Z",
                                 "a level is one word: a conditional or two-part cell gives "
                                 "the guide two answers at the stage's start")

    def test_the_table_has_two_columns(self):
        self.assertIn("  | Stage | Effort |\n  |---|---|\n", block())


class EveryLevelMapsToExactlyOneInstruction(unittest.TestCase):
    def test_each_level_in_use_has_one_instruction(self):
        instructions = depth_instructions(block())
        levels = [level for level, _text in instructions]
        for level in sorted({level for _stage, level in depth_rows(block())}):
            with self.subTest(level=level):
                self.assertEqual(1, levels.count(level))

    def test_no_instruction_is_for_a_level_no_stage_uses(self):
        used = {level for _stage, level in depth_rows(block())}
        self.assertEqual(used, {level for level, _text in depth_instructions(block())})

    def test_the_instructions_are_the_ones_settled(self):
        self.assertEqual(INSTRUCTIONS, dict(depth_instructions(block())))

    def test_two_levels_do_not_share_an_instruction(self):
        texts = [text for _level, text in depth_instructions(block())]
        self.assertEqual(len(texts), len(set(texts)))


class TheGuideAppliesItSilentlyAndChangesNoSetting(unittest.TestCase):
    def setUp(self):
        self.flat = flat(block())

    def test_it_is_never_shown_or_mentioned(self):
        self.assertIn("⛔ **Apply the instruction silently.** Never show the bootcamper this "
                      "table, a level or an instruction, and never say that a stage has one.",
                      self.flat)

    def test_it_changes_no_setting(self):
        self.assertIn("⛔ **It changes no setting.**", self.flat)
        self.assertIn("Do not change the model or the reasoning effort, do not ask the "
                      "bootcamper to change either, and say nothing to them about what they "
                      "are running.", self.flat)
        self.assertIn("Nothing the bootcamp ships sets either one: no skill or agent "
                      "frontmatter, no hook and no settings file.", self.flat)

    def test_an_automatic_mode_is_neither_detected_nor_mentioned(self):
        self.assertIn("the bootcamp neither detects that nor mentions it", self.flat)

    def test_the_block_holds_no_question(self):
        self.assertNotIn("👉", block())

    def test_the_module_start_reminder_points_at_it_and_asks_nothing(self):
        scripts = built("claude") / "scripts"
        sys.path.insert(0, str(scripts))
        try:
            import module_start_apparatus
        finally:
            sys.path.remove(str(scripts))
        for module in ("SDK setup", "graduation"):
            with self.subTest(module=module):
                reminder = module_start_apparatus.reminder(module)
                self.assertIn("work to its working-depth instruction", reminder)
                self.assertIn("without showing or mentioning it", reminder)
                self.assertIn("ask and say nothing about the model or the reasoning effort",
                              reminder)
                self.assertNotRegex(reminder, r"(?i)nudge|recommended model|currently running")


class EveryAssistantGetsTheSameBytes(unittest.TestCase):
    def test_the_block_is_identical_in_every_package(self):
        reference = block("claude").encode("utf-8")
        self.assertGreater(len(reference), 1500, "the block collapsed to a stub")
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual(reference, block(host).encode("utf-8"))

    def test_the_block_names_no_assistant_model_or_control(self):
        text = block()
        source = depth_block((REPO_ROOT / "source" / "skills" / GROUND_RULES).read_text(encoding="utf-8"))
        self.assertNotIn("{{", source, "a host token would render differently per assistant")
        self.assertNotIn("<!-- host:", source)
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertNotIn(capable_model(host), text)

    def test_the_source_block_is_what_every_package_carries(self):
        source = depth_block((REPO_ROOT / "source" / "skills" / GROUND_RULES).read_text(encoding="utf-8"))
        self.assertEqual(source, block("claude"))

    def test_no_fragment_carries_a_per_assistant_copy(self):
        """The two `model-guidance` fragments are gone, and nothing includes one."""
        self.assertEqual([], sorted(str(path.relative_to(REPO_ROOT))
                                    for path in (REPO_ROOT / "hosts").rglob("model-guidance*")))
        for path in sorted((REPO_ROOT / "source").rglob("*.md")):
            with self.subTest(path=path.name):
                self.assertNotIn("host:include model-guidance", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
