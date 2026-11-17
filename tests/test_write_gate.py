"""Tests for the PreToolUse write-gate security control (INV-200 location, INV-109 secrets).

The gate runs two independent checks and each has its own invariant. **INV-200** governs
the location half — every file the bootcamp writes lives inside the Bootcamper's project —
and the `LocationChecks` cases below are its enforcement: system temp, `~/Downloads`,
`%TEMP%`/`TMPDIR` env vars, `..` escapes, any other out-of-project target, and the two
allowances that make it usable (a project-relative path, and a real project that lives
beneath a temp directory). **INV-109** governs the secret half, which fails closed
regardless of path.

INV-200 was registered 2026-08-11: the behavior and these tests long predated it, so the
guarantee was enforced here and recorded in no rule — INV-109's own text scoped itself away
from "the location logic" without anything picking it up. Cited here so `coverage_reports.py
invariants` can see the enforcement that already existed.

**Why several cases assert the MESSAGE, not just the exit code** (2026-08-11,
`specs/inv200-overstates-what-the-write-gate-blocks.md`). The gate used to block only
system temp, `~/Downloads` and relocated temp dirs; a resolved target outside the project
that named none of those lists fell through and was **allowed**, so INV-200's boundary was
a claim no code made. The fall-through now blocks. That fix costs these tests their old
discriminator: when *everything* outside the project blocks, the exit code can no longer
say **which** branch blocked, so a test meant to pin one branch would start passing for the
wrong reason — and the env-var branch, whose whole point is that no static list can match
it, would become untestable by outcome. The two messages restore the distinction, so
`TEMP_MSG` vs `OUTSIDE_MSG` is what those cases assert.

`source/scripts/write-gate.py` reads stdin at import time, so it
cannot be imported directly — each case runs it as a subprocess with synthetic
stdin and a temp project directory (holding `config/bootcamp_progress.json`, which
is what activates the gate), then asserts the exit code (0 allow, 2 block).

**The message for a secret that an edit only removes** (#47). The gate judges the whole
payload, so an edit whose replaced text holds a secret and whose new text does not is
blocked too, and "Use environment variables instead" pointed away from the next step that
works. `SecretOnlyInTheReplacedText` asserts the addition to the message for that case and
that every other payload keeps `SECRET_MSG` alone. What it blocks is unchanged (INV-109).

These tests live OUTSIDE `source/` on purpose: `propagate.sh` mirrors all of
`source/` into the public repo, so tests placed there would ship to bootcampers.

Run:  python3 -m unittest discover -s tests
"""
import ast
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(REPO_ROOT, "source", "scripts", "write-gate.py")
HOSTS = os.path.join(REPO_ROOT, "hosts")

ALLOW, BLOCK = 0, 2

# Discriminating phrases from the gate's two location messages. `write-gate.py` reads stdin
# at import time so its constants cannot be imported; these are substrings, not copies of
# the full text, so re-wording a message does not break the tests while re-pointing a
# branch at the other message does.
TEMP_MSG = "system temp or Downloads"        # LOC_MSG: temp/Downloads specifically
OUTSIDE_MSG = "outside the Bootcamp project"  # OUTSIDE_MSG: the general boundary


def run_gate(file_path=None, content="hello", cwd=None, activate=True,
             raw=None, env=None):
    """Invoke write-gate.py; return (exit_code, stderr)."""
    proj = cwd or tempfile.mkdtemp()
    if activate:
        os.makedirs(os.path.join(proj, "config"), exist_ok=True)
        with open(os.path.join(proj, "config", "bootcamp_progress.json"), "w") as fh:
            fh.write("{}")
    if raw is not None:
        payload = raw
    else:
        payload = json.dumps({"tool_input": {"file_path": file_path, "content": content}})
    run_env = dict(os.environ)
    if env:
        run_env.update(env)
    proc = subprocess.run([sys.executable, GATE], input=payload, cwd=proj,
                          capture_output=True, text=True, env=run_env)
    return proc.returncode, proc.stderr


class LocationChecks(unittest.TestCase):
    def test_project_relative_allowed(self):
        self.assertEqual(run_gate("config/prefs.yaml")[0], ALLOW)

    def test_absolute_in_project_allowed(self):
        proj = tempfile.mkdtemp()
        self.assertEqual(run_gate(os.path.join(proj, "config/x.yaml"), cwd=proj)[0], ALLOW)

    def test_system_tmp_blocked(self):
        self.assertEqual(run_gate("/tmp/scratch.txt")[0], BLOCK)
        self.assertEqual(run_gate("/var/tmp/scratch.txt")[0], BLOCK)

    def test_downloads_blocked(self):
        self.assertEqual(run_gate("/home/someone/Downloads/out.txt")[0], BLOCK)

    def test_windows_temp_env_blocked(self):
        self.assertEqual(run_gate(r"%TEMP%\out.txt")[0], BLOCK)
        self.assertEqual(run_gate(r"%Tmp%\out.txt")[0], BLOCK)  # case-insensitive

    def test_tmpdir_env_blocked(self):
        tmp = tempfile.mkdtemp()
        rc, _ = run_gate(os.path.join(tmp, "x.txt"), env={"TMPDIR": tmp})
        self.assertEqual(rc, BLOCK)

    def test_relocated_temp_dir_blocked_via_env_only(self):
        """The env-var branch, reached only when the static prefix lists CANNOT match.

        Added 2026-08-11. `test_tmpdir_env_blocked` and `test_windows_temp_env_blocked`
        both look like they cover this branch and neither does: the first uses
        `tempfile.mkdtemp()`, which on Linux returns `/tmp/...` and is caught by the
        static prefix; the second passes the literal string `%TEMP%`, caught by the
        substring list. Deleting the whole `for var in ("TMPDIR", "TEMP", "TMP")` loop
        left the suite green — found by negative-controlling INV-200 on the day it was
        registered.

        The branch exists for the platforms this suite does not run on: macOS puts its
        per-user temp under `/var/folders/...` and Windows under
        `C:\\Users\\...\\AppData\\Local\\Temp`, neither of which any static prefix can
        enumerate. So the target here is deliberately a path no prefix or substring
        matches — the block can only come from consulting the env var. The directory need
        not exist: the gate resolves and compares strings, it does not stat.

        Asserted on the MESSAGE, not the exit code: since the boundary fall-through
        blocks, this path is blocked either way, so only `TEMP_MSG` shows the env var was
        consulted. `OUTSIDE_MSG` here means the loop was skipped and the general boundary
        caught it -- exactly the silent regression this case exists to prevent.
        """
        fake_temp = "/opt/relocated-temp-xyz"
        for var in ("TMPDIR", "TEMP", "TMP"):
            with self.subTest(var=var):
                rc, err = run_gate(fake_temp + "/out.txt", env={var: fake_temp})
                self.assertEqual(
                    rc, BLOCK,
                    f"a relocated temp dir named by ${var} must be blocked; no static "
                    "prefix can match it, so only the env-var branch can catch this",
                )
                self.assertIn(
                    TEMP_MSG, err,
                    f"blocked, but not as temp -- ${var} was not consulted and the "
                    "general boundary caught it instead, so the env-var branch is "
                    "unguarded again",
                )

    def test_the_relocated_temp_probe_is_not_caught_by_a_static_list(self):
        """Guard the guard: if the probe path ever matches a prefix, the test above
        starts passing for the wrong reason and the branch is unguarded again.

        Before the boundary fix this asserted ALLOW. It cannot any more -- the probe is
        outside the project, so it now blocks on the boundary -- but the *message* still
        separates the two: `OUTSIDE_MSG` proves no static list named the path.
        """
        rc, err = run_gate("/opt/relocated-temp-xyz/out.txt")
        self.assertEqual(rc, BLOCK, "outside the project -> blocked (INV-200)")
        self.assertIn(
            OUTSIDE_MSG, err,
            "the probe path must reach the gate as a plain out-of-project target, not as "
            "temp, or the test above proves nothing about the env-var branch",
        )

    def test_dotdot_escape_blocked(self):
        """A `..` escape is blocked for escaping, not for where it happens to land.

        The previous version of this case built `config/../../..` + `/tmp/evil.txt`, so
        the escape landed IN `/tmp` and was blocked as temp -- its own comment said so.
        The `..` was incidental and the name claimed a guarantee the body never tested
        (`specs/inv200-overstates-what-the-write-gate-blocks.md`). This target escapes to
        a path no prefix, substring or temp env var names, and `OUTSIDE_MSG` is what
        proves the block came from the boundary check.

        The `..` count is deliberately generous: `norm()` clamps extra `..` at root, so
        this lands on /opt/... from a project at any depth.
        """
        proj = tempfile.mkdtemp()
        escape = os.path.join(proj, "config") + "/.." * 12 + "/opt/not-the-project/x.txt"
        rc, err = run_gate(escape, cwd=proj)
        self.assertEqual(rc, BLOCK, "a `..` escape out of the project must be blocked")
        self.assertIn(
            OUTSIDE_MSG, err,
            "blocked, but as temp/Downloads -- the escape landed somewhere a static list "
            "names, so this proves nothing about `..` handling",
        )

    def test_out_of_project_target_naming_no_list_is_blocked(self):
        """The fall-through branch: outside the project, and no list names it.

        This is the case INV-200 promised and no code enforced. Every other location
        test targets somewhere a list DOES name, which is why twelve passing tests missed
        it: the branch had no `block()` to mutate, so negative-controlling the suite
        could not reach it.

        Not vacuous by construction -- `OUTSIDE_MSG` can only come from the fall-through,
        so if the probe ever starts matching a static list this fails rather than passing
        for the wrong reason. `$HOME` is used because it is the realistic case: a write
        just outside a project living in the home directory.
        """
        proj = tempfile.mkdtemp()
        for target in (
            os.path.join(os.path.expanduser("~"), "escape.txt"),
            "/opt/not-the-project/x.txt",
            "/etc/senzing-bootcamp-probe.conf",
        ):
            with self.subTest(target=target):
                rc, err = run_gate(target, cwd=proj)
                self.assertEqual(
                    rc, BLOCK,
                    f"{target} resolves outside the project and must be blocked; before "
                    "2026-08-11 this fell through the location logic and was allowed",
                )
                self.assertIn(
                    OUTSIDE_MSG, err,
                    f"{target} was blocked by a static list, not the boundary -- pick a "
                    "probe no list names or this case guards nothing",
                )

    def test_project_under_tmp_path_allowed(self):
        # PreToolUseWriteError: a project living under a /tmp/-containing path must
        # not trip the gate for its own in-project writes.
        proj = tempfile.mkdtemp()  # e.g. /tmp/tmpXXXX
        self.assertEqual(run_gate(os.path.join(proj, "config/x.yaml"), cwd=proj)[0], ALLOW)

    def test_home_relative_downloads_blocked(self):
        self.assertEqual(run_gate("~/Downloads/out.txt")[0], BLOCK)

    def test_home_relative_windows_temp_blocked(self):
        self.assertEqual(run_gate("~/AppData/Local/Temp/x")[0], BLOCK)

    def test_home_personal_tmp_is_not_mistaken_for_system_temp(self):
        """`~/tmp` is a personal directory named tmp, NOT system temp.

        Blocked since the boundary fix -- it is outside the project like any other
        out-of-project path -- but it must be blocked as a boundary case, not classified
        as system temp. The `/tmp/` prefix check must stay anchored at the start of the
        resolved path; matching it as a substring would put `~/tmp` in the wrong branch,
        and (per `PreToolUseWriteError`) would also break a real project living under a
        `/tmp/`-containing path.
        """
        rc, err = run_gate("~/tmp/scratch.txt")
        self.assertEqual(rc, BLOCK, "outside the project -> blocked (INV-200)")
        self.assertIn(
            OUTSIDE_MSG, err,
            "~/tmp was classified as SYSTEM temp; the prefix match has stopped being "
            "anchored at the start of the path",
        )

    def test_case_variant_in_project_allowed(self):
        proj = tempfile.mkdtemp()
        self.assertEqual(run_gate(proj.upper() + "/config/x.yaml", cwd=proj)[0], ALLOW)


class SecretChecks(unittest.TestCase):
    def test_pem_private_key_blocked(self):
        self.assertEqual(
            run_gate("config/k.pem", content="-----BEGIN RSA PRIVATE KEY-----\nabc")[0],
            BLOCK)

    def test_aws_key_blocked(self):
        self.assertEqual(run_gate("config/creds", content="AKIA" + "A" * 16)[0], BLOCK)

    def test_senzing_license_blob_blocked(self):
        self.assertEqual(
            run_gate("config/lic.txt", content="AQAAAD" + "abc123XYZ+/=" * 4)[0], BLOCK)

    def test_lic_path_without_key_allowed(self):
        self.assertEqual(
            run_gate("licenses/g2.lic", content="see the Senzing license portal")[0], ALLOW)

    def test_bare_aqaaad_word_allowed(self):
        self.assertEqual(
            run_gate("config/notes.md", content="mentions the AQAAAD prefix in prose")[0],
            ALLOW)


def gate_constant(name):
    """A string constant read out of the gate's source: the gate cannot be imported."""
    with open(GATE, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("write-gate.py no longer assigns %s" % name)


def edit_payload(old, new, **extra):
    """An edit as the gate receives it from every assistant: the new text in `new_string`."""
    tool_input = dict({"file_path": "config/settings.txt", "old_string": old,
                       "new_string": new}, **extra)
    return json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Edit",
                       "tool_input": tool_input})


class SecretOnlyInTheReplacedText(unittest.TestCase):
    """#47: an edit that only removes a secret is still blocked, and told what works.

    The secrets are synthetic, built from the same shapes `SecretChecks` uses.

    What this does not establish: that an assistant's own edit tool sends its new text
    under a key the adapter knows. `test_every_assistants_edit_gets_the_addition` starts
    from one argument shape (`path`, `old_str`, `new_str`), not from a captured payload.
    """

    SECRETS = {
        "PEM private key": "-----BEGIN RSA PRIVATE KEY-----\nabc",
        "AWS access-key ID": "AKIA" + "A" * 16,
        "Senzing license payload": "AQAAAD" + "abc123XYZ+/=" * 4,
    }
    CLEAN = "api_key = os.environ['API_KEY']"

    @classmethod
    def setUpClass(cls):
        cls.secret_msg = gate_constant("SECRET_MSG")

    def assert_secret_msg_alone(self, payload):
        code, err = run_gate(raw=payload)
        self.assertEqual(BLOCK, code)
        self.assertEqual(self.secret_msg + "\n", err)

    def test_the_message_read_from_the_gate_is_the_secret_message(self):
        """INV-265: an empty constant would make every equality below vacuous."""
        self.assertIn("hardcoded secret", self.secret_msg)
        self.assertIn("Use environment variables instead.", self.secret_msg)

    def test_an_edit_that_only_removes_a_secret_is_blocked_with_the_addition(self):
        for label, secret in self.SECRETS.items():
            with self.subTest(secret=label):
                code, err = run_gate(raw=edit_payload("key = '%s'" % secret, self.CLEAN))
                self.assertEqual(BLOCK, code)
                self.assertTrue(err.startswith(self.secret_msg), err)
                addition = err[len(self.secret_msg):]
                self.assertIn("in the text being replaced", addition)
                self.assertIn("write the whole file again without the secret", addition)

    def test_the_addition_names_no_tool(self):
        """The next step has to work on every assistant, so it names none of their tools."""
        _code, err = run_gate(raw=edit_payload(self.SECRETS["AWS access-key ID"], self.CLEAN))
        addition = err[len(self.secret_msg):]
        self.assertTrue(addition.strip())
        for word in ("Edit", "tool", "Bash"):
            self.assertNotIn(word, addition)
        self.assertNotIn(self.SECRETS["AWS access-key ID"], err,
                         "the message must not echo the secret back")

    def test_the_next_step_it_names_passes_the_gate(self):
        """Writing the whole file again without the secret is a write the gate allows."""
        payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Write",
                              "tool_input": {"file_path": "config/settings.txt",
                                             "content": self.CLEAN + "\n"}})
        self.assertEqual((ALLOW, ""), run_gate(raw=payload))

    def test_a_secret_in_both_the_old_and_the_new_text_gets_the_message_alone(self):
        """The addition would be false: the new text holds a secret too."""
        for label, secret in self.SECRETS.items():
            with self.subTest(secret=label):
                self.assert_secret_msg_alone(edit_payload(secret, "rotated: " + secret))

    def test_a_secret_only_in_the_new_text_gets_the_message_alone(self):
        self.assert_secret_msg_alone(
            edit_payload(self.CLEAN, self.SECRETS["Senzing license payload"]))

    def test_a_write_gets_the_message_alone(self):
        for label, secret in self.SECRETS.items():
            with self.subTest(secret=label):
                self.assert_secret_msg_alone(json.dumps(
                    {"hook_event_name": "PreToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": "config/settings.txt", "content": secret}}))

    def test_a_payload_without_a_tool_name_gets_the_message_alone(self):
        """The shape `SecretChecks` sends: nothing says it is an edit."""
        self.assert_secret_msg_alone(json.dumps(
            {"tool_input": {"file_path": "config/creds",
                            "content": self.SECRETS["AWS access-key ID"]}}))

    def test_an_edit_with_no_new_text_gets_the_message_alone(self):
        """A patch arrives as an edit whose added lines are `content`: nothing to compare."""
        self.assert_secret_msg_alone(json.dumps(
            {"hook_event_name": "PreToolUse", "tool_name": "Edit",
             "tool_input": {"file_path": "config/settings.txt",
                            "content": self.SECRETS["PEM private key"]}}))

    def test_a_payload_that_does_not_parse_gets_the_message_alone(self):
        """The gate cannot tell old text from new, even when the text names both."""
        self.assert_secret_msg_alone(
            'garbage "tool_name":"Edit" "file_path":"config/x" "new_string":"clean" '
            '"old_string":"-----BEGIN PRIVATE KEY-----"')

    def test_an_edit_with_no_secret_is_allowed(self):
        """The control: the new branch does not block an ordinary edit."""
        self.assertEqual((ALLOW, ""), run_gate(raw=edit_payload("timeout = 5", "timeout = 9")))

    def test_every_assistants_edit_gets_the_addition(self):
        """Each assistant's edit tools, through the adapter, reach the same branch."""
        spec = importlib.util.spec_from_file_location(
            "hook_adapter_for_write_gate", os.path.join(HOSTS, "_shared", "hook_adapter.py"))
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        secret = self.SECRETS["AWS access-key ID"]
        checked = []
        for host in sorted(os.listdir(HOSTS)):
            profile_path = os.path.join(HOSTS, host, "host.json")
            if not os.path.isfile(profile_path):
                continue
            with open(profile_path, encoding="utf-8") as fh:
                options = json.load(fh).get("options") or {}
            categories = (options.get("adapter") or {}).get("tool_categories") or {}
            for tool in sorted(name for name, kind in categories.items() if kind == "edit"):
                arguments = {"path": "config/settings.txt", "old_str": secret,
                             "new_str": self.CLEAN}
                calls = adapter.canonical_calls(tool, arguments, categories)
                self.assertEqual(1, len(calls), (host, tool))
                tool_name, tool_input = calls[0]
                with self.subTest(host=host, tool=tool):
                    code, err = run_gate(raw=json.dumps(
                        {"hook_event_name": "PreToolUse", "tool_name": tool_name,
                         "tool_input": tool_input}))
                    self.assertEqual(BLOCK, code)
                    self.assertTrue(err.startswith(self.secret_msg), err)
                    self.assertIn("in the text being replaced", err)
                checked.append((host, tool))
        self.assertGreaterEqual(len({host for host, _tool in checked}), 3,
                                "too few assistants declare an edit tool for this to mean much")


class GateActivation(unittest.TestCase):
    def test_disabled_without_progress_file(self):
        self.assertEqual(run_gate("/tmp/x", activate=False)[0], ALLOW)

    def test_fail_open_on_unparseable_payload(self):
        self.assertEqual(run_gate(raw="not json at all")[0], ALLOW)

    def test_secret_still_checked_even_with_bad_json(self):
        # Field-regex fallback still catches secrets when JSON parsing fails.
        rc, _ = run_gate(raw='garbage "file_path":"config/x" -----BEGIN PRIVATE KEY-----')
        self.assertEqual(rc, BLOCK)


if __name__ == "__main__":
    unittest.main()
