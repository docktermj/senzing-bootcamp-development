"""A Bootcamper reply that starts with `/` reaches the walk's session as typed (#656).

`walk.py` sent every Bootcamper reply as `claude -p <reply>`, and the CLI parses a prompt that
starts with `/` as a slash command. A simulated walk stalled at the first effort gate: the
reply `/effort high` then `yes` ran `/effort` with the argument `high\\n\\nyes`, and the CLI's
"Invalid argument" became the next "turn". #656 answered with two things: a reply that starts
with `/` is sent with one leading space, and a leading `/effort <level>` or `/model <name>`
line became a sticky `--effort` / `--model` flag (extended by #870 and #877).

⚠️ **Issue #4 removed the second half (2026-11-16).** The bootcamp no longer asks the
Bootcamper to change the model or the effort, so there is no gate for a simulated Bootcamper
to answer with a slash command, and `walk.py` reads no reply line as one. What remains is the
first half, and it now covers every reply.

Checks, each driven through `walk.run_walk` with a stub `claude` that records every call's
argv and a scripted Bootcamper:

1. **A path reply is the turn.** A reply that starts with `/`, such as `/data/claims.csv`, is
   sent with one leading space, the form the CLI does not parse, and sets no flag.
2. **A `/effort` or `/model` line is text too.** It reaches the guide inside the turn, sets
   no flag on that call or any later one, and writes no flag event.
3. **The original text is logged.** The `bootcamper` event holds the reply exactly as the
   Bootcamper process returned it.
4. **A slash-only reply is a turn.** It is sent, not re-asked, and does not stop the walk.
5. **The opening** `/senzing-bootcamp:start-bootcamp` is still sent unchanged at turn 1.
6. **The brief** no longer tells the Bootcamper how to type a slash command.

⚠️ **What this does NOT establish:** that the live CLI still sends a space-led prompt as
text. That was probed once, against a local stub Messages API with scratch `HOME` and
`CLAUDE_CONFIG_DIR` (no credentials, no model call), and is recorded in the #656 ledger
entry; a CLI release can change it.

Stdlib only, offline (INV-108).
"""
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTO_TEST = REPO_ROOT / ".claude" / "skills" / "auto-test"
DRY_RUN = REPO_ROOT / ".claude" / "skills" / "dry-run"

sys.path.insert(0, str(AUTO_TEST))
sys.path.insert(0, str(DRY_RUN))

import module_banners  # noqa: E402
import transcript_lint  # noqa: E402
import walk  # noqa: E402

POINTER = "\U0001f449"
OPENING = "/senzing-bootcamp:start-bootcamp"


def _assistant(text):
    return json.dumps({"type": "assistant",
                       "message": {"content": [{"type": "text", "text": text}]}})


def _guide_turn(n):
    return f"Turn {n} of the bootcamp. " + "x" * 220 + f"\n{POINTER} What next?"


def run(replies, turns=3, model=None):
    """Walk ``turns`` turns with a scripted Bootcamper; return (argvs, prompts, events)."""
    argvs, prompts, script = [], [], list(replies)

    def fake_claude(args, cwd, stdin_text=None, timeout=600, env=None):
        argvs.append(list(args))
        return subprocess.CompletedProcess(args, 0, stdout=_assistant(
            _guide_turn(len(argvs))) + "\n", stderr="")

    def fake_reply(prompt_text, persona, model, cwd=None, timeout=180):
        prompts.append(prompt_text)
        return script.pop(0) if script else "ok"

    with tempfile.TemporaryDirectory() as tmp, \
            mock.patch.object(walk, "_claude", fake_claude), \
            mock.patch.object(walk, "bootcamper_reply", fake_reply), \
            redirect_stdout(io.StringIO()), \
            mock.patch("sys.stderr", io.StringIO()):
        out = Path(tmp) / "t.jsonl"
        # A project directory of its own: the Bootcamper's cwd is made beside it (#834).
        project = Path(tmp) / "project"
        project.mkdir()
        walk.run_walk(project, out, turns, "terse", Path(tmp) / "mcp.json", model, None,
                      OPENING, False, 5)
        events = [json.loads(line) for line in out.read_text().splitlines() if line]
    return argvs, prompts, events


def flag_values(argv, flag):
    return [argv[i + 1] for i, a in enumerate(argv) if a == flag]


def of_type(events, kind):
    return [e for e in events if e.get("type") == kind]


class APathReplyIsTheTurn(unittest.TestCase):
    """Check 1."""

    def test_a_path_is_sent_with_a_leading_space(self):
        argvs, _, events = run(["/data/claims.csv", "1"], turns=3)
        self.assertEqual(len(argvs), 3)
        self.assertEqual(argvs[1][:2], ["-p", " /data/claims.csv"])
        for argv in argvs:
            self.assertEqual(flag_values(argv, "--effort"), [])
        self.assertEqual(of_type(events, "bootcamper_flag"), [])
        self.assertEqual(of_type(events, "bootcamper")[0]["text"], "/data/claims.csv")

    def test_any_other_command_is_text_too(self):
        argvs, _, _ = run(["/help me pick"], turns=2)
        self.assertEqual(argvs[1][:2], ["-p", " /help me pick"])

    def test_ordinary_text_is_unchanged(self):
        self.assertEqual(walk.as_turn("yes /effort"), "yes /effort")
        self.assertEqual(walk.as_turn("/x"), " /x")


class AModelOrEffortLineIsTextToo(unittest.TestCase):
    """Check 2: the handling issue #4 removed stays removed."""

    def test_effort_high_then_yes_is_sent_whole_and_sets_no_flag(self):
        argvs, _, events = run(["/effort high\n\nyes", "1", "2"], turns=4)
        self.assertEqual(len(argvs), 4)
        self.assertEqual(events[-1]["reason"], "--turns 4 reached")
        self.assertEqual(argvs[1][:2], ["-p", " /effort high\n\nyes"])
        for argv in argvs:
            with self.subTest(argv=argv[:2]):
                self.assertEqual(flag_values(argv, "--effort"), [])
        for argv in argvs[1:]:
            self.assertIn("--resume", argv)

    def test_a_model_line_does_not_replace_the_walks_model(self):
        argvs, _, _ = run(["/effort high\nyes",
                           "/effort low\n/model claude-sonnet-4-5\nok", "x"],
                          turns=4, model="claude-opus-5-5")
        for argv in argvs:
            with self.subTest(argv=argv[:2]):
                self.assertEqual(flag_values(argv, "--model"), ["claude-opus-5-5"])
                self.assertEqual(flag_values(argv, "--effort"), [])
        self.assertEqual(argvs[2][:2], ["-p", " /effort low\n/model claude-sonnet-4-5\nok"])

    def test_no_flag_event_is_written(self):
        _, _, events = run(["/effort high\n\nyes", "/model\nok"], turns=3)
        self.assertEqual(of_type(events, "bootcamper_flag"), [])
        self.assertEqual(of_type(events, "bootcamper_flag_ignored"), [])
        self.assertEqual([], sorted({e["type"] for e in events
                                     if str(e.get("type", "")).startswith("bootcamper_flag")}))

    def test_the_slash_flag_table_and_its_parser_are_gone(self):
        self.assertFalse(hasattr(walk, "SLASH_FLAGS"))
        self.assertFalse(hasattr(walk, "SLASH_LINE"))
        self.assertFalse(hasattr(walk, "split_reply"))


class TheOriginalTextIsLogged(unittest.TestCase):
    """Check 3."""

    def test_the_bootcamper_event_keeps_the_slash_line(self):
        _, _, events = run(["/effort high\n\nyes"], turns=2)
        said = of_type(events, "bootcamper")
        self.assertEqual(said[0]["text"], "/effort high\n\nyes")

    def test_the_transcript_still_loads_turn_for_turn(self):
        _, _, events = run(["/effort high\n\nyes", "1"], turns=3)
        lines = [json.dumps(e) for e in events]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.jsonl"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            self.assertEqual(len(transcript_lint.load(path)), 3)
        _, summary = module_banners.slice_transcript(lines, 1)
        self.assertEqual(summary["walk_stop"]["reason"], "--turns 3 reached")
        self.assertEqual(len(of_type(events, "assistant")), 3)


class ASlashOnlyReplyIsATurn(unittest.TestCase):
    """Check 4."""

    def test_it_is_sent_and_not_asked_again(self):
        argvs, prompts, events = run(["/effort high", "yes"], turns=3)
        self.assertEqual(len(argvs), 3)
        self.assertEqual(argvs[1][:2], ["-p", " /effort high"])
        self.assertEqual(argvs[2][:2], ["-p", "yes"])
        self.assertNotEqual(prompts[0], prompts[1][:len(prompts[0])],
                            "the Bootcamper was asked again with the same guide turn")
        self.assertFalse([p for p in prompts if "You entered:" in p])
        self.assertEqual(events[-1]["reason"], "--turns 3 reached")

    def test_two_in_a_row_do_not_stop_the_walk(self):
        argvs, _, events = run(["/effort high", "/model claude-sonnet-4-5", "ok"], turns=4)
        self.assertEqual(len(argvs), 4)
        self.assertEqual(events[-1]["type"], "walk_stop")
        self.assertEqual(events[-1]["reason"], "--turns 4 reached")


class TheOpeningIsUnchanged(unittest.TestCase):
    """Check 5."""

    def test_turn_one_sends_the_opening_as_given(self):
        argvs, _, _ = run(["/data/claims.csv"], turns=2)
        self.assertEqual(argvs[0][:2], ["-p", OPENING])
        self.assertIn("--session-id", argvs[0])


class TheBriefPromptsNoSlashCommand(unittest.TestCase):
    """Check 6."""

    def test_the_brief_no_longer_carries_the_rule(self):
        brief = " ".join(walk.BOOTCAMPER_BRIEF.split())
        self.assertNotIn("slash command", brief)
        self.assertNotRegex(brief, r"/effort|/model")
        self.assertIn("Never mention that this is a test or a simulation.", brief)


if __name__ == "__main__":
    unittest.main()
