"""The hooks and the hook adapter give the same result whatever Python's I/O encoding is (#25).

On Windows, Python's standard streams take a legacy code page such as cp1252 unless UTF-8 is
asked for. Three hooks read their payload through a text-mode ``sys.stdin``, so a payload
holding a right double quotation mark (U+201D, whose UTF-8 bytes include 0x9D, a byte cp1252
cannot decode) made ``write-gate.py`` exit 1 where it had to block. ``stop-nudge.py`` could
not print its own 👉. ``session-start.py`` printed its em dash as byte 0x97, the adapter's
UTF-8 decode of that failed, and the adapter ended quietly with the hook's exit code lost. A
write the gate refused was then allowed through all four packages that run the adapter.

⛔ **(INV-454) A hook script and the hook adapter give the same exit code and the same bytes on stdout and stderr whatever Python's I/O encoding is.**

How the scripts keep that rule: a payload is read as bytes and decoded as UTF-8, every JSON
they write is ASCII-escaped, and plain text and stderr are written as UTF-8 bytes. Text that
is not valid UTF-8 (a payload, a hook's output, a transcript, a preferences file) is read with
replacement characters or treated as unreadable. It never produces a traceback and never
loses a block. Nor does a lone surrogate, which is valid JSON and cannot be encoded as UTF-8.

**What runs here.** Every case starts a hook script from ``source/scripts/``, or the hook
adapter of a freshly built package, as its own process, the way an assistant does, with
``PYTHONIOENCODING`` set to ``cp1252`` and again set to ``utf-8``, and compares exit code,
stdout bytes and stderr bytes. The other hook tests pin ``PYTHONIOENCODING=utf-8`` and cannot
see any of this.

**What this cannot establish.** This is a simulation on the machine that runs the suite. No
case runs on Windows, and nothing here is evidence of a run on a real assistant.
``PYTHONIOENCODING`` changes the three standard streams and nothing else: the encoding
``open()`` uses when none is named, and the one ``subprocess`` uses for ``text=True``, follow
the locale and are not simulated.

**Negative controls, 2026-11-17.** Run against the scripts as they were before #25, 19 of
this module's 24 tests fail (``FAILED (failures=47, errors=2)``). The five that pass are the
two checks of the simulation, the scenario-coverage check, the four-dialects check and the
readable-transcript control. Then, with one pre-#25 line restored at a time in the fixed
scripts, each of 17 mutations fails at least one test. Two changes have no failing control,
because the text they write is ASCII today: the write gate's block message and the
pre-compact reminder.

Standard library only, and nothing under ``source/`` is imported (INV-108).

Source issue: #25.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _built import built

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "source" / "scripts"
DECLARATION = REPO_ROOT / "source" / "bootcamp.json"
ADAPTER = REPO_ROOT / "hosts" / "_shared" / "hook_adapter.py"

#: The legacy code page simulated, and the encoding every result is compared with.
LEGACY = "cp1252"
UTF8 = "utf-8"

QUOTE = "”"  # right double quotation mark; UTF-8 e2 80 9d, and cp1252 has no 0x9d
POINTER = "\U0001f449"  # 👉, which cp1252 cannot encode
EM_DASH = "—"  # cp1252 encodes it as the single byte 0x97, which is not valid UTF-8
REPLACEMENT = "�"

#: The text every payload carries somewhere: both characters the issue names.
BOTH = "it said “done" + QUOTE + " " + POINTER

#: The packages that run the hooks through the adapter.
ADAPTED_HOSTS = ("copilot", "chatgpt", "gemini", "kiro")

OPT_OUT_ENV = "SENZING_BOOTCAMP_DISABLE_STOP_NUDGE"
DEBUG_ENV = "SENZING_BOOTCAMP_HOOK_DEBUG"
#: Variables that would change what a hook or the adapter does, removed from every run.
SCRUBBED = (OPT_OUT_ENV, DEBUG_ENV, "CLAUDE_PROJECT_DIR", "PROJECT_DIR", "WORKSPACE_DIR",
            "USER_PROMPT", "PYTHONUTF8")

#: A path in system temp and outside every project these tests make.
TEMP_TARGET = "/tmp/bootcamp-legacy-code-page.txt"
#: Text shaped like an AWS access-key ID, built here so no file holds one.
SECRET_SHAPED = "AKIA" + "A" * 16

#: A bootcamp in progress, in an Act 2 module, with a completed directing module whose
#: directing step is unset and a container whose runtime no CLI here serves, so every hook
#: has something to say and no container command is run.
IN_PROGRESS = {
    "current_module": "data_processing",
    "current_step": 3,
    "modules_completed": ["data_quality_mapping"],
    "docker_containers": [{"name": "senzing-postgres", "runtime": "no-such-runtime"}],
}

#: The previous turn: it showed a module number and ended on the pinned transition question.
PREVIOUS_TURN = (
    {"type": "user", "message": {"content": "Yes, " + BOTH}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": (
        "That finishes Module 5 " + EM_DASH + " well done.\n\n" + POINTER
        + " **Are you ready to move on to the next module: Data processing?**")}]}},
    {"type": "user", "message": {"content": "yes"}},
)

#: A settled turn whose final message asks nothing, read when the payload carries no message.
NO_POINTER_TURN = (
    {"type": "user", "message": {"content": "I have finished."}},
    {"type": "assistant", "message": {"content": [
        {"type": "text", "text": "Your document is saved " + QUOTE + "as asked" + QUOTE + "."}]}},
)

#: Bytes no text encoding of a transcript produces.
BINARY = bytes(range(256)) * 4 + b"\x9d\x81\xff\xfe\n"


def raw(payload):
    """A payload as an assistant sends it: UTF-8 JSON with its characters unescaped."""
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def run_process(argv, stdin, cwd, encoding, env=None):
    """Run ``argv`` with ``encoding`` as Python's I/O encoding. Returns
    ``(exit code, stdout bytes, stderr bytes)``."""
    run_env = dict(os.environ)
    for name in SCRUBBED:
        run_env.pop(name, None)
    run_env["PYTHONIOENCODING"] = encoding
    if env:
        run_env.update(env)
    done = subprocess.run([sys.executable] + [str(arg) for arg in argv], input=stdin,
                          cwd=str(cwd), capture_output=True, env=run_env, check=False)
    return done.returncode, done.stdout, done.stderr


class ProjectCase(unittest.TestCase):
    """A bootcamp project at one path, rebuilt before each run so two runs start alike."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.project = Path(scratch.name).resolve() / "project"
        self.transcript = self.project / "transcript.jsonl"

    def make_project(self, progress=IN_PROGRESS, turn=PREVIOUS_TURN, docs_is_a_file=False,
                     preferences=None, transcript_bytes=None):
        shutil.rmtree(self.project, ignore_errors=True)
        (self.project / "config").mkdir(parents=True)
        (self.project / "config" / "bootcamp_progress.json").write_text(
            json.dumps(progress), encoding="utf-8")
        if preferences is not None:
            (self.project / "config" / "bootcamp_preferences.yaml").write_bytes(preferences)
        if transcript_bytes is None:
            transcript_bytes = b"".join(raw(record) + b"\n" for record in turn)
        self.transcript.write_bytes(transcript_bytes)
        if docs_is_a_file:
            # Nothing can be created under docs/, so the checkpoint's own failure report
            # (which holds an em dash) is what reaches stderr.
            (self.project / "docs").write_text("not a directory\n", encoding="utf-8")

    def run_fresh(self, argv, stdin, encoding, env=None, **project):
        self.make_project(**project)
        return run_process(argv, stdin, self.project, encoding, env=env)

    def both(self, argv, stdin, env=None, **project):
        """The same run under UTF-8 and under the legacy code page, each on a fresh project."""
        return (self.run_fresh(argv, stdin, UTF8, env=env, **project),
                self.run_fresh(argv, stdin, LEGACY, env=env, **project))

    def assert_same(self, argv, stdin, env=None, **project):
        """Assert both runs match byte for byte and neither printed a traceback. Returns the
        one result."""
        expected, legacy = self.both(argv, stdin, env=env, **project)
        for label, (_, _, err) in (("utf-8", expected), (LEGACY, legacy)):
            self.assertNotIn(b"Traceback", err, "a traceback under %s" % label)
        self.assertEqual(
            legacy, expected,
            "(exit code, stdout, stderr) under %s differs from the same run under UTF-8"
            % LEGACY)
        return expected


class TheSimulationIsReal(unittest.TestCase):
    """Without these two, every comparison below could pass for the wrong reason."""

    def test_the_legacy_setting_reaches_all_three_streams(self):
        code, out, _ = run_process(
            ["-c", "import sys; print(sys.stdin.encoding, sys.stdout.encoding, sys.stderr.encoding)"],
            b"", REPO_ROOT, LEGACY)
        self.assertEqual((code, out.split()), (0, [b"cp1252"] * 3))

    def test_the_payload_text_is_what_the_legacy_code_page_cannot_carry(self):
        self.assertIn(b"\x9d", raw({"text": BOTH}))
        with self.assertRaises(UnicodeDecodeError):
            raw({"text": QUOTE}).decode(LEGACY)
        with self.assertRaises(UnicodeEncodeError):
            POINTER.encode(LEGACY)
        with self.assertRaises(UnicodeDecodeError):
            EM_DASH.encode(LEGACY).decode(UTF8)


class EveryHookScript(ProjectCase):
    """Criterion 1: each of the ten hook scripts, same exit code, stdout and stderr."""

    def scenarios(self):
        """``label: (script, payload, expected exit code, speaks on stdout, speaks on stderr,
        project)``. Every payload holds U+201D and 👉."""
        transcript = str(self.transcript)
        prompt = {"hook_event_name": "UserPromptSubmit", "cwd": str(self.project),
                  "transcript_path": transcript}
        return {
            "session start": ("session-start.py",
                              {"hook_event_name": "SessionStart", "source": BOTH},
                              0, True, True, {}),
            "session start, checkpoint cannot be created": (
                "session-start.py", {"hook_event_name": "SessionStart", "source": BOTH},
                0, True, True, {"docs_is_a_file": True}),
            "feedback": ("feedback-capture.py",
                         dict(prompt, prompt="I have some feedback about the bootcamp: " + BOTH),
                         0, True, False, {}),
            "checkpoint tick": ("checkpoint-tick.py", dict(prompt, prompt=BOTH),
                                0, True, True, {}),
            "checkpoint tick, checkpoint cannot be created": (
                "checkpoint-tick.py", dict(prompt, prompt=BOTH),
                0, True, True, {"docs_is_a_file": True}),
            "module start reminder": ("module-start-reminder.py", dict(prompt, prompt=BOTH),
                                      0, True, False, {}),
            "module number reminder": ("module-number-reminder.py", dict(prompt, prompt=BOTH),
                                       0, True, False, {}),
            "write gate, temp path": (
                "write-gate.py",
                {"hook_event_name": "PreToolUse", "tool_name": "Write",
                 "tool_input": {"file_path": TEMP_TARGET, "content": BOTH}},
                2, False, True, {}),
            "write gate, allowed": (
                "write-gate.py",
                {"hook_event_name": "PreToolUse", "tool_name": "Write",
                 "tool_input": {"file_path": "docs/notes.md", "content": BOTH}},
                0, False, False, {}),
            "failed run net": (
                "failed-run-net.py",
                {"hook_event_name": "PostToolUseFailure", "tool_name": "Bash",
                 "tool_input": {"command": "python3 src/load/load.py"},
                 "error": "Exit code 1\nValueError: " + BOTH},
                0, True, False, {}),
            "stop nudge, no question asked": (
                "stop-nudge.py",
                {"hook_event_name": "Stop", "stop_hook_active": False,
                 "last_assistant_message": "Saved " + QUOTE + "it" + QUOTE + ".",
                 "note": BOTH},
                0, True, False, {}),
            "stop nudge, question asked": (
                "stop-nudge.py",
                {"hook_event_name": "Stop", "stop_hook_active": False,
                 "last_assistant_message": BOTH + " **Ready?**"},
                0, False, False, {}),
            "pre-compact": ("precompact-recap.py",
                            {"hook_event_name": "PreCompact", "custom_instructions": BOTH},
                            0, True, True, {}),
            "session end": ("session-end.py",
                            {"hook_event_name": "SessionEnd", "reason": BOTH},
                            0, False, True, {}),
        }

    def test_the_scenarios_cover_the_ten_declared_hook_scripts(self):
        declared = {hook["script"]
                    for hook in json.loads(DECLARATION.read_text(encoding="utf-8"))["hooks"]}
        self.assertEqual(len(declared), 10, sorted(declared))
        self.assertEqual({scenario[0] for scenario in self.scenarios().values()}, declared)

    def test_each_hook_gives_the_same_result_under_the_legacy_code_page(self):
        for label, (script, payload, code, on_out, on_err, project) in self.scenarios().items():
            with self.subTest(hook=label):
                stdin = raw(payload)
                self.assertIn(QUOTE.encode(UTF8), stdin)
                self.assertIn(POINTER.encode(UTF8), stdin)
                got_code, out, err = self.assert_same([SCRIPTS / script], stdin, **project)
                # The comparison means something only when the hook did what the scenario is for.
                self.assertEqual(got_code, code, err.decode(UTF8, "replace"))
                self.assertEqual(bool(out), on_out, out)
                self.assertEqual(bool(err), on_err, err)

    def test_plain_text_and_stderr_are_utf8_and_json_is_ascii(self):
        """The three output rules, each read off a hook that has non-ASCII text to write."""
        start = SCRIPTS / "session-start.py"
        _, out, _ = self.run_fresh([start], b"{}", LEGACY)
        text = out.decode(UTF8)  # raises when the em dash was written as byte 0x97
        self.assertIn("A Senzing bootcamp is in progress", text)
        self.assertIn(EM_DASH, text)

        _, _, err = self.run_fresh([start], b"{}", LEGACY, docs_is_a_file=True)
        self.assertIn(EM_DASH, err.decode(UTF8))

        _, out, _ = self.run_fresh(
            [SCRIPTS / "stop-nudge.py"], raw({"last_assistant_message": "Saved."}), LEGACY)
        self.assertTrue(out.isascii(), out)
        self.assertIn(POINTER, json.loads(out)["reason"])


class TheWriteGate(ProjectCase):
    """Criteria 2 and 8: the gate blocks, run directly."""

    GATE = SCRIPTS / "write-gate.py"

    def write(self, file_path, content):
        return {"hook_event_name": "PreToolUse", "tool_name": "Write",
                "tool_input": {"file_path": file_path, "content": content}}

    def test_a_temp_path_write_holding_the_quote_is_blocked(self):
        for encoding in (LEGACY, UTF8):
            with self.subTest(encoding=encoding):
                code, out, err = self.run_fresh(
                    [self.GATE], raw(self.write(TEMP_TARGET, BOTH)), encoding)
                self.assertEqual((code, out), (2, b""), err)
                self.assertIn(b"system temp", err)

    def test_a_secret_shaped_write_holding_the_quote_is_blocked(self):
        for encoding in (LEGACY, UTF8):
            with self.subTest(encoding=encoding):
                code, out, err = self.run_fresh(
                    [self.GATE], raw(self.write("config/settings.txt", BOTH + SECRET_SHAPED)),
                    encoding)
                self.assertEqual((code, out), (2, b""), err)
                self.assertIn(b"hardcoded secret", err)

    def test_an_in_project_write_holding_the_quote_is_allowed(self):
        """The control: the gate is not blocking everything it cannot read."""
        self.assertEqual(
            self.run_fresh([self.GATE], raw(self.write("docs/notes.md", BOTH)), LEGACY),
            (0, b"", b""))

    def test_a_payload_that_is_not_valid_utf8_is_still_judged(self):
        """0xE9 alone is not valid UTF-8. The gate decodes with replacement characters and
        then judges the path and the secret patterns as usual."""
        temp = raw(self.write(TEMP_TARGET, "caf?")).replace(b"?", b"\xe9")
        secret = raw(self.write("config/settings.txt", "caf? " + SECRET_SHAPED)).replace(b"?", b"\xe9")
        allowed = raw(self.write("docs/notes.md", "caf?")).replace(b"?", b"\xe9")
        for stdin in (temp, secret, allowed):
            with self.assertRaises(UnicodeDecodeError):
                stdin.decode(UTF8)
        for encoding in (UTF8, LEGACY):
            with self.subTest(encoding=encoding):
                code, _, err = self.run_fresh([self.GATE], temp, encoding)
                self.assertEqual(code, 2, err)
                self.assertIn(b"system temp", err)
                code, _, err = self.run_fresh([self.GATE], secret, encoding)
                self.assertEqual(code, 2, err)
                self.assertIn(b"hardcoded secret", err)
                self.assertEqual(self.run_fresh([self.GATE], allowed, encoding), (0, b"", b""))


class TheStopNudge(ProjectCase):
    """Criteria 5, 6 and 7."""

    NUDGE = SCRIPTS / "stop-nudge.py"
    ACTIVE = {"current_module": "data_processing"}

    def test_a_pointer_in_the_final_message_is_seen(self):
        asked = raw({"last_assistant_message": "Loaded.\n\n" + POINTER + " **Ready " + QUOTE + "?**"})
        self.assertEqual(self.run_fresh([self.NUDGE], asked, LEGACY, progress=self.ACTIVE),
                         (0, b"", b""))

    def test_the_block_decision_is_the_one_utf8_gives(self):
        paused = raw({"last_assistant_message": "I stopped " + QUOTE + "here" + QUOTE + "."})
        expected, legacy = self.both([self.NUDGE], paused, progress=self.ACTIVE)
        self.assertEqual(legacy, expected)
        code, out, err = legacy
        self.assertEqual((code, err), (0, b""))
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        self.assertIn(POINTER, decision["reason"])
        self.assertEqual(decision["reason"], json.loads(expected[1])["reason"])

    def test_a_binary_transcript_is_undecided_and_silent(self):
        payload = raw({"transcript_path": str(self.transcript), "note": BOTH})
        for encoding in (LEGACY, UTF8):
            with self.subTest(encoding=encoding):
                # The control: the same payload over a readable transcript blocks.
                code, out, err = self.run_fresh([self.NUDGE], payload, encoding,
                                                progress=self.ACTIVE, turn=NO_POINTER_TURN)
                self.assertEqual((code, err), (0, b""))
                self.assertEqual(json.loads(out)["decision"], "block")
                self.assertEqual(
                    self.run_fresh([self.NUDGE], payload, encoding, progress=self.ACTIVE,
                                   transcript_bytes=BINARY),
                    (0, b"", b""))

    def test_a_preferences_file_that_is_not_utf8_neither_raises_nor_loses_the_opt_out(self):
        """``Jos\\xe9`` is "José" saved as cp1252, and is not valid UTF-8."""
        paused = raw({"last_assistant_message": "I stopped here.", "note": BOTH})
        name_only = b"name: Jos\xe9\n"
        opted_out = b"name: Jos\xe9\ndisable_stop_nudge: true\n"
        finished = b"name: Jos\xe9\nbootcamp_complete: true\n"
        for content in (name_only, opted_out, finished):
            with self.assertRaises(UnicodeDecodeError):
                content.decode(UTF8)
        for encoding in (LEGACY, UTF8):
            with self.subTest(encoding=encoding):
                # The control: the undecodable file alone does not silence the hook.
                code, out, err = self.run_fresh([self.NUDGE], paused, encoding,
                                                progress=self.ACTIVE, preferences=name_only)
                self.assertEqual((code, err), (0, b""))
                self.assertEqual(json.loads(out)["decision"], "block")
                self.assertEqual(
                    self.run_fresh([self.NUDGE], paused, encoding, progress=self.ACTIVE,
                                   preferences=opted_out),
                    (0, b"", b""))
                # The same file's other ASCII key, read by the shared finished-bootcamp rule.
                self.assertEqual(
                    self.run_fresh([self.NUDGE], paused, encoding, progress=self.ACTIVE,
                                   preferences=finished),
                    (0, b"", b""))


def adapter_of(host):
    """``(adapter path, its bootcamp_host.json)`` in ``host``'s freshly built package."""
    root = built(host)
    found = sorted(root.rglob("hook_adapter.py"))
    if len(found) != 1:
        raise AssertionError("%s carries %d hook adapters" % (host, len(found)))
    config = json.loads((found[0].parent / "bootcamp_host.json").read_text(encoding="utf-8"))
    return found[0], config


def denial(dialect, result):
    """The reason a result gives for denying a tool call, read the way an assistant with
    ``dialect`` reads it, or None when the call is allowed."""
    code, out, err = result
    if dialect in ("canonical", "text"):
        return err.decode(UTF8).strip() if code == 2 else None
    if code != 0 or not out.strip():
        return None
    body = json.loads(out)
    if dialect == "flat":
        return body.get("permissionDecisionReason") if body.get("permissionDecision") == "deny" else None
    if dialect == "steps":
        return body.get("reason") if body.get("decision") == "deny" else None
    raise AssertionError("unknown result dialect %r" % dialect)


def context(dialect, result):
    """The context a result hands the assistant, read the way ``dialect`` is read."""
    code, out, _ = result
    if code != 0 or not out.strip():
        return None
    if dialect == "text":
        return out.decode(UTF8).strip()
    body = json.loads(out)
    if dialect == "flat":
        return body.get("additionalContext")
    if dialect == "steps":
        steps = body.get("injectSteps") or [{}]
        return steps[0].get("userMessage")
    return (body.get("hookSpecificOutput") or {}).get("additionalContext")


def held_stop(dialect, result):
    """The reason a result gives for holding a stop, or None."""
    code, out, _ = result
    if dialect == "text" or code != 0 or not out.strip():
        return None
    body = json.loads(out)
    wanted = "continue" if dialect == "steps" else "block"
    return body.get("reason") if body.get("decision") == wanted else None


class ThroughEachBuiltPackage(ProjectCase):
    """Criteria 3 and 4: the four packages that run the hooks through the adapter."""

    def write_call(self, config, file_path, content):
        """A write, named as this package's assistant names it."""
        name = config["host_tools"]["write"]
        self.assertEqual(config["tool_categories"].get(name), "write",
                         "%s is not a tool this package's tool_categories maps to write" % name)
        return raw({"cwd": str(self.project), "tool_name": name,
                    "tool_input": {"file_path": file_path, "content": content}})

    def test_the_four_packages_use_four_result_dialects(self):
        dialects = {adapter_of(host)[1]["result_dialect"] for host in ADAPTED_HOSTS}
        self.assertEqual(dialects, {"flat", "canonical", "steps", "text"})

    def test_a_temp_path_write_and_a_secret_shaped_write_are_denied(self):
        for host in ADAPTED_HOSTS:
            adapter, config = adapter_of(host)
            dialect = config["result_dialect"]
            writes = {
                "system temp": self.write_call(config, TEMP_TARGET, BOTH),
                "hardcoded secret": self.write_call(config, "config/settings.txt",
                                                    BOTH + SECRET_SHAPED),
            }
            for words, stdin in writes.items():
                with self.subTest(host=host, dialect=dialect, write=words):
                    result = self.assert_same([adapter, "pre_tool_use"], stdin)
                    reason = denial(dialect, result)
                    self.assertIsNotNone(reason, "the write was allowed: %r" % (result,))
                    self.assertIn(words, reason)
            with self.subTest(host=host, dialect=dialect, write="in the project"):
                # The control: this package's adapter does not deny everything.
                allowed = self.assert_same(
                    [adapter, "pre_tool_use"], self.write_call(config, "docs/notes.md", BOTH))
                self.assertIsNone(denial(dialect, allowed))

    def test_a_lone_surrogate_in_the_payload_loses_no_block(self):
        """``\\ud83d`` alone is half of an emoji, as a cut-off message leaves it. It is valid
        JSON and cannot be encoded as UTF-8, so the adapter hands the scripts ASCII JSON."""
        for host in ADAPTED_HOSTS:
            adapter, config = adapter_of(host)
            name = config["host_tools"]["write"]
            stdin = json.dumps({"cwd": str(self.project), "tool_name": name, "tool_input": {
                "file_path": TEMP_TARGET, "content": "cut off \ud83d"}}).encode("ascii")
            self.assertIn(b"\\ud83d", stdin)
            with self.subTest(host=host):
                result = self.assert_same([adapter, "pre_tool_use"], stdin)
                self.assertIn("system temp", denial(config["result_dialect"], result) or "")

    def test_a_lone_surrogate_in_an_event_data_transcript_loses_no_block(self):
        """The adapter copies such a transcript for the scripts on every event, a tool call
        included, so a copy it cannot write would lose the block."""
        hosts = [host for host in ADAPTED_HOSTS
                 if adapter_of(host)[1].get("transcript_dialect") == "event-data"]
        self.assertTrue(hosts, "no package reads an event-data transcript")
        events = json.dumps({"type": "assistant.message",
                             "data": {"content": "cut off \ud83d"}}).encode("ascii") + b"\n"
        for host in hosts:
            adapter, config = adapter_of(host)
            stdin = raw({"cwd": str(self.project), "transcriptPath": str(self.transcript),
                         "tool_name": config["host_tools"]["write"],
                         "tool_input": {"file_path": TEMP_TARGET, "content": BOTH}})
            with self.subTest(host=host):
                result = self.assert_same([adapter, "pre_tool_use"], stdin,
                                          env={DEBUG_ENV: "1"}, transcript_bytes=events)
                self.assertIn("system temp", denial(config["result_dialect"], result) or "")

    def test_the_session_start_context_reaches_the_assistant(self):
        for host in ADAPTED_HOSTS:
            adapter, config = adapter_of(host)
            dialect = config["result_dialect"]
            with self.subTest(host=host, dialect=dialect):
                result = self.assert_same(
                    [adapter, "session_start"], raw({"cwd": str(self.project), "note": BOTH}))
                text = context(dialect, result)
                self.assertIsNotNone(text, "no session-start context: %r" % (result,))
                self.assertIn("A Senzing bootcamp is in progress", text)
                self.assertIn("Where you left off: Data processing, step 3", text)
                # Both em dashes: the resume message's own and the container summary's.
                self.assertIn("resumed module " + EM_DASH + " it is the only copy", text)
                self.assertIn("This bootcamp started container(s) " + EM_DASH, text)

    def test_a_held_stop_reaches_the_assistant_with_its_pointer(self):
        """The adapter's own output: a 👉 in a result it writes."""
        for host in ADAPTED_HOSTS:
            adapter, config = adapter_of(host)
            dialect = config["result_dialect"]
            stdin = raw({"cwd": str(self.project), "note": BOTH,
                         "last_assistant_message": "I stopped " + QUOTE + "here" + QUOTE + "."})
            with self.subTest(host=host, dialect=dialect):
                result = self.assert_same([adapter, "stop"], stdin)
                reason = held_stop(dialect, result)
                if dialect == "text":  # an assistant that cannot hold a stop is left alone
                    self.assertEqual(result, (0, b"", b""))
                else:
                    self.assertIsNotNone(reason, "the stop was not held: %r" % (result,))
                    self.assertIn(POINTER, reason)
                    self.assertTrue(result[1].isascii(), result[1])

    def test_an_event_data_transcript_that_is_not_utf8_ends_the_stop_quietly(self):
        """Criterion 10. Debug output is on, so a swallowed traceback would show."""
        hosts = [host for host in ADAPTED_HOSTS
                 if adapter_of(host)[1].get("transcript_dialect") == "event-data"]
        self.assertTrue(hosts, "no package reads an event-data transcript")
        for host in hosts:
            adapter, _ = adapter_of(host)
            stdin = raw({"cwd": str(self.project), "transcriptPath": str(self.transcript),
                         "note": BOTH})
            with self.subTest(host=host):
                self.assertEqual(
                    self.run_fresh([adapter, "stop"], stdin, LEGACY, env={DEBUG_ENV: "1"},
                                   transcript_bytes=BINARY),
                    (0, b"", b""))


class TheAdapterNeverLosesAnExitCode(ProjectCase):
    """Criterion 9, in every result dialect, with a stand-in for the hook script."""

    #: A hook that blocks with stderr that is not valid UTF-8, and one whose context is not.
    GATE = ("import sys\n"
            "sys.stdin.buffer.read()\n"
            "sys.stderr.buffer.write(b'keep files in the project \\xff\\x9d\\n')\n"
            "sys.exit(2)\n")
    TALKER = ("import sys\n"
              "sys.stdin.buffer.read()\n"
              "sys.stdout.buffer.write(b'resume from Data collection \\xff\\x9d\\n')\n")

    def package(self, dialect):
        scripts = self.project.parent / ("package-" + dialect) / "scripts"
        scripts.mkdir(parents=True)
        shutil.copy(ADAPTER, scripts / "hook_adapter.py")
        (scripts / "gate.py").write_text(self.GATE, encoding="utf-8")
        (scripts / "talker.py").write_text(self.TALKER, encoding="utf-8")
        (scripts / "bootcamp_host.json").write_text(json.dumps({
            "host": "example", "result_dialect": dialect, "scripts_dir": "scripts",
            "tool_categories": {"create": "write"},
            "hooks": {"pre_tool_use": [{"script": "gate.py", "tools": ["write"]}],
                      "session_start": [{"script": "talker.py"}]},
        }), encoding="utf-8")
        return scripts / "hook_adapter.py"

    def test_a_block_with_undecodable_stderr_is_still_a_denial(self):
        for dialect in ("flat", "canonical", "steps", "text"):
            adapter = self.package(dialect)
            stdin = raw({"cwd": str(self.project), "toolName": "create",
                         "toolArgs": {"path": "notes.md", "content": BOTH}})
            with self.subTest(dialect=dialect):
                result = self.assert_same([adapter, "pre_tool_use"], stdin)
                reason = denial(dialect, result)
                self.assertIsNotNone(reason, "the block was lost: %r" % (result,))
                self.assertIn("keep files in the project", reason)
                self.assertIn(REPLACEMENT, reason)

    def test_context_that_is_not_utf8_still_arrives(self):
        for dialect in ("flat", "canonical", "steps", "text"):
            adapter = self.package(dialect)
            with self.subTest(dialect=dialect):
                result = self.assert_same([adapter, "session_start"],
                                          raw({"cwd": str(self.project), "note": BOTH}))
                text = context(dialect, result)
                self.assertIsNotNone(text, "the context was lost: %r" % (result,))
                self.assertIn("resume from Data collection", text)
                self.assertIn(REPLACEMENT, text)


class TheAdapterReadsAnUndecodableTranscript(unittest.TestCase):
    """Criterion 10 from the inside: the read itself, not only the quiet ending."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("hook_adapter_legacy_code_page", ADAPTER)
        cls.adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.adapter)

    def test_final_message_treats_it_as_unreadable(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "events.jsonl"
            path.write_bytes(BINARY)
            self.assertIsNone(self.adapter.final_message(str(path), "event-data", 0))
            self.assertEqual(self.adapter.canonical_transcript(str(path), "event-data"),
                             (None, False))

    def test_a_readable_one_still_gives_the_message(self):
        """The control: the read is not returning None for everything."""
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "events.jsonl"
            path.write_bytes(
                raw({"type": "user.message", "data": {"content": "hello"}}) + b"\n"
                + raw({"type": "assistant.message", "data": {"content": BOTH}}) + b"\n")
            self.assertEqual(self.adapter.final_message(str(path), "event-data", 0), BOTH)


if __name__ == "__main__":
    unittest.main()
