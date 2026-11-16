"""An auto-test walk can start mid-bootcamp and runs at one model and effort throughout (#870, #4).

A walk meant to judge #855 on Modules 5 to 7 started at Bootcamp preparation, and the
simulated Bootcamper followed the guide's model/effort nudge with `/model opus` and
`/effort high`, which `walk.py` then applied (#656). #870 added `--seed mid`, `--effort` and a
`--pin` flag that held the command line's values against those lines.

⚠️ **Issue #4 removed the nudge, and with it the reason for `--pin`.** The bootcamp asks the
Bootcamper to change no model and no effort, so `walk.py` reads no reply line as a `/model` or
`/effort` command: nothing a Bootcamper types changes a flag, and there is nothing to pin.
This file was `test_auto_test_pin_and_mid.py`. What it holds now:

1. **`--seed mid`** builds the project with `scaffold_project.py`'s mid-bootcamp mode, which
   takes no mode flag, and the lint then defaults to `--phase content`; an explicit `--phase`
   still wins.
2. **`--effort <level>`** goes on every guide call from the first, as `--model` does.
3. **Both hold for the whole walk.** A Bootcamper reply that starts with `/model` or
   `/effort` is sent to the guide as text, changes no flag and logs no flag event.
4. **`--pin` is gone** from `walk.py` and `autotest.py`, with the `bootcamper_flag`,
   `bootcamper_flag_ignored` events and the `bootcamper-flag-ignored` finding.

⚠️ **What this does NOT establish:** that a live walk with `--seed mid` actually resumes at
Module 5, or that the CLI honors `--effort` on a resumed call. Both need a live walk; the
stubs here only show what the harness sends.

Stdlib only, offline (INV-108).
"""
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTO_TEST = REPO_ROOT / ".claude" / "skills" / "auto-test"
sys.path.insert(0, str(AUTO_TEST))

import autotest  # noqa: E402
import walk  # noqa: E402

POINTER = "\U0001f449"


def _assistant(text):
    return json.dumps({"type": "assistant",
                       "message": {"content": [{"type": "text", "text": text}]}})


def run(replies, turns=3, model=None, effort=None):
    """Walk with a stub guide and a scripted Bootcamper; return (argvs, prompts, events)."""
    argvs, prompts, script = [], [], list(replies)

    def fake_claude(args, cwd, stdin_text=None, timeout=600, env=None):
        argvs.append(list(args))
        text = f"Turn {len(argvs)}. " + "x" * 220 + f"\n{POINTER} What next?"
        return subprocess.CompletedProcess(args, 0, stdout=_assistant(text) + "\n", stderr="")

    def fake_reply(prompt_text, persona, model, cwd=None, timeout=180):
        prompts.append(prompt_text)
        return script.pop(0) if script else "ok"

    with tempfile.TemporaryDirectory() as tmp, \
            mock.patch.object(walk, "_claude", fake_claude), \
            mock.patch.object(walk, "bootcamper_reply", fake_reply), \
            redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        out = Path(tmp) / "t.jsonl"
        project = Path(tmp) / "project"
        project.mkdir()
        walk.run_walk(project, out, turns, "terse", Path(tmp) / "mcp.json", model, None,
                      "/senzing-bootcamp:start-bootcamp", False, 5, effort=effort)
        # No phrase-level pattern (#870): each line read is one JSON transcript event.
        events = [json.loads(line) for line in out.read_text().splitlines() if line]
    return argvs, prompts, events


def values(argv, flag):
    return [argv[i + 1] for i, a in enumerate(argv) if a == flag]


def of_type(events, kind):
    return [e for e in events if e.get("type") == kind]


class EffortIsSentFromTheFirstTurn(unittest.TestCase):
    def test_every_call_carries_the_effort(self):
        argvs, _, _ = run(["yes", "ok"], turns=3, effort="low")
        self.assertEqual(len(argvs), 3)
        for argv in argvs:
            self.assertEqual(values(argv, "--effort"), ["low"])

    def test_no_effort_sends_none(self):
        argvs, _, _ = run(["yes"], turns=2)
        for argv in argvs:
            self.assertEqual(values(argv, "--effort"), [])


class NothingABootcamperTypesChangesAFlag(unittest.TestCase):
    REPLIES = ["/model claude-opus-5-5\n/effort high\nyes", "ok"]

    def test_the_model_and_effort_hold_for_the_whole_walk(self):
        argvs, _, events = run(self.REPLIES, turns=3, model="claude-haiku-5-5", effort="low")
        self.assertEqual(len(argvs), 3)
        for argv in argvs:
            self.assertEqual(values(argv, "--model"), ["claude-haiku-5-5"])
            self.assertEqual(values(argv, "--effort"), ["low"])
        self.assertEqual(of_type(events, "bootcamper_flag"), [])
        self.assertEqual(of_type(events, "bootcamper_flag_ignored"), [])

    def test_the_reply_reaches_the_guide_as_text(self):
        """One leading space, the form the CLI does not parse as a command (#656)."""
        argvs, _, events = run(self.REPLIES, turns=2)
        self.assertEqual(argvs[1][:2], ["-p", " " + self.REPLIES[0]])
        self.assertEqual(of_type(events, "bootcamper")[0]["text"], self.REPLIES[0])

    def test_with_no_flags_given_none_is_sent(self):
        argvs, _, _ = run(self.REPLIES, turns=3)
        for argv in argvs:
            self.assertEqual(values(argv, "--model") + values(argv, "--effort"), [])

    def test_a_slash_only_reply_is_a_turn_and_is_not_asked_again(self):
        argvs, prompts, _ = run(["/effort high", "yes"], turns=3, effort="low")
        self.assertEqual(argvs[1][:2], ["-p", " /effort high"])
        self.assertTrue(prompts[0].startswith("Turn 1."))
        self.assertTrue(prompts[1].startswith("Turn 2."),
                        "the Bootcamper was asked again for the same turn")
        self.assertNotIn("You entered:", prompts[1])

    def test_walk_has_no_pin_and_no_slash_flags(self):
        self.assertFalse(hasattr(walk, "SLASH_FLAGS"))
        self.assertFalse(hasattr(walk, "split_reply"))
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            walk.main(["--project", ".", "--out", "x", "--mcp-config", "y", "--pin"])

    def test_the_brief_does_not_prompt_a_slash_command(self):
        self.assertNotRegex(walk.BOOTCAMPER_BRIEF, r"/effort|/model|slash command")


class AutotestPassesItThrough(unittest.TestCase):
    """`autotest.main` with `_run` stubbed: no worktree, no probe, no walk run."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        self.calls = []
        self.transcript_lines = ['{"turn": 1}']
        for name, value in (("_run", self.fake_run),
                            ("SANDBOX_ROOT", self.tmp / "senzing-autotest"),
                            ("REPORT_DIR", self.tmp / "reports")):
            patcher = mock.patch.object(autotest, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def fake_run(self, cmd, **kw):
        cmd = [str(c) for c in cmd]
        self.calls.append(cmd)
        if cmd[:1] == ["git"]:
            return subprocess.CompletedProcess(cmd, 1, "", "no worktree offline")
        if cmd[1].endswith("walk.py"):
            Path(cmd[cmd.index("--out") + 1]).write_text(
                "\n".join(self.transcript_lines) + "\n", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "[]", "")

    def main(self, *argv):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            autotest.main(["--walk", "--json", *argv])
        report = sorted((self.tmp / "reports").glob("2*.json"))
        return json.loads([p for p in report if "transcript" not in p.name][-1].read_text())

    def call(self, script):
        return next(c for c in self.calls if c[1].endswith(script))

    def test_seed_mid_runs_the_scaffold_without_a_mode_flag_and_lints_content(self):
        self.main("--seed", "mid")
        scaffold = self.call("scaffold_project.py")
        self.assertFalse({"--fresh", "--seeded", "--mid"} & set(scaffold), scaffold)
        self.assertEqual(values(self.call("transcript_lint.py"), "--phase"), ["content"])

    def test_an_explicit_phase_wins(self):
        self.main("--seed", "mid", "--phase", "module0")
        self.assertEqual(values(self.call("transcript_lint.py"), "--phase"), ["module0"])

    def test_the_default_seed_is_unchanged(self):
        self.main()
        self.assertIn("--fresh", self.call("scaffold_project.py"))
        self.assertEqual(values(self.call("transcript_lint.py"), "--phase"), ["preparation"])

    def test_effort_reaches_the_walk(self):
        self.main("--effort", "low")
        argv = self.call("walk.py")
        self.assertEqual(values(argv, "--effort"), ["low"])
        self.assertNotIn("--pin", argv)

    def test_it_is_not_sent_by_default(self):
        self.main()
        argv = self.call("walk.py")
        self.assertNotIn("--effort", argv)
        self.assertNotIn("--pin", argv)

    def test_autotest_has_no_pin_and_no_flag_finding(self):
        self.assertFalse(hasattr(autotest, "ignored_flag_findings"))
        with self.assertRaises(SystemExit), redirect_stdout(io.StringIO()), \
                redirect_stderr(io.StringIO()):
            autotest.main(["--walk", "--pin"])

    def test_an_old_flag_event_in_a_transcript_is_not_a_finding(self):
        self.transcript_lines = [json.dumps({"type": "bootcamper_flag_ignored", "turn": 4,
                                             "command": "/model claude-opus-5-5",
                                             "flag": "--model", "value": "claude-opus-5-5"})]
        self.assertEqual([], [f for f in self.main()["findings"]
                              if f["code"] == "bootcamper-flag-ignored"])


if __name__ == "__main__":
    unittest.main()
