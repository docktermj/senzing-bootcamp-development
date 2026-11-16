"""No pinned question hands the bootcamper a model or effort command any more (#4).

**INV-236** names this file as its enforcer. Its rule: where a pinned question hands the
bootcamper a command or a control they can operate themselves, the reply after a yes is
composed from what the setting actually is, never from the yes alone. Its one concrete site
was the module-start switch question ("Would you like to switch to `/effort medium` for this
module?") and the "Are you done modifying the model and effort?" gate that followed a yes.

Issue #4 removed both, on every assistant: the bootcamp never asks for a model or effort
change. So the three reply shapes this file used to hold every copy of the flow to have
nothing left to govern, and what it enforces now is the stronger condition they depended on:

1. No package pins a 👉 question that hands the bootcamper a slash command for the model or
   the effort, or a control for either.
2. No package carries the confirmation gate, in any wording, or the three shapes that
   decided whether it was asked.
3. A module start runs straight into its first step, so there is no reply turn after a yes
   to compose.

⚠️ **What this leaves open.** INV-236's general rule still binds any future pinned question
that hands over a command, and nothing here checks one, because none exists. Its registered
wording describes the retired switch as its concrete case and is superseded separately;
`specs/INVARIANTS.md` is not read here.

Reads collapsed text, so a re-wrapped question still matches.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest

from _model_effort import (ABOUT_MODEL_OR_EFFORT, GROUND_RULES, HOSTS, PINNED_QUESTION, flat,
                           package_texts, skill_text)

#: A pinned question that shows a slash command, or names a control for the model or effort.
HANDS_OVER = re.compile(r"`/(?:model|effort)\b|\b(?:model|effort) (?:and effort )?controls?\b")
#: The post-yes flow's own vocabulary: the gate, and the three shapes read from the dial.
POST_YES_FLOW = re.compile(
    r"(?i)done modifying|read what the dial is actually set to|the dial is not yet set"
    r"|the dial is already at")


def pinned_questions(host):
    """``(file, question)`` for every pinned 👉 question in ``host``'s package."""
    return [(name, match.group(1)) for name, text in package_texts(host) if name.endswith(".md")
            for match in PINNED_QUESTION.finditer(flat(text))]


class NoPinnedQuestionHandsOverAModelOrEffortCommand(unittest.TestCase):
    def test_the_pinned_questions_are_found(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertGreater(len(pinned_questions(host)), 80,
                                   "far fewer pinned questions than the bootcamp asks")

    def test_none_hands_over_a_command_or_a_control(self):
        for host in HOSTS:
            offenders = ["%s: %s" % (name, question[:80])
                         for name, question in pinned_questions(host)
                         if HANDS_OVER.search(question) or ABOUT_MODEL_OR_EFFORT.search(question)]
            with self.subTest(host=host):
                self.assertEqual([], offenders)

    def test_a_question_that_did_is_reported(self):
        """Negative controls (INV-265): the two pinned forms issue #4 removed."""
        for retired in (
                "👉 **Would you like to switch to `/model {model}` + `/effort {effort}` for "
                "this module?** (Recommended for best value.)",
                "👉 **Would you like to switch to {Model} at {effort} reasoning effort for "
                "graduation?** (set it with the model and effort controls.)"):
            with self.subTest(retired=retired[:50]):
                question = PINNED_QUESTION.search(flat(retired)).group(1)
                self.assertTrue(HANDS_OVER.search(question) or ABOUT_MODEL_OR_EFFORT.search(question))


class ThePostYesFlowIsGone(unittest.TestCase):
    def test_no_package_carries_the_gate_or_its_three_shapes(self):
        for host in HOSTS:
            offenders = ["%s: %r" % (name, match.group(0))
                         for name, text in package_texts(host) if name.endswith(".md")
                         for match in POST_YES_FLOW.finditer(flat(text))]
            with self.subTest(host=host):
                self.assertEqual([], offenders)

    def test_a_module_start_leaves_no_reply_turn_to_compose(self):
        for host in HOSTS:
            with self.subTest(host=host):
                rules = flat(skill_text(host, GROUND_RULES))
                self.assertIn("then continue straight into Step 1 the same turn", rules)
                self.assertNotRegex(rules, r"(?i)on \*\*yes\*\*, read|takes one of the three shapes")


if __name__ == "__main__":
    unittest.main()
