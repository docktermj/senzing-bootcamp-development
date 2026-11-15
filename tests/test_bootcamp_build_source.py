"""The real source builds for every host that has a profile, and builds the same way twice."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.emit import build_host  # noqa: E402
from tools.bootcamp_build.model import SOURCE_DIR, host_ids, load_declaration, load_host  # noqa: E402
from tools.bootcamp_build.validate import compare_trees  # noqa: E402


class EveryHostBuilds(unittest.TestCase):
    def test_there_is_at_least_one_host(self):
        self.assertIn("claude", host_ids())

    def test_each_host_builds_and_rebuilds_identically(self):
        declaration = load_declaration(SOURCE_DIR)
        known = set(host_ids())
        for host_id in host_ids():
            with self.subTest(host=host_id):
                host = load_host(host_id)
                with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
                    one = build_host(declaration, host, SOURCE_DIR, Path(first), known)
                    two = build_host(declaration, host, SOURCE_DIR, Path(second), known)
                    self.assertTrue(one.files)
                    self.assertEqual(compare_trees(one.root, two.root), [])

    def test_no_built_text_file_keeps_an_unrendered_token(self):
        declaration = load_declaration(SOURCE_DIR)
        known = set(host_ids())
        for host_id in host_ids():
            with self.subTest(host=host_id), tempfile.TemporaryDirectory() as out:
                build = build_host(declaration, load_host(host_id), SOURCE_DIR, Path(out), known)
                for relative in build.files:
                    if Path(relative).suffix in {".md", ".py", ".json", ".toml"} and "vendor" not in relative:
                        text = (build.root / relative).read_text(encoding="utf-8")
                        self.assertNotIn("{{host.", text, relative)
                        self.assertNotIn("<!-- host:", text, relative)


if __name__ == "__main__":
    unittest.main()
