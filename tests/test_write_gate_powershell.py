"""The write-gate reads a PowerShell command by PowerShell's rules (issue #33).

On 2026-11-17 a dry run sent `python src\\load\\load.py > $env:TEMP\\o.txt` and
`echo hi > C:\\Windows\\Temp\\o.txt` through the built GitHub Copilot adapter with
`toolName: "powershell"`, and both were allowed. The adapter turned every shell tool into the
canonical `Bash` call, so `write-gate.py` read the command as POSIX shell: its lexer dropped
the unquoted backslashes, and it knew `$TMPDIR` and not `$env:TEMP`.

Now an assistant's profile says which of its shell tools is PowerShell
(`options.adapter.shell_dialects`), the adapter passes that on as `shell_dialect` in the
canonical payload, and the gate reads such a command by PowerShell's rules through the same
pipeline as a Bash one. The governing invariant is INV-200: the gate keeps what the bootcamp
writes inside the project, and its dated notes say what the gate reads on a shell command.

**What these tests are, and are not.** Every command below goes through the Copilot package
as the build writes it: its `hook_adapter.py`, its `bootcamp_host.json`, its `write-gate.py`.
The payload is the `preToolUse` payload Copilot CLI 1.0.111 sent for its `bash` tool
(`tests/fixtures/host-payloads/`), with the tool name changed to `powershell`. That tool name
comes from `hosts/copilot/host.json`; **no payload from Copilot on Windows has been observed**,
and no PowerShell ran. The tests show what the gate decides for a command string, not what a
live PowerShell writes.

`LOC_MSG` is read from the gate, and each denial asserts the whole message: it is the only
message the shell branch emits, so a denial with other text came from the Write/Edit path.

Stdlib only (INV-108).

Run:  python3 -m unittest discover -s tests
"""
import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_write_gate_bash as bash_cases   # the Bash cases, replayed through Copilot's `bash`
from _built import built

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_GATE = REPO_ROOT / "source" / "scripts" / "write-gate.py"
SOURCE_README = REPO_ROOT / "source" / "hooks" / "README.md"
HOSTS = REPO_ROOT / "hosts"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "host-payloads" / "copilot-cli-1.0.111.jsonl"

COPILOT = built("copilot")          # the Copilot package, built from source/
ADAPTER = COPILOT / "scripts" / "hook_adapter.py"
GATE = COPILOT / "scripts" / "write-gate.py"
HOST_FILE = COPILOT / "scripts" / "bootcamp_host.json"

_spec = importlib.util.spec_from_file_location("hook_adapter", HOSTS / "_shared" / "hook_adapter.py")
adapter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(adapter)

URL = "https://mcp.senzing.com/examples/x.py"
#: The two commands the issue reports.
REPORTED = ("python src\\load\\load.py > $env:TEMP\\o.txt", "echo hi > C:\\Windows\\Temp\\o.txt")


def gate_constant(name):
    """A string constant of the gate, read from its source (it reads stdin at import time)."""
    for node in ast.parse(SOURCE_GATE.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == name:
            return ast.literal_eval(node.value)
    raise AssertionError("write-gate.py defines no %s" % name)


LOC_MSG = gate_constant("LOC_MSG")
DENIED = {"permissionDecision": "deny", "permissionDecisionReason": LOC_MSG}


def captured_shell_call():
    """The `preToolUse` payload Copilot CLI sent for its `bash` tool, as captured."""
    for line in FIXTURE.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["event"] == "preToolUse" and record["payload"]["toolName"] == "bash":
            return record["payload"]
    raise AssertionError("the capture holds no bash preToolUse payload")


CAPTURED = captured_shell_call()


def send(command, project, tool="powershell"):
    """Send one shell command through the built Copilot adapter; return what it answers.

    `{}` is an allowed call: the adapter writes nothing when no script objects.
    """
    payload = dict(CAPTURED, cwd=project, toolName=tool,
                   toolArgs=dict(CAPTURED["toolArgs"], command=command))
    done = subprocess.run([sys.executable, str(ADAPTER), "pre_tool_use"], input=json.dumps(payload),
                          text=True, capture_output=True, cwd=project, check=False)
    if done.returncode != 0:
        raise AssertionError("the adapter exited %d: %s" % (done.returncode, done.stderr))
    return json.loads(done.stdout) if done.stdout.strip() else {}


def run_gate(payload, project):
    """Run the built gate on a canonical payload; return (exit_code, stderr)."""
    done = subprocess.run([sys.executable, str(GATE)], input=json.dumps(payload), text=True,
                          capture_output=True, cwd=project, check=False)
    return done.returncode, done.stderr.strip()


class _Project(unittest.TestCase):
    """A bootcamp project under the system temp directory, removed after each test."""

    def setUp(self):
        self.proj = os.path.realpath(bash_cases.make_project())
        self.addCleanup(shutil.rmtree, self.proj, True)

    def assertDenied(self, command, tool="powershell"):
        self.assertEqual(send(command, self.proj, tool), DENIED, "not denied with LOC_MSG: %r" % command)

    def assertAllowed(self, command, tool="powershell"):
        self.assertEqual(send(command, self.proj, tool), {}, "not allowed: %r" % command)


class TheDialectTravelsWithTheCall(unittest.TestCase):
    """`host.json` declares it, the build copies it, the adapter passes it on."""

    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads((HOSTS / "copilot" / "host.json").read_text(encoding="utf-8"))
        cls.config = cls.profile["options"]["adapter"]

    def canonical(self, tool, arguments=None):
        payload = dict(CAPTURED, toolName=tool, toolArgs=arguments or {"command": REPORTED[0]})
        return adapter.canonical_payloads(
            "pre_tool_use", {"script": "write-gate.py", "tools": ["write", "edit", "shell"]},
            payload, self.config, {}, Path("/work/project"))

    def test_the_profile_declares_its_powershell_tool(self):
        self.assertEqual(self.config["shell_dialects"], {"powershell": "powershell"})

    def test_the_built_package_carries_the_declaration(self):
        built_config = json.loads(HOST_FILE.read_text(encoding="utf-8"))
        self.assertEqual(built_config["shell_dialects"], self.config["shell_dialects"])

    def test_every_declared_dialect_is_on_a_shell_tool_and_is_one_the_gate_reads(self):
        """Every assistant's profile: a dialect on a tool that is not a shell tool, or one the
        gate does not read, would be silently POSIX."""
        declared = 0
        for path in sorted(HOSTS.glob("*/host.json")):
            options = json.loads(path.read_text(encoding="utf-8")).get("options", {})
            config = options.get("adapter") or {}
            for tool, dialect in config.get("shell_dialects", {}).items():
                declared += 1
                with self.subTest(host=path.parent.name, tool=tool):
                    self.assertEqual(config["tool_categories"].get(tool), "shell")
                    self.assertEqual(dialect, "powershell")
        self.assertGreaterEqual(declared, 1)

    def test_a_powershell_call_stays_the_canonical_shell_tool_and_names_its_dialect(self):
        for tool in ("powershell", "PowerShell"):
            with self.subTest(tool=tool):
                (call,) = self.canonical(tool)
                self.assertEqual(call["tool_name"], "Bash")
                self.assertEqual(call["tool_input"], {"command": REPORTED[0]})
                self.assertEqual(call["shell_dialect"], "powershell")

    def test_a_call_from_any_other_tool_names_no_dialect(self):
        (shell,) = self.canonical("bash")
        self.assertEqual(shell["tool_name"], "Bash")
        self.assertNotIn("shell_dialect", shell)
        (write,) = self.canonical("create", {"path": "src/a.txt", "file_text": "x"})
        self.assertEqual(write["tool_name"], "Write")
        self.assertNotIn("shell_dialect", write)

    def test_a_profile_that_declares_none_names_no_dialect(self):
        config = {key: value for key, value in self.config.items() if key != "shell_dialects"}
        payload = dict(CAPTURED, toolName="powershell")
        (call,) = adapter.canonical_payloads(
            "pre_tool_use", {"script": "write-gate.py", "tools": ["shell"]},
            payload, config, {}, Path("/work/project"))
        self.assertNotIn("shell_dialect", call)


class TheReportedCommandsAreDenied(_Project):
    def test_through_the_powershell_tool(self):
        for command in REPORTED:
            with self.subTest(command=command):
                self.assertDenied(command)

    def test_from_a_project_outside_the_temp_directory(self):
        """The project is under HOME, as a Bootcamper's is. Skipped where HOME is itself
        under a temp prefix, or cannot be written."""
        home = os.path.realpath(os.path.expanduser("~"))
        temp = os.path.realpath(tempfile.gettempdir())
        if home == temp or home.startswith(temp + os.sep) or home.startswith("/tmp/"):
            self.skipTest("HOME (%s) is under the temp directory" % home)
        try:
            self.proj = bash_cases.make_project(parent=home)
        except OSError as exc:
            self.skipTest("HOME is not writable: %s" % exc)
        self.addCleanup(shutil.rmtree, self.proj, True)
        for command in REPORTED:
            with self.subTest(command=command):
                self.assertDenied(command)
        self.assertAllowed("python src\\load\\load.py > logs\\o.txt")


class EveryRedirectIsDenied(_Project):
    def test_each_operator_spaced_and_attached(self):
        for operator in (">", ">>", "2>", "2>>", "*>", "*>>"):
            for command in ("ls %s $env:TEMP\\o.txt" % operator,
                            "ls %s$env:TEMP\\o.txt" % operator,
                            "ls %s C:\\Windows\\Temp\\o.txt" % operator,
                            "ls %s $HOME\\Downloads\\o.txt" % operator):
                with self.subTest(command=command):
                    self.assertDenied(command)

    def test_a_redirect_written_against_its_command(self):
        self.assertDenied("echo hi>$env:TEMP\\o.txt")
        self.assertDenied("ls 2>&1 > $env:TEMP\\o.txt")


#: The issue's cmdlet table: each command and alias, with every way it names its target.
FILE_WRITERS = {
    "Out-File": ("-FilePath", "-LiteralPath"),
    "Set-Content": ("-Path", "-LiteralPath"), "Add-Content": ("-Path", "-LiteralPath"),
    "sc": ("-Path", "-LiteralPath"), "ac": ("-Path", "-LiteralPath"),
    "Tee-Object": ("-FilePath", "-LiteralPath"), "tee": ("-FilePath", "-LiteralPath"),
}
COPIERS = ("Copy-Item", "Move-Item", "cp", "copy", "cpi", "mv", "move", "mi")
FETCHERS = ("Invoke-WebRequest", "iwr", "curl", "wget")


def writer_forms(target):
    """`{label: command}` for every form in the issue's cmdlet table, writing to `target`."""
    forms = {}
    for name, parameters in FILE_WRITERS.items():
        forms[name + ", first positional"] = "Get-Date | %s %s" % (name, target)
        for parameter in parameters:
            forms["%s %s" % (name, parameter)] = "Get-Date | %s %s %s" % (name, parameter, target)
    for name in COPIERS:
        forms[name + ", second positional"] = "%s src\\a.txt %s" % (name, target)
        forms[name + " -Destination"] = "%s -Destination %s src\\a.txt" % (name, target)
        forms[name + " -Path, first positional"] = "%s -Path src\\a.txt %s" % (name, target)
        forms[name + " -LiteralPath, first positional"] = "%s %s -LiteralPath src\\a.txt" % (name, target)
    for name in FETCHERS:
        forms[name + " -OutFile"] = "%s %s -OutFile %s" % (name, URL, target)
    forms["curl.exe -o"] = "curl.exe -fsSL -o %s %s" % (target, URL)
    forms["wget -O"] = "wget -O %s %s" % (target, URL)
    return forms


class EveryWriterAndAliasIsDenied(_Project):
    def test_each_form_into_system_temp(self):
        for label, command in writer_forms("$env:TEMP\\o.txt").items():
            with self.subTest(form=label):
                self.assertDenied(command)

    def test_each_form_into_downloads(self):
        for label, command in writer_forms("$env:USERPROFILE\\Downloads\\o.txt").items():
            with self.subTest(form=label):
                self.assertDenied(command)

    def test_each_form_inside_the_project_is_allowed(self):
        """Negative control for the two tests above: the same forms, the target moved."""
        for label, command in writer_forms("src\\resources\\o.txt").items():
            with self.subTest(form=label):
                self.assertAllowed(command)

    def test_names_match_in_any_case(self):
        for command in ("get-date | out-file -filepath $env:TEMP\\o.txt",
                        "GET-DATE | SET-CONTENT -PATH $env:TEMP\\o.txt",
                        "COPY-ITEM src\\a.txt -DESTINATION $env:TEMP",
                        "Iwr %s -outfile $env:TEMP\\o.txt" % URL):
            with self.subTest(command=command):
                self.assertDenied(command)

    def test_a_parameter_and_its_value_joined_by_a_colon(self):
        self.assertDenied("Set-Content -Path:$env:TEMP\\o.txt -Value hi")
        self.assertDenied("Copy-Item src\\a.txt -Destination:C:\\Windows\\Temp\\a.txt")

    def test_a_switch_takes_no_value_and_any_other_parameter_takes_one(self):
        """`-Force` is a switch, so the word after it is a positional; `-Value` takes `hi`,
        so the path is still the first positional."""
        self.assertDenied("Copy-Item -Force -Recurse src $env:TEMP\\backup")
        self.assertDenied("Set-Content -Value hi $env:TEMP\\o.txt")
        self.assertAllowed("Set-Content -Value $env:TEMP src\\o.txt")
        self.assertAllowed("Set-Content src\\o.txt $env:TEMP")

    def test_a_directory_as_the_destination(self):
        for command in ("Copy-Item src\\a.txt $env:TEMP", "Move-Item src\\a.txt C:\\Windows\\Temp",
                        "Copy-Item src\\a.txt /tmp", "cp src\\a.txt ~\\Downloads"):
            with self.subTest(command=command):
                self.assertDenied(command)


class TheCommandIsSplitOnItsOperators(_Project):
    """A write after `;`, a newline, `|`, `&&` or `||` is still a top-level write."""

    WRITE = "Copy-Item src\\a.txt $env:TEMP"

    def test_each_operator(self):
        for command in ("cd src; " + self.WRITE, "cd src\n" + self.WRITE, "cd src\r\n" + self.WRITE,
                        "Get-Date | Set-Content $env:TEMP\\o.txt",
                        "cd src && " + self.WRITE, "cd src || " + self.WRITE,
                        "cd src;" + self.WRITE, "if ($true) { %s }" % self.WRITE,
                        "& copy-item src\\a.txt $env:TEMP",
                        "Set-Content `\n  -Path $env:TEMP\\o.txt `\n  -Value hi",
                        self.WRITE + "  # keep a copy"):
            with self.subTest(command=command):
                self.assertDenied(command)

    def test_a_comment_is_not_a_command(self):
        self.assertAllowed("Get-Date  # " + self.WRITE)
        self.assertAllowed("<# %s #> Get-Date" % self.WRITE)
        self.assertDenied("<# a note #> " + self.WRITE)


#: Each temp and Downloads directory the issue names, however PowerShell spells it.
TEMP_SPELLINGS = (
    "$env:TEMP", "$env:TMP", "$env:TMPDIR", "$Env:Temp", "$ENV:TMP", "$env:tmpdir",
    "${env:TEMP}", "${env:TMP}", "${Env:TmpDir}",
    "C:\\Windows\\Temp", "c:\\windows\\temp", "C:\\Users\\someone\\AppData\\Local\\Temp", "/tmp",
)
DOWNLOADS_SPELLINGS = (
    "$HOME\\Downloads", "$env:USERPROFILE\\Downloads", "$env:HOME\\Downloads", "~\\Downloads",
    "$home\\downloads", "$Env:UserProfile\\Downloads", "${HOME}\\Downloads",
    "${env:USERPROFILE}\\Downloads", "${env:HOME}\\Downloads", "~/Downloads", "$HOME/Downloads",
)


class EveryTempAndDownloadsSpellingIsDenied(_Project):
    def test_unquoted_and_inside_a_double_quoted_string(self):
        for directory in TEMP_SPELLINGS + DOWNLOADS_SPELLINGS:
            for command in ("echo hi > %s\\o.txt" % directory,
                            'echo hi > "%s\\o.txt"' % directory,
                            'Set-Content -Path "%s\\my notes.txt" -Value hi' % directory):
                with self.subTest(command=command):
                    self.assertDenied(command)

    def test_a_variable_in_a_single_quoted_string_is_not_read(self):
        """A single-quoted string is literal, so PowerShell would write beside the command,
        into a directory named `$env:TEMP`. A literal temp path is still a temp path."""
        self.assertDenied('echo hi > "$env:TEMP\\o.txt"')         # positive control
        self.assertAllowed("echo hi > '$env:TEMP\\o.txt'")
        self.assertAllowed("echo hi > `$env:TEMP\\o.txt")
        self.assertAllowed('echo hi > "`$env:TEMP\\o.txt"')
        self.assertDenied("echo hi > 'C:\\Windows\\Temp\\o.txt'")
        self.assertDenied("echo hi > 'C:\\Windows\\Temp\\it''s.txt'")

    def test_a_longer_variable_name_is_another_variable(self):
        self.assertDenied("echo hi > $env:TEMP\\o.txt")           # positive control
        self.assertDenied("echo hi > $HOME\\Downloads\\o.txt")
        self.assertAllowed("echo hi > $env:TEMPLATES\\o.txt")
        self.assertAllowed("echo hi > $HOMEWORK\\Downloads\\o.txt")


class AWriteInsideTheProjectIsAllowed(_Project):
    def test_a_relative_target(self):
        for command in ("echo hi > src\\o.txt", "echo hi > .\\src\\o.txt", "echo hi >> src/o.txt",
                        "Get-Date | Out-File -FilePath .\\logs\\o.txt",
                        "Copy-Item src\\a.txt src\\b.txt", "iwr %s -OutFile src\\resources\\x.py" % URL):
            with self.subTest(command=command):
                self.assertAllowed(command)
        self.assertDenied("echo hi > $env:TEMP\\src\\o.txt")      # positive control

    def test_an_absolute_target_in_a_project_that_lives_under_a_temp_directory(self):
        """Resolve, then compare: the project is under the temp directory, and its own files
        are still inside it. The same file one level up is outside it, and is denied."""
        temp = os.path.realpath(tempfile.gettempdir())
        self.assertTrue(self.proj.startswith(temp + os.sep), self.proj)
        for inside in (os.path.join(self.proj, "src", "o.txt"), self.proj + "\\src\\o.txt"):
            for command in ("echo hi > %s" % inside, 'echo hi > "%s"' % inside,
                            "Set-Content -Path %s -Value hi" % inside,
                            "Copy-Item src\\a.txt %s" % inside):
                with self.subTest(command=command):
                    self.assertAllowed(command)
        self.assertAllowed("Copy-Item src\\a.txt %s" % self.proj)
        outside = os.path.dirname(self.proj) + "\\o.txt"
        self.assertDenied("echo hi > %s" % outside)
        self.assertDenied("Set-Content -Path %s -Value hi" % outside)


class TheseAreAllowed(_Project):
    def test_the_null_device_and_a_stream_merge_name_no_file(self):
        for command in ("ls > $null", "ls >$null", "ls 2> $null", "ls *> $null", "ls > $NULL",
                        "ls 2>&1", "ls *>&1", "ls 2>&1 | Out-File src\\o.txt",
                        "Get-Date | Out-File $null"):
            with self.subTest(command=command):
                self.assertAllowed(command)
        self.assertDenied("ls > $env:TEMP\\null")     # positive control

    def test_a_temp_path_that_is_a_source(self):
        for command in ("Copy-Item $env:TEMP\\a.txt src\\a.txt",
                        "Copy-Item -Path $env:TEMP\\a.txt -Destination src\\a.txt",
                        "Copy-Item -Destination src\\a.txt -Path $env:TEMP\\a.txt",
                        "cp -Destination src\\a.txt -Path $env:TEMP\\a.txt",
                        "Copy-Item $env:TEMP\\a.txt, $env:TEMP\\b.txt src\\",
                        "Copy-Item $env:TEMP\\a.txt,$env:TEMP\\b.txt src\\",
                        "Move-Item C:\\Windows\\Temp\\a.txt .\\src\\",
                        "Get-Content $env:TEMP\\a.txt | Set-Content src\\a.txt",
                        "Get-Content $env:TEMP\\a.txt", "python $env:TEMP\\x.py > src\\out.txt",
                        "iwr https://example.com/tmp/x -OutFile src\\x",
                        "curl.exe -o src\\x https://example.com/tmp/x"):
            with self.subTest(command=command):
                self.assertAllowed(command)

    def test_the_source_cases_are_denied_when_their_target_is_temp(self):
        """Positive control for the cases above: source and target exchanged."""
        for command in ("Copy-Item src\\a.txt $env:TEMP\\a.txt",
                        "Copy-Item -Path src\\a.txt -Destination $env:TEMP\\a.txt",
                        "cp -Destination $env:TEMP\\a.txt -Path src\\a.txt",
                        "Copy-Item src\\a.txt, src\\b.txt $env:TEMP",
                        "Get-Content src\\a.txt | Set-Content $env:TEMP\\a.txt",
                        "python src\\x.py > $env:TEMP\\out.txt",
                        "curl.exe -o $env:TEMP\\x https://example.com/src/x"):
            with self.subTest(command=command):
                self.assertDenied(command)

    def test_outside_the_project_but_not_temp_or_downloads(self):
        for command in ("echo hi > D:\\data\\o.txt", "echo hi > $env:USERPROFILE\\Documents\\o.txt",
                        "Copy-Item src\\a.txt C:\\ProgramData\\senzing\\a.txt",
                        "Copy-Item src\\a.txt ~\\.cargo\\bin\\", "echo hi > $HOME\\tmp\\o.txt"):
            with self.subTest(command=command):
                self.assertAllowed(command)
        self.assertDenied("echo hi > $env:USERPROFILE\\Downloads\\o.txt")     # positive control

    def test_a_quoted_payload_is_one_word(self):
        for payload in REPORTED + ("Copy-Item src\\a.txt $env:TEMP",):
            self.assertDenied(payload)                # positive control: unquoted, it is read
            for command in ("powershell -Command '%s'" % payload, "Invoke-Expression '%s'" % payload,
                            'pwsh -c "%s"' % payload, "echo '%s'" % payload):
                with self.subTest(command=command):
                    self.assertAllowed(command)

    def test_a_command_with_an_unbalanced_quote(self):
        for command in ('echo "unbalanced > $env:TEMP\\o.txt', "echo 'unbalanced > $env:TEMP\\o.txt",
                        'echo hi > "$env:TEMP\\o.txt'):
            with self.subTest(command=command):
                self.assertAllowed(command)
        self.assertDenied('echo "balanced" > $env:TEMP\\o.txt')      # positive control

    def test_a_here_string_body_is_data(self):
        body = "Copy-Item src\\a.txt $env:TEMP"
        self.assertDenied(body)                       # positive control: alone, it is a command
        for quote in ("'", '"'):
            here = "@%s\n%s\necho hi > $env:TEMP\\o.txt\n%s@" % (quote, body, quote)
            with self.subTest(quote=quote):
                self.assertAllowed("Set-Content src\\backup.ps1 %s" % here)
                self.assertAllowed("%s | Set-Content src\\backup.ps1\necho done" % here)
                self.assertDenied("%s | Set-Content $env:TEMP\\backup.ps1" % here)
                self.assertDenied("Set-Content src\\backup.ps1 %s\n%s" % (here, body))

    def test_no_bootcamp_no_gate(self):
        self.assertDenied(REPORTED[0])                # positive control: the gate is on
        os.remove(os.path.join(self.proj, "config", "bootcamp_progress.json"))
        for command in REPORTED:
            self.assertAllowed(command)


class APayloadThatNamesNoDialectIsReadAsToday(_Project):
    """Only a tool the profile declares as PowerShell gets PowerShell's rules."""

    def test_the_reported_commands_through_the_bash_tool_are_read_as_posix_shell(self):
        """A POSIX shell drops an unquoted backslash, so both name a file in the project."""
        for command in REPORTED:
            with self.subTest(command=command):
                self.assertAllowed(command, tool="bash")
                self.assertDenied(command, tool="powershell")

    def test_a_cmdlet_is_no_writer_to_a_posix_shell(self):
        for command in ("Copy-Item src/a.txt /tmp/a.txt", "sc /tmp/o.txt hi", "copy src/a.txt /tmp",
                        "echo hi | Tee-Object /tmp/o.txt", "iwr %s -OutFile /tmp/x" % URL):
            with self.subTest(command=command):
                self.assertAllowed(command, tool="bash")
                self.assertDenied(command, tool="powershell")

    def test_every_form_the_bash_test_blocks_is_denied_through_the_bash_tool(self):
        cases = dict(bash_cases.EveryNamedFormIsBlocked.CASES, incident=bash_cases.INCIDENT)
        for name, command in cases.items():
            with self.subTest(form=name):
                self.assertDenied(command, tool="bash")

    def test_the_canonical_payload_alone_decides(self):
        """The gate on its own: the same command, with and without the field."""
        for command in REPORTED + ("Copy-Item src\\a.txt $env:TEMP",):
            call = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
            with self.subTest(command=command):
                self.assertEqual(run_gate(call, self.proj), (0, ""))
                self.assertEqual(run_gate(dict(call, shell_dialect=None), self.proj), (0, ""))
                self.assertEqual(run_gate(dict(call, shell_dialect="fish"), self.proj), (0, ""))
                self.assertEqual(run_gate(dict(call, shell_dialect="powershell"), self.proj), (2, LOC_MSG))

    def test_a_posix_write_with_no_dialect_is_blocked_as_before(self):
        call = {"tool_name": "Bash", "tool_input": {"command": "echo hi > /tmp/o.txt"}}
        self.assertEqual(run_gate(call, self.proj), (2, LOC_MSG))

    def test_the_dialect_does_not_reach_a_write_or_an_edit(self):
        """`tool_name` still selects the branch: the field on a Write changes nothing."""
        for path, expected in (("src/o.txt", 0), ("/tmp/o.txt", 2)):
            call = {"tool_name": "Write", "shell_dialect": "powershell",
                    "tool_input": {"file_path": path, "content": "x = 1"}}
            with self.subTest(path=path):
                self.assertEqual(run_gate(call, self.proj)[0], expected)


class TheGateSaysWhatItChecksOnPowerShell(unittest.TestCase):
    """Read from `source/`, so it holds in every package that ships the file."""

    FORMS = ("Out-File", "Set-Content", "Add-Content", "Tee-Object", "Copy-Item", "Move-Item",
             "Invoke-WebRequest -OutFile", "$env:TEMP", "$env:TMP", "$env:TMPDIR")

    def test_the_docstring(self):
        doc = " ".join(ast.get_docstring(ast.parse(SOURCE_GATE.read_text(encoding="utf-8"))).split())
        aliases = ("sc", "ac", "tee", "cp", "copy", "cpi", "mv", "move", "mi", "iwr", "curl", "wget")
        redirects = (">", ">>", "2>", "2>>", "*>", "*>>")
        homes = ("$HOME", "$env:USERPROFILE", "$env:HOME", "~")
        for form in self.FORMS + aliases + redirects + homes + ("$null", "2>&1"):
            with self.subTest(form=form):
                self.assertIn("``%s``" % form, doc)
        for phrase in ("PowerShell", '"shell_dialect": "powershell"', "has not been observed"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, doc)

    def test_the_readme_row(self):
        row = next(line for line in SOURCE_README.read_text(encoding="utf-8").splitlines()
                   if "`scripts/write-gate.py`" in line and line.startswith("|"))
        self.assertIn("PowerShell", row)
        for form in self.FORMS + ("2>", "*>"):
            with self.subTest(form=form):
                self.assertIn("`%s`" % form, row)


if __name__ == "__main__":
    unittest.main()
