"""Building a host's package: where files go, and what stops a host being left behind."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build import model  # noqa: E402
from tools.bootcamp_build.emit import build_host, claude_style_hooks, unmapped_hooks  # noqa: E402
from tools.bootcamp_build.model import BuildError, load_declaration, load_host  # noqa: E402
from tools.bootcamp_build.validate import compare_trees, lint_source, residue  # noqa: E402

DECLARATION = {
    "name": "senzing-bootcamp",
    "version": "1.2.3",
    "description": "Bootcamp for {{host.product}}.",
    "author": {"name": "Senzing"},
    "homepage": "https://example.invalid/home",
    "repository": "https://example.invalid/repo",
    "license": "Apache-2.0",
    "mcp_servers": {"senzing": {"url": "https://example.invalid/mcp"}},
    "hooks": [
        {"event": "prompt_submit", "script": "one.py"},
        {"event": "prompt_submit", "script": "two.py"},
        {"event": "pre_tool_use", "tools": ["write", "shell"], "script": "gate.py"},
        {"event": "pre_compact", "script": "one.py"},
    ],
}

EVENTS = {event: None for event in model.HOOK_EVENTS}


def host_profile(host_id, product, **overrides):
    profile = {
        "id": host_id,
        "name": host_id.title(),
        "package_format": "claude-plugin",
        "vars": {"product": product, "plugin_root": "${ROOT}"},
        "layout": {"skills": "skills", "scripts": "scripts"},
        "hooks": {
            "command": 'python3 "{{host.plugin_root}}/scripts/{script}"',
            "events": {**EVENTS, "prompt_submit": "PromptSubmit", "pre_tool_use": "PreTool"},
            "tools": {"write": "Write", "edit": "Edit", "shell": "Bash"},
        },
        "foreign_terms": [],
    }
    profile.update(overrides)
    return profile


class Workspace(unittest.TestCase):
    """A miniature repository: a source tree and two host profiles."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.source = self.root / "source"
        self.hosts = self.root / "hosts"
        self.out = self.root / "dist"
        self.write("source/skills/start/SKILL.md", "Run {{host.product}}.\n")
        for script in ("one.py", "two.py", "gate.py"):
            self.write(f"source/scripts/{script}", "print('hello')\n")
        os.chmod(self.source / "scripts" / "gate.py", 0o755)
        self.write("source/bootcamp.json", json.dumps(DECLARATION))
        self.profile("alpha", "Alpha Code", foreign_terms=["Beta"])
        self.profile("beta", "Beta Chat", foreign_terms=["Alpha"])

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def profile(self, host_id, product, **overrides):
        self.write(f"hosts/{host_id}/host.json", json.dumps(host_profile(host_id, product, **overrides)))

    def build(self, host_id):
        declaration = load_declaration(self.source)
        host = load_host(host_id, self.hosts)
        return declaration, build_host(declaration, host, self.source, self.out, {"alpha", "beta"})


class Packages(Workspace):
    def test_text_is_rendered_and_placed_by_the_layout(self):
        _, build = self.build("alpha")
        self.assertEqual((build.root / "skills/start/SKILL.md").read_text(), "Run Alpha Code.\n")
        self.assertEqual(build.root, self.out / "plugins" / "alpha" / "senzing-bootcamp")

    def test_the_executable_bit_survives(self):
        _, build = self.build("alpha")
        self.assertTrue(os.access(build.root / "scripts/gate.py", os.X_OK))
        self.assertFalse(os.access(build.root / "scripts/one.py", os.X_OK))

    def test_the_manifest_takes_its_text_from_the_declaration(self):
        _, build = self.build("beta")
        manifest = json.loads((build.root / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(manifest["version"], "1.2.3")
        self.assertEqual(manifest["description"], "Bootcamp for Beta Chat.")

    def test_a_rebuild_replaces_the_previous_output(self):
        _, build = self.build("alpha")
        stale = build.root / "skills/stale.md"
        stale.write_text("left over\n")
        self.build("alpha")
        self.assertFalse(stale.exists())

    def test_two_builds_are_identical(self):
        _, first = self.build("alpha")
        other = self.root / "again"
        declaration = load_declaration(self.source)
        second = build_host(declaration, first.host, self.source, other, {"alpha", "beta"})
        self.assertEqual(compare_trees(first.root, second.root), [])


class NoHostIsLeftBehind(Workspace):
    def test_a_source_file_no_layout_entry_covers_stops_the_build(self):
        self.write("source/commands/start.md", "Start.\n")
        with self.assertRaisesRegex(BuildError, "source/commands/start.md is not covered"):
            self.build("alpha")

    def test_mapping_an_entry_to_null_drops_it_on_purpose(self):
        self.write("source/commands/start.md", "Start.\n")
        self.profile("alpha", "Alpha Code", layout={"skills": "skills", "scripts": "scripts", "commands": None})
        _, build = self.build("alpha")
        self.assertFalse((build.root / "commands").exists())

    def test_a_variable_one_host_lacks_stops_that_hosts_build(self):
        self.write("source/skills/start/SKILL.md", "Open {{host.settings_menu}}.\n")
        with self.assertRaisesRegex(BuildError, "does not define variable 'settings_menu'"):
            self.build("alpha")

    def test_a_host_profile_must_decide_every_hook_event(self):
        profile = host_profile("alpha", "Alpha Code")
        del profile["hooks"]["events"]["session_end"]
        self.write("hosts/alpha/host.json", json.dumps(profile))
        with self.assertRaisesRegex(BuildError, "no entry for 'session_end'"):
            self.build("alpha")

    def test_a_hook_naming_a_missing_script_is_rejected(self):
        declaration = dict(DECLARATION, hooks=[{"event": "stop", "script": "absent.py"}])
        self.write("source/bootcamp.json", json.dumps(declaration))
        with self.assertRaisesRegex(BuildError, "'absent.py' is not a file"):
            self.build("alpha")


class Hooks(Workspace):
    def test_consecutive_hooks_for_one_event_share_a_group(self):
        declaration, build = self.build("alpha")
        hooks = claude_style_hooks(declaration, build.host)["hooks"]
        self.assertEqual(
            [entry["command"] for entry in hooks["PromptSubmit"][0]["hooks"]],
            ['python3 "${ROOT}/scripts/one.py"', 'python3 "${ROOT}/scripts/two.py"'],
        )
        self.assertNotIn("matcher", hooks["PromptSubmit"][0])

    def test_tool_categories_become_the_hosts_tool_names(self):
        declaration, build = self.build("alpha")
        hooks = claude_style_hooks(declaration, build.host)["hooks"]
        self.assertEqual(hooks["PreTool"][0]["matcher"], "Write|Bash")

    def test_an_event_the_host_lacks_is_left_out_and_reported(self):
        declaration, build = self.build("alpha")
        self.assertNotIn(None, claude_style_hooks(declaration, build.host)["hooks"])
        self.assertEqual([hook["event"] for hook in unmapped_hooks(declaration, build.host)], ["pre_compact"])


class OtherHostsStayOut(Workspace):
    def test_another_hosts_name_in_a_built_package_is_reported(self):
        self.write("source/skills/start/SKILL.md", "Works like Beta Chat.\n")
        _, build = self.build("alpha")
        findings = residue(build)
        self.assertEqual([(f.path, f.line, f.term) for f in findings], [("skills/start/SKILL.md", 1, "Beta")])

    def test_a_host_name_in_the_source_outside_its_block_is_reported(self):
        self.write(
            "source/skills/start/SKILL.md",
            "<!-- host:only beta -->\nBeta only.\n<!-- host:end -->\nBeta for everyone.\n",
        )
        hosts = [load_host("alpha", self.hosts), load_host("beta", self.hosts)]
        findings = lint_source(self.source, hosts)
        self.assertEqual([(f.line, f.term) for f in findings], [(4, "Beta")])

    def test_neutral_source_passes(self):
        hosts = [load_host("alpha", self.hosts), load_host("beta", self.hosts)]
        self.assertEqual(lint_source(self.source, hosts), [])


if __name__ == "__main__":
    unittest.main()
