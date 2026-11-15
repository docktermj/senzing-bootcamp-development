"""Hook payloads captured from real assistants, run through the adapter.

Each file under ``tests/fixtures/host-payloads/`` holds payloads an assistant actually sent,
recorded with a probe plugin and stripped of paths and identifiers. They are the evidence the
adapter's translation rests on: documentation described some of these shapes differently.
"""

import importlib.util
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "host-payloads"

_spec = importlib.util.spec_from_file_location("hook_adapter", REPO_ROOT / "hosts" / "_shared" / "hook_adapter.py")
adapter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(adapter)

#: The canonical event each of the assistant's own event names stands for.
COPILOT_EVENTS = {
    "sessionStart": "session_start", "userPromptSubmitted": "prompt_submit", "preToolUse": "pre_tool_use",
    "postToolUse": "post_tool_use", "agentStop": "stop", "sessionEnd": "session_end",
}


def load(name):
    return [json.loads(line) for line in (FIXTURES / name).read_text(encoding="utf-8").splitlines()]


class CopilotCli(unittest.TestCase):
    """Copilot CLI 1.0.111, captured 2026-11-14 with a plugin loaded by ``--plugin-dir``."""

    @classmethod
    def setUpClass(cls):
        cls.records = load("copilot-cli-1.0.111.jsonl")
        profile = json.loads((REPO_ROOT / "hosts" / "copilot" / "host.json").read_text(encoding="utf-8"))
        cls.profile = profile
        cls.config = profile["options"]["adapter"]

    def canonical(self, host_event, hook=None, index=0):
        payloads = [r["payload"] for r in self.records if r["event"] == host_event]
        return adapter.canonical_payloads(
            COPILOT_EVENTS[host_event], hook or {"script": "x.py", "tools": ["write", "edit", "shell"]},
            payloads[index], self.config, {}, Path("/work/project"))

    def test_the_profile_names_every_event_the_capture_saw(self):
        named = set(self.profile["hooks"]["events"].values())
        for record in self.records:
            self.assertIn(record["event"], named)

    def test_the_prompt_is_found(self):
        (payload,) = self.canonical("userPromptSubmitted")
        self.assertTrue(payload["prompt"].startswith("This is a short tooling check."))

    def test_a_file_creation_becomes_a_canonical_write_with_its_content(self):
        calls = [call for index in (0, 1) for call in self.canonical("preToolUse", index=index)]
        writes = [call for call in calls if call["tool_name"] == "Write"]
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0]["tool_input"]["file_path"], "/work/project/probe.txt")
        self.assertEqual(writes[0]["tool_input"]["content"], "hello\n")

    def test_a_shell_command_becomes_the_canonical_shell_tool(self):
        calls = [call for index in (0, 1) for call in self.canonical("preToolUse", index=index)]
        shells = [call for call in calls if call["tool_name"] == "Bash"]
        self.assertEqual([call["tool_input"]["command"] for call in shells], ["false"])

    def test_a_failed_command_is_reported_as_an_error(self):
        """Copilot fires no failure event: ``false`` arrives as a "success" whose text says exit code 1."""
        results = {}
        for index in (0, 1):
            for call in self.canonical("postToolUse", {"script": "x.py", "tools": ["shell"]}, index):
                results[call["tool_input"]["command"]] = call["tool_response"]["is_error"]
        self.assertEqual(results, {"false": True})

    def test_the_stop_payload_carries_the_loop_guard_and_a_transcript(self):
        (payload,) = self.canonical("agentStop")
        self.assertIs(payload["stop_hook_active"], False)
        self.assertTrue(payload["transcript_path"].endswith("events.jsonl"))
        self.assertNotIn("last_assistant_message", payload)

    def test_the_transcript_is_one_the_adapter_can_convert(self):
        self.assertEqual(self.config["transcript_dialect"], "event-data")


if __name__ == "__main__":
    unittest.main()
