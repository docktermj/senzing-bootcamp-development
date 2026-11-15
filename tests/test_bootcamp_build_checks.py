"""A package nobody has run on the real assistant is labeled a preview, on its page and at promotion.

``hosts/<assistant>/checks.json`` records each real run: which version, in which client, how far
it went. The install page says what those records say, and promotion will not write a package
that was never installed and started unless the maintainer names it as a preview.
"""

import contextlib
import dataclasses
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.__main__ import main  # noqa: E402
from tools.bootcamp_build.model import SOURCE_DIR, host_ids, load_declaration, load_host  # noqa: E402
from tools.bootcamp_build.site import verification_note  # noqa: E402

VERSION = load_declaration(SOURCE_DIR)["version"]


def record(scope, result="pass", version=VERSION, date="2026-11-14"):
    return {"release": version, "client": "Example CLI 1.0", "date": date, "scope": scope, "result": result}


def note(*records):
    host = dataclasses.replace(load_host("kiro"), checks=tuple(records))
    return verification_note(host, VERSION, "")


class InstallPageNote(unittest.TestCase):
    def test_no_record_is_a_preview_that_says_it_was_never_run(self):
        text = note()
        self.assertIn("<strong>Preview.</strong>", text)
        self.assertIn("has not yet been run in Kiro", text)

    def test_a_first_turn_from_a_local_build_is_still_a_preview(self):
        text = note(record("first-turn"))
        self.assertIn("<strong>Preview.</strong>", text)
        self.assertIn("from a local build", text)
        self.assertIn("Example CLI 1.0 on 2026-11-14", text)

    def test_an_install_check_is_a_preview_until_the_bootcamp_is_walked(self):
        text = note(record("install"))
        self.assertIn("<strong>Preview.</strong>", text)
        self.assertIn("installed and started", text)

    def test_a_full_walk_is_reported_as_checked(self):
        text = note(record("first-turn"), record("full"))
        self.assertNotIn("Preview", text)
        self.assertIn("Checked end to end in Example CLI 1.0 on 2026-11-14", text)

    def test_a_check_of_another_version_does_not_count(self):
        self.assertIn("has not yet been run", note(record("full", version="0.0.1")))

    def test_a_failed_check_does_not_count(self):
        self.assertIn("has not yet been run", note(record("full", result="fail")))


class RecordedChecks(unittest.TestCase):
    def test_every_record_on_file_is_well_formed(self):
        """Loading a profile validates its records, so a malformed one stops every build."""
        for host_id in host_ids():
            with self.subTest(host=host_id):
                for check in load_host(host_id).checks:
                    self.assertIn(check["scope"], ("first-turn", "install", "full"))
                    self.assertTrue(check.get("notes"), "a record says what was seen")


class PromotionGate(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.public = Path(scratch.name)
        subprocess.run(["git", "-C", str(self.public), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(self.public), "remote", "add", "origin",
                        "git@github.com:Senzing/bootcamp.git"], check=True)

    def promote(self, *arguments):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["promote", "--to", str(self.public), *arguments])
        return code, out.getvalue(), err.getvalue()

    def written(self):
        return [path for path in self.public.rglob("*") if path.is_file() and ".git" not in path.parts]

    def unchecked(self):
        return [
            host_id for host_id in host_ids()
            if not any(load_host(host_id).check_for(VERSION, scope) for scope in ("install", "full"))
        ]

    def test_the_plan_lists_what_was_checked_and_writes_nothing(self):
        code, out, _ = self.promote()
        self.assertEqual(code, 0)
        self.assertIn(f"On-assistant checks recorded for version {VERSION}", out)
        for host_id in host_ids():
            self.assertRegex(out, rf"(?m)^  {host_id}\s")
        self.assertEqual(self.written(), [])

    def test_applying_is_refused_while_an_assistant_was_never_installed(self):
        if not self.unchecked():
            self.skipTest("every assistant has an install check for this version")
        code, _, err = self.promote("--apply")
        self.assertEqual(code, 2)
        self.assertIn("has not been installed and started on", err)
        self.assertIn("--allow-preview", err)
        self.assertEqual(self.written(), [], "a refused promotion writes nothing")

    def test_naming_the_previews_lets_the_promotion_through(self):
        code, out, _ = self.promote("--apply", "--allow-preview", "all")
        self.assertEqual(code, 0)
        self.assertIn("Nothing was committed or pushed", out)
        self.assertTrue((self.public / "plugins" / "claude" / "senzing-bootcamp").is_dir())

    def test_naming_only_some_previews_is_still_refused(self):
        unchecked = self.unchecked()
        if len(unchecked) < 2:
            self.skipTest("fewer than two assistants lack an install check")
        code, _, err = self.promote("--apply", "--allow-preview", unchecked[0])
        self.assertEqual(code, 2)
        self.assertNotIn(unchecked[0] + ",", err.split("on:")[1].split(".")[0] + ",")
        self.assertEqual(self.written(), [])


if __name__ == "__main__":
    unittest.main()
