"""Every assistant's package carries the same bootcamp, in the shape that assistant installs.

These checks run on what the build writes for each host, so they hold whatever the source says:
the same skills everywhere, an entry point for every command, hooks that name files the package
really contains, the same MCP server, and a catalog that points at a package that exists.

A host's configuration also agrees with itself (#34). Three things had two sources each, and
the two disagreed (`production-readiness-audit-2026-11-17`, findings 17, 18 and 26): a hook
matcher and the adapter's map of the assistant's tools, the hooks disclosure and the hook files
the installer writes, and the catalog's category and the manifest's. Each now has one source,
and these checks read the real host profiles:

⛔ **On an assistant whose hooks go through the hook adapter, a hook's matcher names exactly the tools the adapter's map gives the categories the hook covers.**

⛔ **A package that installs its hooks tells the bootcamper about every hook file it writes, in one bullet for each.**

Those two lines are queued as `DEFERRED INVARIANT` blocks in this issue's entry of
`specs/IMPLEMENTED.md`, awaiting the maintainer's sign-off. Until then only this file holds
them. A catalog entry also gives the category its manifest gives; that is one value read from
one profile key, and no rule is drafted for it.

No phrase-level pattern (#1): its one line read counts a built file's lines against its
source's; it matches no phrase. The disclosure check (#34) reads no line either: it matches the
file name that opens a bullet, one token that cannot wrap.
"""

import json
import re
import subprocess
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
INSTALLER = "install_hooks.py"
DISCLOSURE = "skills/bootcamp-hooks-setup/SKILL.md"
DISCLOSURE_HEADING = "## What to tell the bootcamper"
#: The adapter turns a patch into write and edit calls (``patch_calls`` in the hook adapter).
PATCH_COVERS = {"write", "edit"}


def has_matchers(host):
    """True for a host whose hooks go through the adapter and are limited to named tools."""
    return uses_adapter(host) and host.hooks.get("matchers", True)


def covered_categories(declaration, host):
    """``{host event: [tool category, ...]}`` for every declared event the host can run."""
    covered = {}
    for hook in declaration["hooks"]:
        event = host.hooks["events"][hook["event"]]
        if event is not None:
            covered.setdefault(event, [])
            covered[event] += [tool for tool in hook.get("tools", []) if tool not in covered[event]]
    return covered


def mapped_names(host, categories):
    """The names the host's own adapter map gives ``categories``, read from its profile."""
    wanted = set(categories) | ({"patch"} if PATCH_COVERS & set(categories) else set())
    return [name for name, category in host.options["adapter"]["tool_categories"].items() if category in wanted]


def matcher_problems(matcher, mapped):
    """What is wrong with one matcher, given the names the adapter maps for its hook."""
    names = matcher.split("|") if matcher else []
    problems = [f"omits {name!r}, which the adapter maps" for name in mapped if name not in names]
    problems += [f"names {name!r}, which the adapter maps to nothing the hook covers"
                 for name in names if name not in mapped]
    problems += [f"names {name!r} twice" for name in sorted(set(names)) if names.count(name) > 1]
    return problems


def install_hooks(build, workspace):
    """Run the package's hook installer on ``workspace``: what it printed, and the files it wrote."""
    script = build.root / build.host.layout["scripts"] / INSTALLER
    completed = subprocess.run(
        [sys.executable, str(script), "install", "--workspace", str(workspace), "--yes"],
        capture_output=True, check=True,
    )
    written = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(Path(workspace).rglob("*.json"))
    }
    return completed.stdout.decode("utf-8", errors="replace"), written


def built_matchers(build, workspace):
    """``{host event: [matcher or None, ...]}`` from the package's hook file, or from the hook
    files its installer writes into ``workspace``. ``None`` when the package has neither."""
    path = build.root / "hooks" / "hooks.json"
    if path.is_file():
        events = json.loads(path.read_text(encoding="utf-8"))["hooks"]
        return {event: [group.get("matcher") for group in groups] for event, groups in events.items()}
    if f"{build.host.layout['scripts']}/{INSTALLER}" not in build.files:
        return None
    found = {}
    for definition in install_hooks(build, workspace)[1].values():
        for hook in definition["hooks"]:
            found.setdefault(hook["trigger"], []).append(hook.get("matcher"))
    return found


def disclosure_problems(text, hook_files):
    """What is wrong with a hooks disclosure, given the hook files the installer writes.

    The disclosure is the list under ``DISCLOSURE_HEADING``. Each hook file needs one bullet
    there that begins with the file's name, and a bullet may not name a file that is not written.
    """
    if DISCLOSURE_HEADING not in text:
        return [f"has no {DISCLOSURE_HEADING!r} section"]
    section = text.split(DISCLOSURE_HEADING, 1)[1].split("\n## ", 1)[0]
    named = re.findall(r"^- `([^`]+\.json)`", section, re.M)
    problems = [f"has no bullet that begins with `{name}`" for name in hook_files if name not in named]
    problems += [f"has a bullet for `{name}`, which the installer does not write"
                 for name in named if name not in hook_files]
    problems += [f"has more than one bullet for `{name}`" for name in sorted(set(named)) if named.count(name) > 1]
    return problems


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

    def test_each_matcher_holds_exactly_the_tools_the_hosts_adapter_maps(self):
        """Read from the real profiles: the built hook file, or the files the installer writes."""
        checked = set()
        for build in self.builds.values():
            host = build.host
            if not has_matchers(host):
                continue
            with tempfile.TemporaryDirectory() as workspace:
                built = built_matchers(build, workspace)
            covered = covered_categories(self.declaration, host)
            with self.subTest(host=host.id):
                self.assertIsNotNone(built, "the package carries neither a hook file nor an installer")
                self.assertEqual(sorted(built), sorted(covered))
            for event, categories in covered.items():
                with self.subTest(host=host.id, event=event):
                    if not categories:
                        self.assertEqual(built[event], [None])
                        continue
                    mapped = mapped_names(host, categories)
                    self.assertTrue(mapped)
                    self.assertEqual(len(built[event]), 1, built[event])
                    self.assertEqual(matcher_problems(built[event][0], mapped), [])
                    checked.add(host.id)
        self.assertEqual(sorted(checked), [host.id for host in self.hosts if has_matchers(host)])
        self.assertTrue(checked, "no host with an adapter and matchers was read")

    def test_a_matcher_that_omits_a_mapped_tool_is_reported(self):
        """The check above fails on a matcher one name short, as each matcher was before #34."""
        checked = []
        for build in self.builds.values():
            host = build.host
            if not has_matchers(host):
                continue
            with self.subTest(host=host.id):
                mapped = mapped_names(host, ["write", "edit", "shell"])
                self.assertGreater(len(mapped), 1)
                for name in mapped:
                    short = "|".join(other for other in mapped if other != name)
                    self.assertEqual(matcher_problems(short, mapped), [f"omits {name!r}, which the adapter maps"])
                self.assertEqual(matcher_problems("|".join(mapped), mapped), [])
                self.assertEqual(matcher_problems("|".join(mapped + ["other", mapped[0]]), mapped), [
                    "names 'other', which the adapter maps to nothing the hook covers",
                    f"names {mapped[0]!r} twice",
                ])
            checked.append(host.id)
        self.assertTrue(checked, "no host with an adapter and matchers was read")

    def test_the_hooks_disclosure_has_one_bullet_for_each_hook_file_the_installer_writes(self):
        checked = []
        for build in self.builds.values():
            if f"{build.host.layout['scripts']}/{INSTALLER}" not in build.files:
                continue
            with tempfile.TemporaryDirectory() as workspace:
                printed, written = install_hooks(build, workspace)
            names = list(written)
            with self.subTest(host=build.host.id):
                self.assertTrue(names)
                for name in names:
                    self.assertIn(f"  {name}: on ", printed)
                text = (build.root / DISCLOSURE).read_text(encoding="utf-8")
                self.assertEqual(disclosure_problems(text, names), [])
                # The same check fails once a bullet is taken away, or a hook file is added.
                self.assertEqual(disclosure_problems(text.replace(f"- `{names[0]}`", "- The first hook"), names),
                                 [f"has no bullet that begins with `{names[0]}`"])
                self.assertEqual(disclosure_problems(text, names + ["senzing-bootcamp-new.json"]),
                                 ["has no bullet that begins with `senzing-bootcamp-new.json`"])
                self.assertEqual(disclosure_problems(text, names[1:]),
                                 [f"has a bullet for `{names[0]}`, which the installer does not write"])
            checked.append(build.host.id)
        self.assertTrue(checked, "no package carries a hook installer")

    def test_a_catalog_entry_gives_the_category_the_manifest_gives(self):
        checked = []
        for build in self.builds.values():
            host = build.host
            if not host.catalog or host.catalog["style"] != "codex":
                continue
            with self.subTest(host=host.id):
                profile = json.loads((host.directory / "host.json").read_text(encoding="utf-8"))
                category = profile["options"]["manifest"]["interface"]["category"]
                catalog = json.loads((self.out / host.catalog["path"]).read_text(encoding="utf-8"))
                manifest = json.loads((build.root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
                self.assertEqual([plugin["category"] for plugin in catalog["plugins"]], [category])
                self.assertEqual(manifest["interface"]["category"], category)
            checked.append(host.id)
        self.assertTrue(checked, "no catalog of this style was built")

if __name__ == "__main__":
    unittest.main()
