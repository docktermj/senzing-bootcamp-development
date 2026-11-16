"""The guide is told to read the ground rules to the last line, on every assistant (PR #3).

Kiro IDE 1.4.26 cuts a tool result at about 30,000 characters, and `ground-rules.md` is about
134 KB. On 2026-11-15 a first turn there read under a tenth of the file before the welcome, so
most of the bootcamp's rules were never seen. The onboarding skill now says a read that was cut
short has not read the file, and to continue to the last line before the first reply.

Enforces **INV-427** (registered 2026-11-16). It establishes that every package carries the
instruction at the step that names the file; it does not establish that a live turn obeys it,
which only a run on the assistant can show (`hosts/kiro/checks.json` records one that did).

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest

from _built import built

HOSTS = ("claude", "copilot", "kiro", "chatgpt", "gemini")


def flat(text):
    """Whitespace collapsed, so a re-wrapped sentence still matches."""
    return re.sub(r"\s+", " ", text)


def step_one(host):
    text = flat((built(host) / "skills" / "bootcamp-onboarding" / "SKILL.md").read_text(encoding="utf-8"))
    start = text.index("1. **Read and follow `ground-rules.md`**")
    return text[start:text.index("2. **Fresh start vs. resume", start)]


def says_read_to_the_end(step):
    return all(phrase in step for phrase in (
        "(INV-427) Read the file to its last line.",
        "cut short or truncated has not read it",
        "continue from where it stopped",
        "before the first reply",
    ))


class TheGroundRulesAreReadToTheEnd(unittest.TestCase):
    def test_every_package_says_so_at_the_step_that_names_the_file(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertTrue(says_read_to_the_end(step_one(host)), step_one(host))

    def test_the_instruction_is_the_same_in_every_package(self):
        steps = {host: step_one(host).split("\u26d4", 1)[1] for host in HOSTS}
        self.assertEqual(len(set(steps.values())), 1, steps)


class TheCheckSeesAStepWithoutIt(unittest.TestCase):
    def test_a_step_missing_any_part_fails(self):
        whole = step_one("claude")
        self.assertTrue(says_read_to_the_end(whole))
        for part in ("Read the file to its last line.", "continue from where it stopped",
                     "before the first reply"):
            with self.subTest(part=part):
                self.assertFalse(says_read_to_the_end(whole.replace(part, "")))


if __name__ == "__main__":
    unittest.main()
