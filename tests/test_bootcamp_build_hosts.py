"""Every assistant's package carries the same bootcamp, in the shape that assistant installs.

These checks run on what the build writes for each host, so they hold whatever the source says:
the same skills everywhere, an entry point for every command, hooks that name files the package
really contains, the same MCP server, and a catalog that points at a package that exists.

No phrase-level pattern (#1): its one line read counts a built file's lines against its
source's; it matches no phrase.
"""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.emit import build_host, unmapped_hooks, uses_adapter, write_catalogs  # noqa: E402
from tools.bootcamp_build.model import (  # noqa: E402
    HOOK_EVENTS, SOURCE_DIR, host_ids, load_declaration, load_hosts,
)
from tools.bootcamp_build.render import render_text  # noqa: E402
from tools.bootcamp_build.validate import skill_problems  # noqa: E402

EXPECTED_HOSTS = ["chatgpt", "claude", "copilot", "gemini", "kiro"]
MCP_FILES = (".mcp.json", "mcp.json", "mcp_config.json")
HOOK_FILES = ("hooks/hooks.json", "com.github.copilot/hooks/hooks.json", "hooks.json")


class Packages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory()
        cls.out = Path(cls.scratch.name)
        cls.declaration = load_declaration(SOURCE_DIR)
        cls.hosts = load_hosts()
        known = set(host_ids())
        cls.builds = {
            host.id: build_host(cls.declaration, host, SOURCE_DIR, cls.out, known) for host in cls.hosts
        }
        cls.catalogs = write_catalogs(cls.declaration, cls.hosts, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def each(self):
        for host_id, build in self.builds.items():
            with self.subTest(host=host_id):
                yield build

    def test_the_bootcamp_is_built_for_the_five_assistants(self):
        self.assertEqual(host_ids(), EXPECTED_HOSTS)

    def test_every_package_carries_every_curriculum_skill(self):
        curriculum = sorted(path.name for path in (SOURCE_DIR / "skills").iterdir() if path.is_dir())
        for build in self.each():
            shipped = {path.name for path in (build.root / "skills").iterdir() if path.is_dir()}
            self.assertEqual(sorted(set(curriculum) - shipped), [])

    def test_every_curriculum_file_is_in_every_package(self):
        """A skill's phase files travel with it, so no assistant gets half a module."""
        files = sorted(
            path.relative_to(SOURCE_DIR).as_posix()
            for path in (SOURCE_DIR / "skills").rglob("*") if path.is_file()
        )
        for build in self.each():
            self.assertEqual([name for name in files if name not in build.files], [])

    def test_every_command_has_an_entry_point_on_every_assistant(self):
        commands = sorted(path.stem for path in (SOURCE_DIR / "commands").glob("*.md"))
        self.assertTrue(commands)
        for build in self.each():
            for name in commands:
                as_command = f"commands/{name}.md" in build.files
                as_skill = f"skills/{name}/SKILL.md" in build.files
                self.assertTrue(as_command or as_skill, name)

    def test_a_command_turned_into_a_skill_keeps_its_instructions(self):
        for build in self.each():
            for path in sorted((SOURCE_DIR / "commands").glob("*.md")):
                skill = build.root / "skills" / path.stem / "SKILL.md"
                if not skill.is_file():
                    continue
                # The command as this host is given it (issue #28): a command can hold a host
                # block, whose marker lines and other hosts' lines reach no package.
                source_text = render_text(path.read_text(encoding="utf-8"), build.host,
                                          f"source/commands/{path.name}", directives=True,
                                          known_hosts=set(host_ids()))
                source_body = source_text.split("---\n", 2)[2]
                built_body = skill.read_text(encoding="utf-8").split("---\n", 2)[2]
                # The skill is the command's text plus one closing note saying where sibling
                # skills are, so an assistant never searches the disk for them. A host that
                # hands over a skill without its path adds one more, naming the skill's own
                # directory.
                source_lines, built_lines = source_body.rstrip("\n").splitlines(), built_body.splitlines()
                notes = 2 if build.host.options.get("skill_location_note") else 1
                self.assertEqual(len(built_lines), len(source_lines) + 2 * notes, path.name)
                self.assertEqual(built_lines[len(source_lines)], "", path.name)
                self.assertIn("Never search the filesystem for a skill file",
                              built_lines[len(source_lines) + 1], path.name)
                if notes == 2:
                    self.assertIn(f"/skills/{path.stem}/`", built_lines[-1], path.name)

    def test_every_skill_uses_only_frontmatter_every_assistant_reads(self):
        for build in self.each():
            self.assertEqual(skill_problems(build), [])

    def test_every_package_registers_the_same_mcp_server(self):
        urls = {}
        for build in self.each():
            found = [name for name in MCP_FILES if (build.root / name).is_file()]
            self.assertEqual(len(found), 1, found)
            servers = json.loads((build.root / found[0]).read_text())["mcpServers"]
            urls[build.host.id] = {name: server.get("url") for name, server in servers.items()}
        self.assertEqual(len({json.dumps(value, sort_keys=True) for value in urls.values()}), 1, urls)

    def test_every_hook_command_names_a_script_the_package_carries(self):
        for build in self.each():
            scripts = build.host.layout["scripts"]
            for name in HOOK_FILES:
                path = build.root / name
                if not path.is_file():
                    continue
                for script in re.findall(r"/([A-Za-z0-9_-]+\.py)", path.read_text()):
                    self.assertIn(f"{scripts}/{script}", build.files, name)

    def test_a_host_without_bundled_hooks_carries_an_installer_instead(self):
        for build in self.each():
            bundled = any((build.root / name).is_file() for name in HOOK_FILES)
            if not bundled:
                scripts = build.host.layout["scripts"]
                self.assertIn(f"{scripts}/install_hooks.py", build.files)

    def test_the_adapter_travels_with_the_hosts_that_need_it_and_only_those(self):
        for build in self.each():
            scripts = build.host.layout["scripts"]
            carried = f"{scripts}/hook_adapter.py" in build.files
            self.assertEqual(carried, uses_adapter(build.host))
            if carried:
                config = json.loads((build.root / scripts / "bootcamp_host.json").read_text())
                self.assertEqual(config["host"], build.host.id)
                self.assertEqual(config["bootcamp_version"], self.declaration["version"])
                for event, hooks in config["hooks"].items():
                    self.assertIn(event, HOOK_EVENTS)
                    for hook in hooks:
                        self.assertIn(f"{scripts}/{hook['script']}", build.files)

    def test_every_declared_hook_runs_or_is_reported_as_unmapped(self):
        """Nothing is dropped silently: a hook the host cannot run is one the build names."""
        for build in self.each():
            host = build.host
            unmapped = {(hook["event"], hook["script"]) for hook in unmapped_hooks(self.declaration, host)}
            for hook in self.declaration["hooks"]:
                mapped = host.hooks["events"][hook["event"]] is not None
                self.assertNotEqual(mapped, (hook["event"], hook["script"]) in unmapped)

    def test_every_package_has_the_same_version(self):
        versions = set()
        for build in self.each():
            for name in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "plugin.json"):
                path = build.root / name
                if path.is_file():
                    versions.add(json.loads(path.read_text())["version"])
        self.assertEqual(versions, {self.declaration["version"]})

    def test_each_catalog_points_at_a_package_that_exists(self):
        self.assertEqual(len(self.catalogs), len(set(self.catalogs)))
        for relative in self.catalogs:
            with self.subTest(catalog=relative):
                catalog = json.loads((self.out / relative).read_text())
                for plugin in catalog["plugins"]:
                    source = plugin["source"]
                    path = source["path"] if isinstance(source, dict) else source
                    self.assertTrue((self.out / path).is_dir(), path)

    def test_no_two_hosts_share_a_catalog_file(self):
        paths = [host.catalog["path"] for host in self.hosts if host.catalog]
        self.assertEqual(len(paths), len(set(paths)))


if __name__ == "__main__":
    unittest.main()
