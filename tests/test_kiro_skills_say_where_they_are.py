"""Every skill in the Kiro package says where its own directory is.

Kiro hands the assistant a ``SKILL.md`` without its path, so "this skill directory" names
nothing. On Kiro IDE 1.4.26 (2026-11-15) the first turn ran ``find /`` for the files beside the
skill and reached a backup of another copy of the bootcamp. The Kiro package therefore states
each skill's installed location in the skill itself.
"""

import unittest

from _built import built

INSTALLED = "~/.kiro/powers/installed/senzing-bootcamp"


class KiroSkillsSayWhereTheyAre(unittest.TestCase):
    def test_every_kiro_skill_names_its_own_directory(self):
        skills = sorted(path for path in (built("kiro") / "skills").iterdir() if path.is_dir())
        self.assertTrue(skills)
        for skill in skills:
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill.name):
                self.assertIn(f"`{INSTALLED}/skills/{skill.name}/`", text)
                self.assertIn("Never search the rest of the filesystem", text)

    def test_the_note_is_stated_once(self):
        for skill in sorted((built("kiro") / "skills").iterdir()):
            if skill.is_dir():
                text = (skill / "SKILL.md").read_text(encoding="utf-8")
                with self.subTest(skill=skill.name):
                    self.assertEqual(text.count("**Where this skill's files are.**"), 1)

    def test_an_assistant_that_gives_the_path_gets_no_note(self):
        for host in ("claude", "copilot"):
            for skill in sorted((built(host) / "skills").iterdir()):
                if skill.is_dir():
                    with self.subTest(host=host, skill=skill.name):
                        self.assertNotIn(".kiro/", (skill / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
