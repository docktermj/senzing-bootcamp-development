"""The model notes and every assistant's site tips name no mid-bootcamp switch (#4).

Two places outside the skills told a reader that the bootcamp would ask for a model or
effort change along the way: the maintainer notes in `docs/model-selection.md` (a page in this
repository that no package carries, #12), and
the "Model and effort" tip on each assistant's install page
(`hosts/<assistant>/fragments/site-tips.html`). Issue #4 removed the request, so both now
say what the welcome says: one model is fine for the whole bootcamp, and the bootcamp never
asks for a change. A page that still promised a switch would describe a bootcamp that no
longer exists.

What must hold:

1. Each assistant's tip states the one-model rule, names that assistant's capable-tier model
   and says the bootcamp never asks for a switch.
2. No tip and no install fragment says the bootcamp suggests, recommends or announces a
   model or effort change at a module start, or tells the reader how to make one mid-way.
3. `model-selection.md` states the same rule, names no switch and no command that sets the
   model or the effort, and keeps one derived copy of the working-depth table.
4. The Claude install walkthrough starts the reader on the model the welcome names.

⚠️ **Choosing a model once, before the bootcamp starts, is not a switch.** The install
fragments that name a model or an effort to start on are not reported for that.

HTML is read as visible text: tags removed and whitespace collapsed, so a re-wrapped
paragraph still matches.

Run:  python3 -m unittest discover -s tests
"""
import html
import re
import unittest

from _built import REPO_ROOT
from _model_effort import HOSTS, capable_model, depth_block, depth_instructions, depth_rows, flat, skill_text

HOSTS_DIR = REPO_ROOT / "hosts"
MODEL_SELECTION = REPO_ROOT / "docs" / "model-selection.md"

RULE = "One model is fine for the whole bootcamp."
NEVER = "The bootcamp never asks you to switch models or change settings along the way."

#: Wording that describes a model or effort change made during the bootcamp.
MID_BOOTCAMP_SWITCH = re.compile(
    r"(?i)at the start of each module"
    r"|\b(?:tells you when|may suggest|suggests|recommends)\b"
    r"|\bswitch(?:es|ing)? (?:to|up|down|back|mid|the session)\b"
    r"|\bmid-(?:session|bootcamp|module)\b"
    r"|\bonly you can change\b"
    r"|\badapts its model\b"
    r"|(?<![\w./-])/(?:model|effort)(?![\w-])")


def visible(path):
    """An HTML fragment's text as a reader sees it."""
    return flat(html.unescape(re.sub(r"<[^>]+>", " ", path.read_text(encoding="utf-8"))))


def tip(host):
    """The text of ``host``'s model tip: the block with ``id="model"``."""
    text = (HOSTS_DIR / host / "fragments" / "site-tips.html").read_text(encoding="utf-8")
    match = re.search(r'<div class="tip" id="model">(.*?)</div>', text, re.S)
    return flat(html.unescape(re.sub(r"<[^>]+>", " ", match.group(1)))) if match else None


class EveryAssistantsTipStatesTheOneModelRule(unittest.TestCase):
    def test_every_assistant_has_the_tip(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIsNotNone(tip(host), "site-tips.html has no tip with id=\"model\"")

    def test_it_states_the_rule_and_that_nothing_is_asked(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIn(RULE, tip(host))
                self.assertIn(NEVER, tip(host))

    def test_it_names_that_assistants_capable_model(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIn(capable_model(host).lower() + " suits it well", tip(host).lower())

    def test_it_is_headed_for_the_model_alone(self):
        """Sentence case, and no effort setting to look for."""
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertTrue(tip(host).startswith("Model " + RULE), tip(host)[:60])


class NoSitePageNamesAMidBootcampSwitch(unittest.TestCase):
    def fragments(self):
        return sorted(HOSTS_DIR.glob("*/fragments/site-*.html"))

    def test_the_fragments_are_found(self):
        self.assertGreaterEqual(len(self.fragments()), 3 * len(HOSTS))

    def test_no_fragment_names_one(self):
        for path in self.fragments():
            with self.subTest(path=path.relative_to(REPO_ROOT).as_posix()):
                found = [m.group(0) for m in MID_BOOTCAMP_SWITCH.finditer(visible(path))]
                self.assertEqual([], found)

    def test_the_wording_each_tip_used_to_carry_is_reported(self):
        """Negative controls (INV-265): the five sentences issue #4 removed."""
        for retired in (
                "At the start of each module the bootcamp tells you when to switch to Opus 5.5.",
                "The bootcamp suggests a model and effort at the start of each module, and only "
                "you can change the setting.",
                "At the start of each module the bootcamp may suggest a more capable model.",
                "it adapts its model and effort guidance to the interface you are in",
                "Switch mid-session with /model claude-opus-5-5",
        ):
            with self.subTest(retired=retired[:40]):
                self.assertTrue(MID_BOOTCAMP_SWITCH.search(retired))

    def test_the_new_wording_and_an_install_time_choice_are_not(self):
        for kept in (RULE + " Opus 5.5 suits it well. " + NEVER,
                     "Choose the Model Opus 5.5.",
                     "claude --model claude-opus-5-5 --effort medium --permission-mode auto",
                     "In the lower right of Codex, select the model and effort:"):
            with self.subTest(kept=kept[:40]):
                self.assertIsNone(MID_BOOTCAMP_SWITCH.search(kept))

    def test_the_claude_walkthrough_starts_on_the_model_the_welcome_names(self):
        text = visible(HOSTS_DIR / "claude" / "fragments" / "site-install.html")
        self.assertIn("Choose the Model %s ." % capable_model("claude"), text)
        self.assertIn("claude --model claude-opus-5-5 ", text)
        self.assertNotIn("Sonnet", text)


class TheMaintainerNotesDescribeTheSameBehavior(unittest.TestCase):
    def setUp(self):
        self.raw = MODEL_SELECTION.read_text(encoding="utf-8")
        self.text = flat(self.raw)

    def test_they_state_the_rule(self):
        self.assertIn("the bootcamp handles this itself", self.text)
        self.assertIn("One model is fine for the whole bootcamp, the bootcamper is never asked to "
                      "change the model or the reasoning effort", self.text)
        self.assertIn("how carefully the guide works at each stage is set by instruction alone",
                      self.text)

    def test_they_name_no_mid_bootcamp_switch(self):
        found = [m.group(0) for m in MID_BOOTCAMP_SWITCH.finditer(self.text)]
        self.assertEqual([], found)
        self.assertNotRegex(self.text, r"(?i)switch question|done modifying|the nudge\b")

    def test_they_say_why_a_skill_setting_does_not_fit(self):
        self.assertIn("**Skill frontmatter is turn-scoped.**", self.text)
        self.assertIn("A bootcamp module is loaded once and then runs for many turns", self.text)

    def test_their_table_and_instructions_are_the_ground_rules_copy(self):
        rules = depth_block(skill_text("claude", "bootcamp-onboarding/ground-rules.md"))
        start = self.raw.index("| Stage | Effort |")
        notes = self.raw[start:self.raw.index("**One row per stage", start)]
        self.assertEqual(depth_rows(rules), depth_rows(notes))
        self.assertEqual(depth_instructions(rules), depth_instructions(notes))


if __name__ == "__main__":
    unittest.main()
