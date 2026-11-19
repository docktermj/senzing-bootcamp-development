#!/usr/bin/env python3
"""Run the bootcamp's hooks on an assistant whose hook payloads are not the canonical ones.

    python3 hook_adapter.py <event>

The bootcamp's hook scripts are written once and speak one dialect: a canonical JSON payload
on stdin, and a canonical result on stdout or in the exit code. An assistant that speaks
another dialect has its hook configuration call this adapter instead of the scripts. The
adapter rewrites the assistant's payload in the canonical shape, runs every script the
bootcamp declares for the event, merges their results, and writes them in the assistant's
shape. The scripts themselves are the same files on every assistant.

``bootcamp_host.json``, beside this file, is written by the build and says which assistant
this is: its tool names, its result dialect, and the scripts each event runs.

A hook must never break the assistant it runs in. Anything that goes wrong here ends
quietly, allowing the action; set ``SENZING_BOOTCAMP_HOOK_DEBUG=1`` to see why on stderr.

Nothing here depends on the encoding the console gives Python (a legacy code page on
Windows; INV-454). The payload is read as bytes and decoded as UTF-8. Each script is given ASCII JSON
and its output is read as bytes, so its exit code is used even when that output is not valid
UTF-8. Every JSON this writes is ASCII-escaped, and plain text and stderr are written as
UTF-8 bytes.

Standard library only.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "bootcamp_host.json"
DEBUG_ENV = "SENZING_BOOTCAMP_HOOK_DEBUG"
SCRIPT_TIMEOUT_SECONDS = 30
FINAL_MESSAGE_WAIT_SECONDS = 2.0

#: The canonical name of each event, as the hook scripts read it in ``hook_event_name``.
CANONICAL_EVENT = {
    "session_start": "SessionStart",
    "prompt_submit": "UserPromptSubmit",
    "pre_tool_use": "PreToolUse",
    "post_tool_use": "PostToolUse",
    "post_tool_use_failure": "PostToolUseFailure",
    "stop": "Stop",
    "pre_compact": "PreCompact",
    "session_end": "SessionEnd",
}
TOOL_EVENTS = {"pre_tool_use", "post_tool_use", "post_tool_use_failure"}

#: The canonical tool name for each tool category the bootcamp's hooks can be limited to.
CANONICAL_TOOL = {"write": "Write", "edit": "Edit", "shell": "Bash"}

PROMPT_KEYS = ("prompt", "user_prompt", "userPrompt", "userMessage", "message")
PROJECT_KEYS = ("cwd", "workspace", "workspaceRoot", "workspace_root", "projectDir", "project_dir")
PROJECT_ENV = ("CLAUDE_PROJECT_DIR", "PROJECT_DIR", "WORKSPACE_DIR")
PATH_KEYS = ("file_path", "path", "filePath", "filename", "target_file", "absolute_path", "TargetFile")
TEXT_KEYS = ("content", "new_string", "new_str", "file_text", "text", "contents", "code_edit", "CodeContent")
COMMAND_KEYS = ("command", "cmd", "script", "commandLine", "CommandLine")
LAST_MESSAGE_KEYS = ("last_assistant_message", "lastAssistantMessage")
TRANSCRIPT_KEYS = ("transcript_path", "transcriptPath")
STOP_ACTIVE_KEYS = ("stop_hook_active", "stopHookActive")
RESPONSE_KEYS = ("tool_response", "toolResponse", "toolResult", "tool_result", "result")

PATCH_FILE_RE = re.compile(r"^\*\*\* (Add|Update|Delete) File: (.+?)\s*$")
EXIT_CODE_RE = re.compile(r"exit(?:ed with)? code:? (-?\d+)", re.IGNORECASE)
RESULT_TEXT_KEYS = ("stdout", "text_result_for_llm", "textResultForLlm", "output", "content", "text", "result")
RESULT_ERROR_KEYS = ("is_error", "isError", "error")
RESULT_KIND_KEYS = ("result_type", "resultType", "status")
FAILED_KINDS = ("failure", "failed", "error", "rejected", "denied")


def write_text(stream, text):
    """Write ``text`` to ``stream`` as UTF-8 bytes, whatever encoding the stream has.

    A Windows console gives ``sys.stdout`` and ``sys.stderr`` a legacy code page, which
    cannot write some characters and writes others as bytes that are not valid UTF-8. A
    character UTF-8 cannot encode (a lone surrogate) is written as a backslash escape. A
    stream with no ``buffer`` (a text buffer a caller passed in) is given the text itself.
    """
    raw = getattr(stream, "buffer", None)
    if raw is None:
        stream.write(text)
        return
    stream.flush()
    raw.write(text.encode("utf-8", errors="backslashreplace"))
    raw.flush()


def debug(message):
    if os.environ.get(DEBUG_ENV):
        write_text(sys.stderr, f"bootcamp hook adapter: {message}\n")


def first(mapping, keys, kind=str):
    """The first value of the wanted kind found under any of ``keys``."""
    if isinstance(mapping, dict):
        for key in keys:
            value = mapping.get(key)
            if isinstance(value, kind) and (value or kind is bool):
                return value
    return None


def load_config(path=CONFIG):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def read_payload(raw):
    """The assistant's payload as a dict. An empty or unreadable payload is an empty one."""
    try:
        value = json.loads(raw) if raw.strip() else {}
    except ValueError:
        return {}
    return value if isinstance(value, dict) else {}


def project_dir(payload, environ, package_root):
    """The bootcamper's project directory, or None when the assistant does not say.

    Some assistants run a hook with the package's own directory as the working directory, so
    the working directory is trusted only when it is not inside the package.
    """
    candidates = [first(payload, PROJECT_KEYS)]
    candidates += [environ.get(name) for name in PROJECT_ENV]
    candidates.append(os.getcwd())
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        if not path.is_dir():
            continue
        resolved = path.resolve()
        if resolved == package_root or package_root in resolved.parents:
            continue
        return resolved
    return None


# --- tool calls -------------------------------------------------------------------------


def parse_arguments(arguments):
    """Tool arguments as a dict when they are one (or JSON for one), else the raw text."""
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        try:
            value = json.loads(arguments)
        except ValueError:
            return arguments
        return value if isinstance(value, dict) else arguments
    return {}


def raw_tool_calls(payload):
    """``(name, arguments)`` for each tool call in a payload, in whichever shape it uses."""
    calls = payload.get("toolCalls") or payload.get("tool_calls")
    if isinstance(calls, list):
        found = []
        for call in calls:
            if isinstance(call, dict):
                name = first(call, ("name", "toolName", "tool_name"))
                if name:
                    arguments = next(
                        (call[key] for key in ("args", "arguments", "input", "toolArgs", "tool_input")
                         if key in call),
                        {},
                    )
                    found.append((name, arguments))
        return found
    for name_key, argument_key in (("tool_name", "tool_input"), ("toolName", "toolArgs"),
                                   ("tool", "input"), ("name", "args")):
        name = payload.get(name_key)
        if isinstance(name, str) and name:
            return [(name, payload.get(argument_key, {}))]
    return []


def patch_calls(text):
    """One canonical write per file a patch touches, carrying the lines the patch adds.

    The added lines are what a secret check must see; a deleted file writes nothing.
    """
    calls, current, added = [], None, []

    def flush():
        if current is not None:
            calls.append(("Write" if current[0] == "Add" else "Edit",
                          {"file_path": current[1], "content": "\n".join(added)}))

    for line in text.splitlines():
        header = PATCH_FILE_RE.match(line)
        if header:
            flush()
            current = None if header.group(1) == "Delete" else (header.group(1), header.group(2))
            added = []
        elif current is not None and line.startswith("+"):
            added.append(line[1:])
    flush()
    return calls


def canonical_calls(name, arguments, categories):
    """Canonical ``(tool_name, tool_input)`` pairs for one of the assistant's tool calls."""
    category = categories.get(name) or categories.get(name.lower())
    parsed = parse_arguments(arguments)
    patch_text = None
    if isinstance(parsed, str):
        patch_text = parsed
    elif category == "patch":
        patch_text = first(parsed, ("patch", "input", "command") + TEXT_KEYS)
    if patch_text is not None and (category == "patch" or "*** Begin Patch" in patch_text):
        return patch_calls(patch_text)
    if not isinstance(parsed, dict) or category not in CANONICAL_TOOL:
        return []
    if category == "shell":
        command = first(parsed, COMMAND_KEYS)
        return [("Bash", {"command": command})] if command else []
    path = first(parsed, PATH_KEYS)
    if not path:
        return []
    tool_input = dict(parsed)
    tool_input["file_path"] = path
    text = first(parsed, TEXT_KEYS)
    if text is not None:
        tool_input["content" if category == "write" else "new_string"] = text
    return [(CANONICAL_TOOL[category], tool_input)]


def shell_dialect(name, dialects):
    """The shell one of the assistant's shell tools runs, when its profile declares one.

    ``shell_dialects`` in the profile maps a tool name to a dialect (``"powershell"``). A tool
    it does not name declares none, and the hook scripts read its commands as POSIX shell.
    """
    dialect = dialects.get(name) or dialects.get(name.lower())
    return dialect if isinstance(dialect, str) else None


def canonical_response(raw):
    """A tool result in the canonical shape: ``{"stdout", "stderr", "is_error"}``.

    Assistants report a failed command differently: an error flag, a result kind, or only a
    sentence such as "completed with exit code 1" in the text. All three become ``is_error``,
    so the scripts never have to know which assistant ran the command.
    """
    if raw is None:
        return None
    if isinstance(raw, dict) and isinstance(raw.get("stdout"), str) and "is_error" in raw:
        return raw  # already canonical
    flagged = False
    stderr = ""
    if isinstance(raw, dict):
        text = first(raw, RESULT_TEXT_KEYS) or ""
        stderr = first(raw, ("stderr",)) or ""
        flagged = any(raw.get(key) is True for key in RESULT_ERROR_KEYS)
        kind = first(raw, RESULT_KIND_KEYS) or ""
        flagged = flagged or kind.lower() in FAILED_KINDS
    else:
        text = raw if isinstance(raw, str) else ""
    codes = EXIT_CODE_RE.findall(text + "\n" + stderr)
    return {"stdout": text, "stderr": stderr, "is_error": flagged or any(code != "0" for code in codes)}


# --- transcripts ------------------------------------------------------------------------


def canonical_transcript(path, dialect):
    """A transcript the hook scripts can read: ``path`` itself, or a canonical copy of it.

    The scripts read a JSON-lines transcript of ``{"type": "user"|"assistant", "message":
    {"content": ...}}`` records. ``event-data`` transcripts carry the same content as
    ``{"type": "user.message"|"assistant.message", "data": {"content": ...}}`` events.
    Returns ``(path, temporary)``; a temporary copy is the caller's to delete. The copy is
    ASCII JSON, like every other JSON this adapter writes: a lone surrogate in a message
    cannot be encoded as UTF-8, and failing on one here ended every event of the session
    quietly, a block included.
    """
    if not path or dialect in (None, "canonical"):
        return path, False
    if dialect != "event-data":
        return None, False
    records = []
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                kind = event.get("type") if isinstance(event, dict) else None
                if kind in ("user.message", "assistant.message"):
                    data = event.get("data")
                    content = data.get("content") if isinstance(data, dict) else None
                    records.append({"type": kind.split(".")[0], "message": {"content": content}})
    except (OSError, ValueError):
        return None, False
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=".jsonl", prefix="bootcamp-transcript-", delete=False)
    with handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
    return handle.name, True


def final_message(path, dialect, wait_seconds=FINAL_MESSAGE_WAIT_SECONDS):
    """The assistant's final text for the turn that is ending, read from an ``event-data`` transcript.

    Some assistants run the stop hook before the turn's last message is on disk, so a single
    read finds nothing and the closing-question check stays silent (seen in one assistant, where
    the same transcript read a moment later holds the message). This waits briefly for it.
    Returns None when the dialect is not one this reads, or no message appears in time. A
    transcript that is not valid UTF-8 is unreadable, as ``canonical_transcript`` treats it:
    ``UnicodeDecodeError`` is a ``ValueError``, not an ``OSError``.
    """
    if dialect != "event-data" or not path:
        return None
    deadline = time.monotonic() + wait_seconds
    while True:
        text = None
        try:
            with open(path, encoding="utf-8") as handle:
                events = []
                for line in handle:
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(event, dict):
                        events.append(event)
        except (OSError, ValueError):
            events = []
        last_user = max((i for i, e in enumerate(events) if e.get("type") == "user.message"), default=-1)
        for event in events[last_user + 1:]:
            if event.get("type") != "assistant.message":
                continue
            content = (event.get("data") or {}).get("content")
            if isinstance(content, list):
                content = "\n".join(
                    block.get("text", "") for block in content
                    if isinstance(block, dict) and block.get("type") == "text")
            if isinstance(content, str) and content.strip():
                text = content
        if text is not None or time.monotonic() >= deadline:
            return text
        time.sleep(0.05)


# --- canonical payloads -----------------------------------------------------------------


def canonical_payloads(event, hook, payload, config, environ, project):
    """The canonical payloads to run one declared hook with (none when it does not apply)."""
    base = {"hook_event_name": CANONICAL_EVENT[event], "cwd": str(project)}
    session = first(payload, ("session_id", "sessionId"))
    if session:
        base["session_id"] = session
    transcript = first(payload, TRANSCRIPT_KEYS)
    if transcript:
        base["transcript_path"] = transcript

    if event == "prompt_submit":
        base["prompt"] = first(payload, PROMPT_KEYS) or environ.get("USER_PROMPT", "")
        return [base]
    if event == "stop":
        base["stop_hook_active"] = first(payload, STOP_ACTIVE_KEYS, bool) is True
        message = first(payload, LAST_MESSAGE_KEYS)
        if message is not None:
            base["last_assistant_message"] = message
        return [base]
    if event not in TOOL_EVENTS:
        return [base]

    wanted = {CANONICAL_TOOL[category] for category in hook.get("tools", CANONICAL_TOOL)}
    payloads = []
    for name, arguments in raw_tool_calls(payload):
        for tool_name, tool_input in canonical_calls(name, arguments, config.get("tool_categories", {})):
            if tool_name not in wanted:
                continue
            call = dict(base, tool_name=tool_name, tool_input=tool_input)
            dialect = shell_dialect(name, config.get("shell_dialects") or {})
            if tool_name == CANONICAL_TOOL["shell"] and dialect:
                call["shell_dialect"] = dialect  # the tool stays the canonical shell tool
            response = canonical_response(next((payload[key] for key in RESPONSE_KEYS if key in payload), None))
            if response is not None:
                call["tool_response"] = response
            if isinstance(payload.get("error"), str):
                call["error"] = payload["error"]
            payloads.append(call)
    return payloads


# --- running the scripts ----------------------------------------------------------------


class Result:
    """What the bootcamp's scripts asked for, merged across every script that ran."""

    def __init__(self):
        self.context = []
        self.deny = None
        self.keep_going = None

    def add(self, completed):
        output = (completed.stdout or "").strip()
        if completed.returncode == 2:
            self.deny = self.deny or (completed.stderr or "").strip() or "Blocked by the bootcamp."
            return
        if completed.returncode != 0:
            debug(f"a hook script exited {completed.returncode}: {(completed.stderr or '').strip()[:400]}")
            return
        if not output:
            return
        try:
            value = json.loads(output)
        except ValueError:
            self.context.append(output)  # plain text is context, as session start writes it
            return
        if not isinstance(value, dict):
            return
        specific = value.get("hookSpecificOutput")
        specific = specific if isinstance(specific, dict) else {}
        if value.get("decision") == "block":
            self.keep_going = self.keep_going or str(value.get("reason") or "")
        if specific.get("permissionDecision") == "deny":
            self.deny = self.deny or str(specific.get("permissionDecisionReason") or "Blocked by the bootcamp.")
        context = specific.get("additionalContext") or value.get("additionalContext")
        if isinstance(context, str) and context.strip():
            self.context.append(context)


def run_script(script, payload, project, environ, host):
    """Run one hook script with a canonical payload. Returns the completed process, its
    ``stdout`` and ``stderr`` as text.

    Bytes go in and bytes come out, so no locale and no console code page takes part. The
    payload is ASCII JSON, which a script reads the same under any encoding. The output is
    decoded here as UTF-8 with replacement characters: a strict decode raised on output
    that was not valid UTF-8, and the script's exit code, a block included, was lost with
    it.
    """
    completed = subprocess.run(
        [sys.executable, str(HERE / script)],
        input=json.dumps(payload).encode("ascii"),
        capture_output=True,
        cwd=str(project),
        env=dict(environ, SENZING_BOOTCAMP_HOST=host),
        timeout=SCRIPT_TIMEOUT_SECONDS,
        check=False,
    )
    completed.stdout = completed.stdout.decode("utf-8", errors="replace")
    completed.stderr = completed.stderr.decode("utf-8", errors="replace")
    return completed


# --- results in the assistant's dialect -------------------------------------------------


def write_result(event, result, dialect, out, err):
    """Write ``result`` the way the assistant reads it. Returns the exit code.

    JSON is ASCII-escaped, and plain text and a denial reason are written as UTF-8 bytes
    (``write_text``), so the bytes are the same whatever encoding ``out`` and ``err`` have.
    """
    context = "\n\n".join(result.context)
    stopping = event == "stop"

    if dialect == "flat":  # decisions and context as top-level keys
        if result.deny:
            body = {"permissionDecision": "deny", "permissionDecisionReason": result.deny}
        elif stopping and result.keep_going:
            body = {"decision": "block", "reason": result.keep_going}
        elif context:
            body = {"additionalContext": context}
        else:
            return 0
        out.write(json.dumps(body) + "\n")
        return 0

    if dialect == "steps":  # always one JSON object, always exit 0
        if result.deny:
            body = {"decision": "deny", "reason": result.deny}
        elif stopping and result.keep_going:
            body = {"decision": "continue", "reason": result.keep_going}
        elif context and not stopping:
            body = {"injectSteps": [{"userMessage": context}]}
        else:
            body = {}
        out.write(json.dumps(body) + "\n")
        return 0

    if dialect == "text":  # stdout is context, a non-zero exit blocks, a stop cannot be held
        if result.deny:
            write_text(err, result.deny + "\n")
            return 2
        if context and not stopping:
            write_text(out, context + "\n")
        return 0

    # "canonical": the dialect the scripts themselves speak
    if result.deny:
        write_text(err, result.deny + "\n")
        return 2
    if stopping and result.keep_going:
        out.write(json.dumps({"decision": "block", "reason": result.keep_going}) + "\n")
    elif context and not stopping:
        body = {"hookSpecificOutput": {"hookEventName": CANONICAL_EVENT[event], "additionalContext": context}}
        out.write(json.dumps(body) + "\n")
    return 0


def run(event, raw, environ, out, err, config=None):
    if event not in CANONICAL_EVENT:
        debug(f"unknown event {event!r}")
        return 0
    config = config if config is not None else load_config()
    dialect = config.get("result_dialect", "canonical")
    result = Result()
    payload = read_payload(raw)
    project = project_dir(payload, environ, HERE.parents[len(Path(config.get("scripts_dir", "scripts")).parts) - 1])
    if project is None:
        debug("the assistant did not say which project this is")
        return write_result(event, result, dialect, out, err)

    if event == "stop" and first(payload, LAST_MESSAGE_KEYS) is None:
        message = final_message(first(payload, TRANSCRIPT_KEYS), config.get("transcript_dialect"))
        if message is not None:
            payload = dict(payload, last_assistant_message=message)
    transcript, temporary = canonical_transcript(
        first(payload, TRANSCRIPT_KEYS), config.get("transcript_dialect"))
    try:
        for hook in config.get("hooks", {}).get(event, []):
            for canonical in canonical_payloads(event, hook, payload, config, environ, project):
                if transcript:
                    canonical["transcript_path"] = transcript
                else:
                    canonical.pop("transcript_path", None)
                result.add(run_script(hook["script"], canonical, project, environ, config.get("host", "")))
    finally:
        if temporary:
            try:
                os.unlink(transcript)
            except OSError:
                pass
    return write_result(event, result, dialect, out, err)


def main(argv=None):
    argv = sys.argv if argv is None else argv
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        return run(argv[1] if len(argv) > 1 else "", raw, os.environ, sys.stdout, sys.stderr)
    except Exception:  # noqa: BLE001 - a hook must never break the assistant
        if os.environ.get(DEBUG_ENV):
            traceback.print_exc()
        return 0


if __name__ == "__main__":
    sys.exit(main())
