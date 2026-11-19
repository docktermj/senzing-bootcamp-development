"""Building a host's package: where files go, and what stops a host being left behind.

Enforces **INV-446** (registered 2026-11-18) on a miniature repository, with
`test_bootcamp_build_hosts.py` on the real profiles; neither establishes that a name in an
adapter map is a tool name the assistant really sends.
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build import __main__ as cli  # noqa: E402
from tools.bootcamp_build import model  # noqa: E402
from tools.bootcamp_build.emit import (  # noqa: E402
    build_host, claude_style_hooks, unmapped_hooks, write_catalogs,
)
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


#: An adapter map whose names differ from the profile's ``hooks.tools`` names (Write, Edit, Bash),
#: so a matcher shows which of the two it was built from.
ADAPTER_MAP = {"patcher": "patch", "Put": "write", "put_file": "write", "Change": "edit", "Run": "shell"}


class AdapterMatchers(Workspace):
    """A host that goes through the hook adapter takes each matcher from the adapter's map (#34)."""

    def adapter_profile(self, tool_categories=None, package_format="claude-plugin", **hooks):
        profile = host_profile("alpha", "Alpha Code", foreign_terms=["Beta"], package_format=package_format)
        profile["hooks"]["command"] = 'python3 "{{host.plugin_root}}/scripts/{script}" {event}'
        profile["hooks"].update(hooks)
        categories = ADAPTER_MAP if tool_categories is None else tool_categories
        profile["options"] = {"adapter": {"result_dialect": "canonical", "tool_categories": categories}}
        self.write("hosts/alpha/host.json", json.dumps(profile))

    def matcher(self, tools):
        declaration, build = self.build("alpha")
        declaration = dict(declaration, hooks=[{"event": "pre_tool_use", "tools": tools, "script": "gate.py"}])
        return claude_style_hooks(declaration, build.host)["hooks"]["PreTool"][0].get("matcher")

    def test_a_matcher_holds_every_name_the_map_gives_a_covered_category(self):
        self.adapter_profile()
        self.assertEqual(self.matcher(["write", "shell"]), "patcher|Put|put_file|Run")
        self.assertEqual(self.matcher(["write", "edit", "shell"]), "patcher|Put|put_file|Change|Run")

    def test_a_patch_tool_is_matched_where_the_hook_covers_a_write_or_an_edit(self):
        self.adapter_profile()
        self.assertEqual(self.matcher(["edit"]), "patcher|Change")
        self.assertEqual(self.matcher(["write"]), "patcher|Put|put_file")
        self.assertEqual(self.matcher(["shell"]), "Run")

    def test_a_host_without_an_adapter_still_takes_its_names_from_hooks_tools(self):
        declaration, build = self.build("beta")
        hooks = claude_style_hooks(declaration, build.host)["hooks"]
        self.assertEqual(hooks["PreTool"][0]["matcher"], "Write|Bash")

    def test_a_host_that_has_no_matchers_keeps_none(self):
        self.adapter_profile(matchers=False)
        self.assertIsNone(self.matcher(["write", "edit", "shell"]))

    def test_a_category_the_map_cannot_name_stops_the_build(self):
        self.adapter_profile({"patcher": "patch", "Put": "write"})
        with self.assertRaisesRegex(BuildError, r"alpha: options\.adapter\.tool_categories .* 'shell'"):
            self.build("alpha")

    def test_it_stops_the_build_of_a_package_that_carries_no_hook_file_too(self):
        """Such a package's matchers are built later, by an installer, from the emitted map."""
        self.write("source/bootcamp.json", json.dumps(dict(DECLARATION, keywords=["bootcamp"])))
        self.adapter_profile({"Put": "write"}, package_format="agent-plugin")
        with self.assertRaisesRegex(BuildError, r"alpha: options\.adapter\.tool_categories .* 'shell'"):
            self.build("alpha")
        self.adapter_profile(package_format="agent-plugin")
        _, build = self.build("alpha")
        self.assertFalse([name for name in build.files if name.endswith("hooks.json")])


class CatalogCategory(Workspace):
    """A catalog entry's category is the one the host's manifest gives (#34)."""

    CATALOG = {"path": "catalog/marketplace.json", "style": "codex", "name": "alpha"}

    def catalog(self, interface):
        self.profile("alpha", "Alpha Code", catalog=self.CATALOG, options={"manifest": {"interface": interface}})
        written = write_catalogs(load_declaration(self.source), [load_host("alpha", self.hosts)], self.out)
        self.assertEqual(written, [self.CATALOG["path"]])
        return json.loads((self.out / self.CATALOG["path"]).read_text(encoding="utf-8"))

    def test_the_category_comes_from_the_host_profile(self):
        for category in ("Zeta Tools", "Another Shelf"):
            with self.subTest(category=category):
                self.assertEqual(self.catalog({"category": category})["plugins"][0]["category"], category)

    def test_a_profile_without_a_category_stops_the_build(self):
        for interface in ({}, {"category": ""}):
            with self.subTest(interface=interface):
                with self.assertRaisesRegex(BuildError, r"alpha: options\.manifest\.interface\.category"):
                    self.catalog(interface)


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


class LetterCaseDoesNotHideAName(Workspace):
    """Issue #30: a model ID, a directory and a variable spell an assistant's name in lower or
    upper case. Each is reported, in a built package and in the source, as the name itself is.

    ⛔ **The build's check for another assistant's name matches it in any letter case, in `source/` and in every built package.**

    That line is queued as a `DEFERRED INVARIANT` block in issue #30's entry of
    `specs/IMPLEMENTED.md`, awaiting the maintainer's sign-off. Until then only this file and
    `tests/test_shared_text_holds_in_every_package.py`, which holds the real tree to the
    recorded ceilings, hold it.
    """

    SPELLINGS = ("beta-large-5 / high", "the .beta-plugin directory", "BETA_PROJECT_DIR", "bEtA")

    def hosts_loaded(self):
        return [load_host("alpha", self.hosts), load_host("beta", self.hosts)]

    def test_any_spelling_in_a_built_package_is_reported(self):
        for spelling in self.SPELLINGS:
            with self.subTest(spelling=spelling):
                self.write("source/skills/start/SKILL.md", f"Neutral.\nSee {spelling}.\n")
                _, build = self.build("alpha")
                findings = residue(build)
                self.assertEqual([(f.path, f.line, f.term.lower()) for f in findings],
                                 [("skills/start/SKILL.md", 2, "beta")])

    def test_any_spelling_in_a_script_is_reported_like_any_other_text(self):
        """A path or a comment in a script gets no exemption."""
        self.write("source/scripts/one.py", "# see .beta/skills\nROOT = '.beta-plugin'\n")
        _, build = self.build("alpha")
        self.assertEqual([(f.path, f.line) for f in residue(build)],
                         [("scripts/one.py", 1), ("scripts/one.py", 2)])
        self.assertEqual([(f.path, f.line) for f in lint_source(self.source, self.hosts_loaded())],
                         [("source/scripts/one.py", 1), ("source/scripts/one.py", 2)])

    def test_any_spelling_in_the_source_outside_its_block_is_reported(self):
        for spelling in self.SPELLINGS:
            with self.subTest(spelling=spelling):
                self.write(
                    "source/skills/start/SKILL.md",
                    f"<!-- host:only beta -->\nOnly {spelling}.\n<!-- host:end -->\nAll: {spelling}.\n",
                )
                findings = lint_source(self.source, self.hosts_loaded())
                self.assertEqual([(f.line, f.term.lower()) for f in findings], [(4, "beta")])

    def test_a_hosts_own_name_stays_allowed_in_its_own_package(self):
        self.write("source/skills/start/SKILL.md",
                   "<!-- host:only beta -->\nUse beta-large-5.\n<!-- host:end -->\n")
        _, build = self.build("beta")
        self.assertIn("Use beta-large-5.", (build.root / "skills/start/SKILL.md").read_text())
        self.assertEqual(residue(build), [])
        self.assertEqual(lint_source(self.source, self.hosts_loaded()), [])

    def test_a_word_that_only_contains_other_letters_is_not_reported(self):
        self.write("source/skills/start/SKILL.md", "Read the alphabet, then bet on a result.\n")
        _, build = self.build("beta")
        self.assertEqual([f.term for f in residue(build)], ["alpha"])
        self.write("source/skills/start/SKILL.md", "Bet on a better result.\n")
        _, build = self.build("alpha")
        self.assertEqual(residue(build), [])


class TheCheckCommandReportsIt(Workspace):
    """`python3 -m tools.bootcamp_build check`, run on the miniature repository."""

    FRONTMATTER = "---\nname: start\ndescription: Start the work.\n---\n"

    def setUp(self):
        super().setUp()
        self.skill("Run {{host.product}}.\n")

    def skill(self, body):
        """The one skill, with the frontmatter the check also reads; its body starts on line 5."""
        self.write("source/skills/start/SKILL.md", self.FRONTMATTER + body)

    def check(self):
        ids = ["alpha", "beta"]
        out = io.StringIO()
        with mock.patch.object(cli, "SOURCE_DIR", self.source), \
                mock.patch.object(cli, "host_ids", lambda: ids), \
                mock.patch.object(cli, "load_hosts",
                                  lambda selected=None: [load_host(i, self.hosts) for i in selected or ids]), \
                mock.patch.object(cli, "NEUTRALITY", self.root / "neutrality.json"), \
                contextlib.redirect_stdout(out):
            code = cli.main(["check"])
        return code, out.getvalue()

    def test_a_neutral_tree_passes(self):
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertTrue(out.endswith("\nOK\n"), out)

    def test_a_lowercase_name_in_another_assistants_package_fails_the_check(self):
        # The name reaches the package from a profile value, so the source itself stays neutral
        # and only the package check can report it.
        for host_id, product, other in (("alpha", "Alpha Code", "Beta"), ("beta", "Beta Chat", "Alpha")):
            self.profile(host_id, product, foreign_terms=[other],
                         vars={"product": product, "plugin_root": "${ROOT}", "model": "beta-large-5"})
        self.skill("Use {{host.model}}.\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("skills/start/SKILL.md:5: 'beta': Use beta-large-5.", out)
        self.assertIn("source: 0 host-specific terms outside a host block", out)
        self.assertIn("alpha: 1 is above the recorded ceiling of 0", out)
        self.assertTrue(out.endswith("\nFAILED: 1 problems\n"), out)

    def test_a_lowercase_name_in_the_source_outside_a_host_block_fails_the_check(self):
        self.write("source/scripts/one.py", "ROOT = '.beta-plugin'\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("source/scripts/one.py:1: 'beta': ROOT = '.beta-plugin'", out)
        self.assertIn("source: 1 is above the recorded ceiling of 0", out)
        self.assertRegex(out, r"\nFAILED: \d+ problems\n\Z")


if __name__ == "__main__":
    unittest.main()
