"""The bootcamp never asks the bootcamper to change the model or the effort (#4).

**This design has now swung six times**, every swing a deliberate decision:

| | Behavior |
|---|---|
| INV-062 | non-blocking suggestion |
| INV-063 | blocking switch question when the recommendation changes |
| INV-069 | plus a second confirmation gate |
| INV-119/INV-120 | all of it conditional on an `advisory`/`off`/`prompt` preference |
| INV-137 | unconditional again; the preference and its question retired |
| 2026-07-26 | the trigger becomes the Bootcamper's *current setting*, not the previous stage |
| **#4, 2026-11-16** | no request at all: one model named once in the welcome, effort by instruction |

So the risk this file guards is specific and has materialized before: a future edit
quietly reinstating one of the retired shapes, or a stale `model_guidance` read
surviving in a file nobody thought to check. What must hold now, in **every** assistant's
built package:

1. No file carries a request to change the model or the effort: not the switch question,
   not the "Are you done modifying the model and effort?" gate, not a 👉 question about
   either, not a slash command or a control that sets either, and not the module-start
   nudge under any name it had.
2. No module's opening line and no module-start reminder lists a model or effort item.
3. The `model_guidance` capture question exists **nowhere**, and no shipped skill instructs
   the guide to read, honor or persist `model_guidance` (the part of INV-137 that still
   binds).

⚠️ **What a diagnostic mention is, and why it passes.** `feedback.md` records the model and
the reasoning effort in a feedback file's context, and graduation calls them diagnostic.
Neither asks the bootcamper for anything, and no pattern here matches them; the must-not-flag
cases below pin that.

⚠️ **What this cannot establish:** that a live guide, reading these files, asks nothing. That
is a conversational outcome and belongs to `/dry-run` phase 3 and `transcript_lint.py`'s
`check_model_effort_requests`.

The registered wording of INV-063, INV-064, INV-069, INV-098, INV-138, INV-139 and INV-236
describes the retired nudge; `specs/INVARIANTS.md` is superseded separately and is not read
here.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

from _wrapped_text import match_lines
from _built import built  # one assistant's package, built from source/
from _model_effort import HOSTS, package_texts, requests_in, skill_text, skills_dir

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(str(built("claude")))
PREPARATION = os.path.join(PLUGIN, "skills", "bootcamp-preparation", "SKILL.md")

QUESTION = "How would you like model guidance handled?"

# Phrasings that would mean a file is treating the retired preference as live.
#: ⚠️ A verb negated just before it ("do not honor", "never read") forbids the use rather
#: than instructing it, so it is not matched. Found by the #424 conversion: Bootcamp
#: preparation's retirement note says "do not honor a\nstale `model_guidance` key", which a
#: line-at-a-time read never saw and a wrap-aware read flagged (INV-282: fix the matcher).
LIVE_PREFERENCE_USE = re.compile(
    r"(?<!not )(?<!NOT )(?<!not\*\* )(?<!never )(?<!Never )"
    r"(Read|read|honou?r|Honou?r|persist|Persist|carry)\s+[^.\n]{0,40}`model_guidance`"
    r"|`model_guidance`[^.\n]{0,30}(from|to)\s+`config/bootcamp_preferences\.yaml`",
)

# Mode-gated phrasings retired by INV-137.
RETIRED_MODE_PHRASINGS = (
    "belongs to `prompt` alone",
    "Under `advisory`",
    "treat as `advisory`",
    "`advisory` (the default)",
    "absent-means-`advisory`",
    "The three modes",
)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def phrase_lines(text, phrase):
    """1-based lines where the literal ``phrase`` starts, matched across line wraps (#424).

    A retired phrase searched in the raw text, or one line at a time, passes once a line
    break falls inside it; ``match_lines`` reads each Markdown block with whitespace collapsed.
    """
    return match_lines(text, re.compile(re.escape(phrase)))


def flat(path):
    """`read`, with runs of whitespace collapsed to single spaces.

    These files are wrapped prose. A phrase assertion against the raw text is
    really an assertion about where the line breaks fall, so re-flowing a
    paragraph — an edit with no meaning — fails it. Use this for any check about
    what a file *says*; use `read` only when layout genuinely matters.
    """
    return re.sub(r"\s+", " ", read(path))


def shipped_markdown():
    for dirpath, dirnames, filenames in os.walk(PLUGIN):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def skill_markdown():
    root = os.path.join(PLUGIN, "skills")
    return [p for p in shipped_markdown() if os.path.abspath(p).startswith(os.path.abspath(root))]


class TestTheQuestionIsGone(unittest.TestCase):

    def test_no_shipped_file_asks_it(self):
        offenders = [
            os.path.relpath(p, REPO_ROOT) for p in shipped_markdown()
            if phrase_lines(read(p), QUESTION)
        ]
        self.assertEqual(
            [],
            offenders,
            f"the retired model-guidance question is asked in: {offenders}. INV-137 "
            "removes it entirely — the choice is not the Bootcamper's to make.",
        )

    def test_preparation_records_that_it_is_retired(self):
        """A note in its place, so a future edit does not silently re-add it."""
        text = read(PREPARATION)
        self.assertRegex(
            text,
            r"no `model_guidance` preference|model[- ]guidance question.{0,40}retired"
            r"|retired.{0,60}model.guidance",
            "Bootcamp preparation should state that the question is retired, so the "
            "absence is deliberate rather than looking like an omission.",
        )

    def test_the_consolidated_write_does_not_persist_it(self):
        text = read(PREPARATION)
        write_step = text[text.index("## 6.") : text.index("## 7.")]
        self.assertNotRegex(
            write_step,
            r"`model_guidance`\s*\(",
            "Step 6 must not persist model_guidance — the key is retired (INV-137)",
        )


class TestNoFileTreatsThePreferenceAsLive(unittest.TestCase):

    def test_no_skill_reads_or_honors_it(self):
        offenders = []
        for path in skill_markdown():
            for n in match_lines(read(path), LIVE_PREFERENCE_USE):
                offenders.append(f"{os.path.relpath(path, REPO_ROOT)}:{n}")
        self.assertEqual(
            [],
            offenders,
            f"file(s) still instruct reading/honoring `model_guidance`: {offenders}. "
            "INV-137 retires the key; a stale value must not be honored.",
        )

    def test_no_retired_mode_phrasing_survives(self):
        offenders = []
        for path in shipped_markdown():
            text = read(path)
            for phrase in RETIRED_MODE_PHRASINGS:
                for n in phrase_lines(text, phrase):
                    offenders.append(f"{os.path.relpath(path, REPO_ROOT)}:{n}: {phrase!r}")
        self.assertEqual(
            [],
            offenders,
            f"mode-gated phrasing retired by INV-137 survives: {offenders}",
        )

    def test_each_retired_phrasing_is_caught_when_wrapped(self):
        """Negative controls (#424): each phrase split across two lines is still found."""
        cases = (
            (LIVE_PREFERENCE_USE, "Before the module starts, read the\n`model_guidance` key.\n"),
            (re.compile(re.escape(QUESTION)), "Ask: How would you like model\nguidance handled?\n"),
            (re.compile(re.escape("Under `advisory`")), "Under\n`advisory`, offer the switch.\n"),
        )
        for pattern, wrapped in cases:
            with self.subTest(pattern=pattern.pattern[:30]):
                self.assertEqual([1], match_lines(wrapped, pattern))
                # The old line-at-a-time read, kept only to show the fixture is the hard case.
                self.assertFalse(any(pattern.search(l) for l in wrapped.split("\n")))

    def test_a_retirement_note_is_not_a_live_read(self):
        """Must-not-flag (INV-282): saying the key is retired, or forbidding its use, reads
        nothing. The second case is Bootcamp preparation's own note, wrapped as it ships."""
        for text in ("There is no `model_guidance` preference any more; the key is retired\n"
                     "(INV-137).\n",
                     "Do **not** reintroduce the question, and do not honor a\n"
                     "stale `model_guidance` key left in an old preferences file.\n",
                     "Never read `model_guidance` from an old file.\n"):
            with self.subTest(text=text[:40]):
                self.assertEqual([], match_lines(text, LIVE_PREFERENCE_USE))

    def test_no_file_counts_it_among_the_capture_questions(self):
        """Preparation's Step 0 said the preferences rule covers all capture questions,
        "not just model guidance", as though that were still one of them (#234).

        Matched on flattened text, so a line break inside the phrase cannot hide it.
        Negative-controlled by restoring the phrase to bootcamp-preparation/SKILL.md.
        """
        offenders = [
            os.path.relpath(p, REPO_ROOT) for p in shipped_markdown()
            if re.search(r"(?i)not just model guidance", flat(p))
        ]
        self.assertEqual(
            [],
            offenders,
            f"these files count model guidance among the capture questions: {offenders}. "
            "INV-137 retires the question, so no preference rule is scoped against it.",
        )


class TestNoPackageAsksForAModelOrEffortChange(unittest.TestCase):
    """Issue #4, criterion 1: no request, ever, on any assistant."""

    def test_every_package_is_scanned_and_not_empty(self):
        """INV-265: the scan reads real files that could carry a request."""
        for host in HOSTS:
            with self.subTest(host=host):
                names = [name for name, _text in package_texts(host)]
                self.assertGreater(len(names), 40, "far fewer text files than a package holds")
                self.assertTrue(any(name.endswith("ground-rules.md") for name in names))
                self.assertTrue(any(name.endswith("graduation/SKILL.md") for name in names))

    def test_no_file_in_any_package_carries_a_request(self):
        offenders = []
        for host in HOSTS:
            for name, text in package_texts(host):
                offenders += ["%s: %s: %s" % (host, name, found) for found in requests_in(text)]
        self.assertEqual(
            [], offenders,
            "a built package asks the bootcamper to change the model or the effort. The "
            "bootcamp never does (#4):\n  " + "\n  ".join(offenders))

    def test_no_module_opening_lists_a_model_or_effort_item(self):
        """Every content module's **First:** line names its module-start output."""
        opened = 0
        for host in HOSTS:
            for skill in sorted(skills_dir(host).glob("*/SKILL.md")):
                collapsed = " ".join(skill.read_text(encoding="utf-8").split())
                first = re.search(r"\*\*First:\*\* .{0,400}?before any module work", collapsed)
                if not first:
                    continue
                opened += 1
                with self.subTest(host=host, skill=skill.parent.name):
                    self.assertIn("estimated time-to-complete", first.group(0))
                    self.assertNotRegex(first.group(0), r"(?i)\bmodel\b|\beffort\b|nudge")
        self.assertGreaterEqual(opened, 8 * len(HOSTS), "the **First:** lines were not found")

    def test_the_transition_runs_straight_into_step_1(self):
        """No switch turn and no gate sit between a module's opening and its first step."""
        for host in HOSTS:
            with self.subTest(host=host):
                collapsed = " ".join(skill_text(host, "bootcamp-onboarding/ground-rules.md").split())
                self.assertIn(
                    "banner + journey map + before/after + step overview + estimated time to "
                    "complete, then continue straight into Step 1 the same turn", collapsed)

    def test_graduation_and_preparation_ask_nothing(self):
        for host in HOSTS:
            graduation = " ".join(skill_text(host, "graduation/SKILL.md").split())
            preparation = " ".join(skill_text(host, "bootcamp-preparation/SKILL.md").split())
            with self.subTest(host=host):
                self.assertIn("Graduation asks nothing about the model or the reasoning effort, "
                              "and says nothing about them", graduation)
                self.assertIn("The bootcamp never asks the bootcamper to change the model or the "
                              "reasoning effort", preparation)

    def test_the_ground_rules_state_the_rule_and_name_no_exception(self):
        for host in HOSTS:
            with self.subTest(host=host):
                collapsed = " ".join(skill_text(host, "bootcamp-onboarding/ground-rules.md").split())
                self.assertIn("Never ask the bootcamper to change either one", collapsed)
                self.assertIn("Never change either one yourself", collapsed)
                self.assertIn("**There is no exception:**", collapsed)
                self.assertNotRegex(collapsed, r"(?i)the single exception|the only [\w-]+ control")


class TestTheRequestScanIsNotVacuous(unittest.TestCase):
    """Negative controls: each retired shape is reported, wrapped or not."""

    RETIRED = (
        "👉 **Would you like to switch to `/model {model}` + `/effort {effort}` for this module?**",
        "👉 **Would you like to switch to {Model} at {effort} reasoning effort for\n"
        "graduation?** (Recommended for best value.)",
        "👉 **Are you done modifying the model and\neffort?** (Reply yes.)",
        "Run `/effort high` before the next step.",
        "set it with the model and effort controls in your interface",
        "Use the model picker to choose a stronger model.",
        "and the recommended model/effort nudge, before any module work.",
        "👉 **Which model would you like for this module?**",
    )
    ALLOWED = (
        "- **Model and effort:** the model name/ID and the reasoning-effort level in use.",
        '- **Model / effort:** [model ID and reasoning-effort level; e.g. "x / high", or "Unknown"]',
        "OS/architecture, plugin version, and model/effort are diagnostic context.",
        "One model is fine for the whole bootcamp: Opus 5.5 suits it well, and the bootcamp\n"
        "never asks you to switch models or change settings along the way.",
        "Never ask the bootcamper to change either one: no 👉 question, no gate.",
        "See `../../docs/model-selection.md`.",
        "👉 **Would you like to switch to SQLite?**",
        "| **Entity Graph** | `/api/graph`, `/api/records` | a **mode** toggle |",
    )

    def test_every_retired_shape_is_reported(self):
        for text in self.RETIRED:
            with self.subTest(text=text[:50]):
                self.assertTrue(requests_in(text), "not reported: %r" % text)

    def test_a_diagnostic_mention_and_a_prohibition_are_not(self):
        for text in self.ALLOWED:
            with self.subTest(text=text[:50]):
                self.assertEqual([], requests_in(text))


if __name__ == "__main__":
    unittest.main()
