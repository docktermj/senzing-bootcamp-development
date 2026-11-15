"""Promotion writes a build into the public repository's working tree, and only there."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.model import BuildError  # noqa: E402
from tools.bootcamp_build.promote import promote  # noqa: E402

CATALOG = ".claude-plugin/marketplace.json"


def git(directory, *arguments):
    return subprocess.run(["git", "-C", str(directory), *arguments], capture_output=True, text=True, check=True)


class Promotion(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.dist, self.site, self.public = self.root / "dist", self.root / "site", self.root / "public"
        self.write(self.dist / "plugins/claude/senzing-bootcamp/skills/start/SKILL.md", "v2\n")
        self.write(self.dist / CATALOG, "{}\n")
        self.write(self.site / "index.html", "<h1>new</h1>\n")
        self.write(self.site / "promote.json", '{"preserve": ["video/"]}\n')
        self.public.mkdir()
        git(self.public, "init", "-q")
        git(self.public, "remote", "add", "origin", "git@github.com:Senzing/bootcamp.git")
        self.write(self.public / "plugins/claude/senzing-bootcamp/skills/start/SKILL.md", "v1\n")
        self.write(self.public / "plugins/claude/senzing-bootcamp/skills/retired/SKILL.md", "old\n")
        self.write(self.public / "docs/index.html", "<h1>old</h1>\n")
        self.write(self.public / "docs/stale.html", "gone\n")
        self.write(self.public / "docs/video/promo.mp4", "binary\n")
        self.write(self.public / "README.md", "public readme\n")

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_promotion(self, apply):
        return promote(self.dist, [CATALOG], self.site, self.public, apply=apply)

    def test_the_plan_names_every_change_and_writes_nothing(self):
        plan = self.run_promotion(apply=False)
        self.assertEqual(plan.added, [CATALOG])
        self.assertEqual(plan.changed, ["docs/index.html", "plugins/claude/senzing-bootcamp/skills/start/SKILL.md"])
        self.assertEqual(plan.removed, ["docs/stale.html", "plugins/claude/senzing-bootcamp/skills/retired/SKILL.md"])
        self.assertEqual((self.public / "docs/index.html").read_text(), "<h1>old</h1>\n")
        self.assertFalse((self.public / CATALOG).exists())

    def test_applying_makes_the_managed_paths_match_the_build(self):
        self.run_promotion(apply=True)
        self.assertEqual((self.public / "plugins/claude/senzing-bootcamp/skills/start/SKILL.md").read_text(), "v2\n")
        self.assertFalse((self.public / "plugins/claude/senzing-bootcamp/skills/retired").exists())
        self.assertEqual((self.public / "docs/index.html").read_text(), "<h1>new</h1>\n")
        self.assertFalse((self.public / "docs/stale.html").exists())
        self.assertTrue(self.run_promotion(apply=False).empty)

    def test_preserved_site_paths_and_unmanaged_files_are_left_alone(self):
        self.run_promotion(apply=True)
        self.assertEqual((self.public / "docs/video/promo.mp4").read_text(), "binary\n")
        self.assertEqual((self.public / "README.md").read_text(), "public readme\n")
        self.assertFalse((self.public / "docs/promote.json").exists())

    def test_nothing_is_committed_or_staged(self):
        self.run_promotion(apply=True)
        self.assertEqual(git(self.public, "diff", "--cached", "--name-only").stdout, "")
        self.assertNotEqual(git(self.public, "status", "--porcelain").stdout, "")

    def test_a_directory_that_is_not_the_public_repository_is_refused(self):
        git(self.public, "remote", "set-url", "origin", "git@github.com:someone/elsewhere.git")
        with self.assertRaisesRegex(BuildError, "not Senzing/bootcamp"):
            self.run_promotion(apply=True)
        self.assertEqual((self.public / "docs/index.html").read_text(), "<h1>old</h1>\n")

    def test_a_directory_that_is_not_a_repository_is_refused(self):
        with tempfile.TemporaryDirectory() as plain, self.assertRaisesRegex(BuildError, "not a git working tree"):
            promote(self.dist, [CATALOG], self.site, Path(plain), apply=True)


if __name__ == "__main__":
    unittest.main()
