"""The hook adapter lets one set of hook scripts run on assistants with different hook dialects.

It rewrites an assistant's payload in the canonical shape, runs the declared scripts, and
writes their merged result the way that assistant reads it. These tests pin both directions
for every payload shape and result dialect an assistant is known to use.
"""

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = REPO_ROOT / "hosts" / "_shared" / "hook_adapter.py"

_spec = importlib.util.spec_from_file_location("hook_adapter", ADAPTER)
adapter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(adapter)

CATEGORIES = {
    "create": "write", "write_file": "write", "edit": "edit", "str_replace_editor": "edit",
    "apply_patch": "patch", "bash": "shell", "run_command": "shell",
}
PATCH = (
    "*** Begin Patch\n"
    "*** Add File: src/new.py\n"
    "+print('hello')\n"
    "+KEY = 'AKIAABCDEFGHIJKLMNOP'\n"
    "*** Update File: src/old.py\n"
    "@@\n"
    "-old line\n"
    "+new line\n"
    "*** Delete File: src/gone.py\n"
    "*** End Patch\n"
)


def completed(stdout="", returncode=0, stderr=""):
    return SimpleNamespace(stdout=stdout, returncode=returncode, stderr=stderr)


class ToolCallShapes(unittest.TestCase):
    def test_every_known_payload_shape_yields_the_same_call(self):
        shapes = [
            {"tool_name": "create", "tool_input": {"path": "a.txt", "content": "x"}},
            {"toolName": "create", "toolArgs": {"path": "a.txt", "content": "x"}},
            {"toolCalls": [{"name": "create", "args": {"path": "a.txt", "content": "x"}}]},
            {"toolName": "create", "toolArgs": json.dumps({"path": "a.txt", "content": "x"})},
        ]
        for payload in shapes:
            with self.subTest(payload=payload):
                self.assertEqual(adapter.raw_tool_calls(payload)[0][0], "create")
                name, arguments = adapter.raw_tool_calls(payload)[0]
                calls = adapter.canonical_calls(name, arguments, CATEGORIES)
                self.assertEqual(calls[0][0], "Write")
                self.assertEqual(calls[0][1]["file_path"], "a.txt")
                self.assertEqual(calls[0][1]["content"], "x")

    def test_an_edit_keeps_the_new_text_so_a_secret_check_can_see_it(self):
        calls = adapter.canonical_calls("edit", {"filePath": "a.py", "new_str": "SECRET"}, CATEGORIES)
        self.assertEqual(calls, [("Edit", {"filePath": "a.py", "new_str": "SECRET",
                                           "file_path": "a.py", "new_string": "SECRET"})])

    def test_a_shell_call_becomes_the_canonical_shell_tool(self):
        self.assertEqual(adapter.canonical_calls("run_command", {"CommandLine": "ls > /tmp/x"}, CATEGORIES),
                         [("Bash", {"command": "ls > /tmp/x"})])

    def test_a_tool_the_bootcamp_does_not_gate_yields_nothing(self):
        self.assertEqual(adapter.canonical_calls("read_file", {"path": "a.txt"}, CATEGORIES), [])

    def test_a_patch_becomes_one_write_per_file_with_the_added_lines(self):
        for arguments in (PATCH, {"command": PATCH}, {"patch": PATCH}):
            with self.subTest(arguments=type(arguments).__name__):
                calls = adapter.canonical_calls("apply_patch", arguments, CATEGORIES)
                self.assertEqual([(tool, call["file_path"]) for tool, call in calls],
                                 [("Write", "src/new.py"), ("Edit", "src/old.py")])
                self.assertIn("AKIAABCDEFGHIJKLMNOP", calls[0][1]["content"])
                self.assertEqual(calls[1][1]["content"], "new line")

    def test_a_deleted_file_writes_nothing(self):
        self.assertNotIn("src/gone.py", [call["file_path"] for _, call in adapter.patch_calls(PATCH)])


class CanonicalPayloads(unittest.TestCase):
    def payloads(self, event, payload, hook=None, environ=None):
        return adapter.canonical_payloads(
            event, hook or {"script": "x.py"}, payload, {"tool_categories": CATEGORIES},
            environ or {}, Path("/project"))

    def test_the_prompt_is_found_under_any_known_key_or_in_the_environment(self):
        for payload, environ in (({"prompt": "hi"}, {}), ({"user_prompt": "hi"}, {}),
                                 ({"userPrompt": "hi"}, {}), ({}, {"USER_PROMPT": "hi"})):
            with self.subTest(payload=payload, environ=environ):
                (canonical,) = self.payloads("prompt_submit", payload, environ=environ)
                self.assertEqual(canonical["prompt"], "hi")
                self.assertEqual(canonical["hook_event_name"], "UserPromptSubmit")
                self.assertEqual(canonical["cwd"], "/project")

    def test_a_tool_hook_runs_once_per_call_it_is_limited_to(self):
        payload = {"toolCalls": [{"name": "bash", "args": {"command": "ls"}},
                                 {"name": "create", "args": {"path": "a", "content": "b"}}]}
        only_shell = self.payloads("pre_tool_use", payload, {"script": "x.py", "tools": ["shell"]})
        self.assertEqual([p["tool_name"] for p in only_shell], ["Bash"])
        everything = self.payloads("pre_tool_use", payload, {"script": "x.py", "tools": ["write", "edit", "shell"]})
        self.assertEqual([p["tool_name"] for p in everything], ["Bash", "Write"])

    def test_a_tool_result_travels_with_the_call(self):
        payload = {"toolName": "bash", "toolArgs": {"command": "python3 src/load.py"},
                   "toolResult": {"stdout": "", "stderr": "Traceback", "is_error": True}}
        (canonical,) = self.payloads("post_tool_use", payload, {"script": "x.py", "tools": ["shell"]})
        self.assertEqual(canonical["tool_response"]["stderr"], "Traceback")
        self.assertEqual(canonical["hook_event_name"], "PostToolUse")

    def test_a_failed_command_is_an_error_however_the_assistant_reports_it(self):
        """Captured from Copilot CLI 1.0.111: a failed command arrives as a "success" result
        whose text alone says "completed with exit code 1"."""
        failed = [
            {"resultType": "success", "textResultForLlm": "\n<shellId: 0 completed with exit code 1>"},
            {"result_type": "failure", "text_result_for_llm": "boom"},
            {"output": "Traceback (most recent call last)", "isError": True},
            "Exit code 2\nValueError: bad record",
        ]
        for result in failed:
            with self.subTest(result=result):
                self.assertIs(adapter.canonical_response(result)["is_error"], True)
        passed = [
            {"resultType": "success", "textResultForLlm": "\n<shellId: 0 completed with exit code 0>"},
            {"stdout": "loaded 100 records", "stderr": "", "is_error": False},
            "done",
        ]
        for result in passed:
            with self.subTest(result=result):
                self.assertIs(adapter.canonical_response(result)["is_error"], False)

    def test_a_tool_result_reaches_the_scripts_in_the_canonical_shape(self):
        payload = {"toolName": "bash", "toolArgs": {"command": "python3 src/load/load.py"},
                   "toolResult": {"resultType": "success", "textResultForLlm": "<shellId: 0 completed with exit code 1>"}}
        (canonical,) = self.payloads("post_tool_use", payload, {"script": "x.py", "tools": ["shell"]})
        self.assertEqual(set(canonical["tool_response"]), {"stdout", "stderr", "is_error"})
        self.assertIs(canonical["tool_response"]["is_error"], True)

    def test_the_stop_payload_carries_the_final_message_and_the_loop_guard(self):
        (canonical,) = self.payloads("stop", {"stopHookActive": True, "lastAssistantMessage": "Done."})
        self.assertIs(canonical["stop_hook_active"], True)
        self.assertEqual(canonical["last_assistant_message"], "Done.")

    def test_a_stop_payload_without_the_guard_is_not_active(self):
        (canonical,) = self.payloads("stop", {})
        self.assertIs(canonical["stop_hook_active"], False)
        self.assertNotIn("last_assistant_message", canonical)


class Results(unittest.TestCase):
    def merged(self, *runs):
        result = adapter.Result()
        for run in runs:
            result.add(run)
        return result

    def written(self, event, result, dialect):
        out, err = io.StringIO(), io.StringIO()
        code = adapter.write_result(event, result, dialect, out, err)
        return code, out.getvalue(), err.getvalue()

    def test_contexts_from_several_scripts_are_merged(self):
        result = self.merged(
            completed(json.dumps({"hookSpecificOutput": {"additionalContext": "one"}})),
            completed("plain text context"),
            completed(""),
        )
        self.assertEqual(result.context, ["one", "plain text context"])

    def test_exit_code_two_is_a_denial_with_stderr_as_the_reason(self):
        self.assertEqual(self.merged(completed(returncode=2, stderr="outside the project\n")).deny,
                         "outside the project")

    def test_a_crashed_script_is_ignored_rather_than_blocking(self):
        result = self.merged(completed(returncode=1, stderr="Traceback"))
        self.assertIsNone(result.deny)
        self.assertEqual(result.context, [])

    def test_each_dialect_writes_context_its_own_way(self):
        result = self.merged(completed("resume from Data collection"))
        expected = {
            "canonical": {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                                 "additionalContext": "resume from Data collection"}},
            "flat": {"additionalContext": "resume from Data collection"},
            "steps": {"injectSteps": [{"userMessage": "resume from Data collection"}]},
        }
        for dialect, body in expected.items():
            with self.subTest(dialect=dialect):
                code, out, _ = self.written("session_start", result, dialect)
                self.assertEqual((code, json.loads(out)), (0, body))
        self.assertEqual(self.written("session_start", result, "text"),
                         (0, "resume from Data collection\n", ""))

    def test_each_dialect_denies_its_own_way(self):
        result = self.merged(completed(returncode=2, stderr="no"))
        self.assertEqual(self.written("pre_tool_use", result, "canonical"), (2, "", "no\n"))
        self.assertEqual(self.written("pre_tool_use", result, "text"), (2, "", "no\n"))
        code, out, _ = self.written("pre_tool_use", result, "flat")
        self.assertEqual((code, json.loads(out)),
                         (0, {"permissionDecision": "deny", "permissionDecisionReason": "no"}))
        code, out, _ = self.written("pre_tool_use", result, "steps")
        self.assertEqual((code, json.loads(out)), (0, {"decision": "deny", "reason": "no"}))

    def test_each_dialect_holds_a_stop_its_own_way(self):
        result = self.merged(completed(json.dumps({"decision": "block", "reason": "ask the question"})))
        for dialect, body in (("canonical", {"decision": "block", "reason": "ask the question"}),
                              ("flat", {"decision": "block", "reason": "ask the question"}),
                              ("steps", {"decision": "continue", "reason": "ask the question"})):
            with self.subTest(dialect=dialect):
                code, out, _ = self.written("stop", result, dialect)
                self.assertEqual((code, json.loads(out)), (0, body))

    def test_an_assistant_that_cannot_hold_a_stop_is_left_alone(self):
        result = self.merged(completed(json.dumps({"decision": "block", "reason": "ask"})))
        self.assertEqual(self.written("stop", result, "text"), (0, "", ""))

    def test_the_steps_dialect_always_writes_an_object(self):
        self.assertEqual(self.written("post_tool_use", adapter.Result(), "steps"), (0, "{}\n", ""))

    def test_nothing_to_say_writes_nothing_elsewhere(self):
        for dialect in ("canonical", "flat", "text"):
            with self.subTest(dialect=dialect):
                self.assertEqual(self.written("prompt_submit", adapter.Result(), dialect), (0, "", ""))


class Transcripts(unittest.TestCase):
    def test_an_event_data_transcript_is_rewritten_in_the_canonical_shape(self):
        with tempfile.TemporaryDirectory() as scratch:
            source = Path(scratch) / "events.jsonl"
            source.write_text(
                json.dumps({"type": "user.message", "data": {"content": "yes"}}) + "\n"
                + json.dumps({"type": "tool.call", "data": {}}) + "\n"
                + "not json\n"
                + json.dumps({"type": "assistant.message", "data": {"content": [{"type": "text", "text": "ok"}]}}) + "\n",
                encoding="utf-8")
            path, temporary = adapter.canonical_transcript(str(source), "event-data")
            self.addCleanup(os.unlink, path)
            self.assertTrue(temporary)
            records = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
        self.assertEqual(records, [
            {"type": "user", "message": {"content": "yes"}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "ok"}]}},
        ])

    def test_a_canonical_transcript_is_used_as_it_is(self):
        self.assertEqual(adapter.canonical_transcript("/x/t.jsonl", "canonical"), ("/x/t.jsonl", False))

    def test_an_unknown_dialect_gives_the_scripts_no_transcript(self):
        self.assertEqual(adapter.canonical_transcript("/x/t.jsonl", "mystery"), (None, False))


class FinalMessage(unittest.TestCase):
    """The stop hook can run before the turn's last message is written (Copilot CLI)."""

    def transcript(self, *events):
        handle = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
        with handle:
            for event in events:
                handle.write(json.dumps(event) + "\n")
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_the_last_message_of_the_current_turn_is_returned(self):
        path = self.transcript(
            {"type": "user.message", "data": {"content": "earlier"}},
            {"type": "assistant.message", "data": {"content": "old reply"}},
            {"type": "user.message", "data": {"content": "hello"}},
            {"type": "assistant.message", "data": {"content": ""}},
            {"type": "assistant.message", "data": {"content": "Welcome back!"}})
        self.assertEqual(adapter.final_message(path, "event-data", 0), "Welcome back!")

    def test_a_message_that_is_not_there_yet_is_waited_for_then_given_up_on(self):
        path = self.transcript({"type": "user.message", "data": {"content": "hello"}})
        self.assertIsNone(adapter.final_message(path, "event-data", 0.1))

    def test_a_reply_from_an_earlier_turn_is_never_used(self):
        path = self.transcript(
            {"type": "assistant.message", "data": {"content": "old reply"}},
            {"type": "user.message", "data": {"content": "hello"}})
        self.assertIsNone(adapter.final_message(path, "event-data", 0))

    def test_other_dialects_are_left_to_the_scripts(self):
        self.assertIsNone(adapter.final_message("/x/t.jsonl", "canonical", 0))


class ProjectDirectory(unittest.TestCase):
    def test_the_payload_wins_over_the_working_directory(self):
        with tempfile.TemporaryDirectory() as project, tempfile.TemporaryDirectory() as package:
            found = adapter.project_dir({"cwd": project}, {}, Path(package).resolve())
            self.assertEqual(found, Path(project).resolve())

    def test_a_directory_inside_the_package_is_never_the_project(self):
        with tempfile.TemporaryDirectory() as package:
            inside = Path(package) / "scripts"
            inside.mkdir()
            original = os.getcwd()
            os.chdir(inside)
            self.addCleanup(os.chdir, original)
            self.assertIsNone(adapter.project_dir({"cwd": str(inside)}, {}, Path(package).resolve()))


class EndToEnd(unittest.TestCase):
    """The adapter as an assistant runs it: a process, a payload on stdin, a result on stdout."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scripts = Path(scratch.name) / "package" / "scripts"
        self.scripts.mkdir(parents=True)
        self.project = Path(scratch.name) / "project"
        self.project.mkdir()
        shutil.copy(ADAPTER, self.scripts / "hook_adapter.py")
        (self.scripts / "echo.py").write_text(
            "import json, sys\n"
            "payload = json.load(sys.stdin)\n"
            "print(json.dumps({'hookSpecificOutput': {'additionalContext': payload['prompt'].upper()}}))\n")
        (self.scripts / "gate.py").write_text(
            "import json, sys\n"
            "payload = json.load(sys.stdin)\n"
            "if payload['tool_input']['file_path'].startswith('/tmp'):\n"
            "    sys.stderr.write('keep files in the project')\n"
            "    sys.exit(2)\n")
        (self.scripts / "bootcamp_host.json").write_text(json.dumps({
            "host": "example", "result_dialect": "flat", "scripts_dir": "scripts",
            "tool_categories": CATEGORIES,
            "hooks": {"prompt_submit": [{"script": "echo.py"}],
                      "pre_tool_use": [{"script": "gate.py", "tools": ["write", "edit"]}]},
        }))

    def run_adapter(self, event, payload):
        return subprocess.run(
            [sys.executable, str(self.scripts / "hook_adapter.py"), event],
            input=json.dumps(payload), text=True, capture_output=True, cwd=self.project, check=False)

    def test_context_from_a_script_reaches_the_assistant(self):
        done = self.run_adapter("prompt_submit", {"userPrompt": "start the bootcamp"})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout), {"additionalContext": "START THE BOOTCAMP"})

    def test_a_denied_write_reaches_the_assistant_in_its_dialect(self):
        done = self.run_adapter("pre_tool_use", {"toolName": "create", "toolArgs": {"path": "/tmp/x", "content": ""}})
        self.assertEqual(json.loads(done.stdout),
                         {"permissionDecision": "deny", "permissionDecisionReason": "keep files in the project"})

    def test_an_allowed_write_says_nothing(self):
        done = self.run_adapter("pre_tool_use", {"toolName": "create", "toolArgs": {"path": "src/x.py", "content": ""}})
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_a_broken_payload_never_breaks_the_assistant(self):
        done = subprocess.run(
            [sys.executable, str(self.scripts / "hook_adapter.py"), "pre_tool_use"],
            input="{not json", text=True, capture_output=True, cwd=self.project, check=False)
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_an_unknown_event_never_breaks_the_assistant(self):
        done = self.run_adapter("no_such_event", {})
        self.assertEqual((done.returncode, done.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
