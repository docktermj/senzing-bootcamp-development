"""No assistant's package sets the model or the reasoning effort, and all five say the same (#4).

The packages used to differ here: Claude's guidance named its commands and the other
assistants shared a wording that named controls. Issue #4 removed both. What is left is one
instruction text, identical everywhere, and no setting changed anywhere. This file checks
the second half against each built package, where a mechanism would have to live:

1. **Skill and command frontmatter** carries no `model` or `effort` key. On the assistant
   that reads one, a skill's `effort:` lasts only for the turn that loads the skill, and a
   bootcamp module is loaded once and runs for many turns (`docs/effort-mechanisms.md`).
2. **No agents directory.** A helper agent can hold its own model and effort, and does not
   see the conversation the bootcamp's stages depend on.
3. **Hook configuration** names no model and no effort, and runs commands only.
4. **No settings file** ships in a package, and no manifest or other JSON sets either one.

It also holds the parity the old file held: the same stages, the same level for each and
the same instructions, in every package.

Line-scoped by design (#4): frontmatter is one `key: value` pair per line.

Run:  python3 -m unittest discover -s tests
"""
import json
import re
import unittest

from _built import built
from _model_effort import GROUND_RULES, HOSTS, depth_block, depth_instructions, depth_rows, skill_text

FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
#: A key that sets the model or the effort, in any spelling an assistant documents.
SETTING_KEY = re.compile(r"(?i)^(?:model|effort|reasoning[_-]?effort|model[_-]reasoning[_-]effort)$")
#: A file whose job is to hold an assistant's settings.
SETTINGS_FILE = re.compile(r"(?i)^(?:settings(?:\.local)?\.json|config\.toml|settings\.toml)$")


def frontmatter_keys(text):
    """The top-level keys of a Markdown file's frontmatter, or [] when it has none."""
    match = FRONTMATTER.match(text)
    if not match:
        return []
    return [line.split(":", 1)[0].strip() for line in match.group(1).splitlines()
            if line.strip() and line[0] not in " \t#" and ":" in line]


def json_keys(value):
    """Every key at any depth of a parsed JSON value."""
    if isinstance(value, dict):
        for key, inner in value.items():
            yield key
            yield from json_keys(inner)
    elif isinstance(value, list):
        for inner in value:
            yield from json_keys(inner)


def files(host):
    root = built(host)
    return [path for path in sorted(root.rglob("*")) if path.is_file()]


class NoPackageSetsTheModelOrTheEffort(unittest.TestCase):
    def test_no_frontmatter_sets_either(self):
        seen = 0
        for host in HOSTS:
            for path in files(host):
                if path.suffix != ".md":
                    continue
                keys = frontmatter_keys(path.read_text(encoding="utf-8"))
                seen += bool(keys)
                with self.subTest(host=host, path=path.relative_to(built(host)).as_posix()):
                    self.assertEqual([], [key for key in keys if SETTING_KEY.match(key)])
        self.assertGreaterEqual(seen, 12 * len(HOSTS), "the skills' frontmatter was not read")

    def test_every_skill_frontmatter_is_name_and_description_only(self):
        for host in HOSTS:
            for path in sorted((built(host) / "skills").glob("*/SKILL.md")):
                with self.subTest(host=host, skill=path.parent.name):
                    self.assertEqual(["name", "description"],
                                     frontmatter_keys(path.read_text(encoding="utf-8")))

    def test_no_package_ships_an_agents_directory(self):
        for host in HOSTS:
            with self.subTest(host=host):
                root = built(host)
                self.assertEqual([], [path.relative_to(root).as_posix() for path in root.rglob("*")
                                      if path.is_dir() and path.name.lower() in ("agents", "subagents")])

    def test_no_package_ships_a_settings_file(self):
        for host in HOSTS:
            with self.subTest(host=host):
                root = built(host)
                self.assertEqual([], [path.relative_to(root).as_posix() for path in files(host)
                                      if SETTINGS_FILE.match(path.name)])

    def test_no_json_in_a_package_sets_either(self):
        """Manifests, MCP configuration and hook configuration, at any depth."""
        parsed = 0
        for host in HOSTS:
            root = built(host)
            for path in files(host):
                if path.suffix != ".json" or "vendor" in path.parts:
                    continue
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except ValueError:
                    continue
                parsed += 1
                with self.subTest(host=host, path=path.relative_to(root).as_posix()):
                    self.assertEqual([], [key for key in json_keys(data) if SETTING_KEY.match(key)])
        self.assertGreaterEqual(parsed, 3 * len(HOSTS), "the packages' JSON was not read")

    def test_every_hook_runs_a_command(self):
        """A prompt or agent hook is the hook form that can carry a model."""
        hooked = 0
        for host in HOSTS:
            root = built(host)
            for path in files(host):
                if path.name != "hooks.json":
                    continue
                hooked += 1
                text = path.read_text(encoding="utf-8")
                with self.subTest(host=host, path=path.relative_to(root).as_posix()):
                    self.assertNotRegex(text, r'"type"\s*:\s*"(?:prompt|agent)"')
        self.assertGreaterEqual(hooked, 1, "no package's hook configuration was found")

    def test_the_setting_key_pattern_sees_each_spelling(self):
        """Negative controls (INV-265)."""
        for key in ("model", "effort", "reasoningEffort", "model_reasoning_effort", "Effort"):
            with self.subTest(key=key):
                self.assertTrue(SETTING_KEY.match(key))
        for key in ("name", "description", "model_capable", "command"):
            with self.subTest(key=key):
                self.assertFalse(SETTING_KEY.match(key))
        self.assertEqual(["name", "effort"],
                         frontmatter_keys("---\nname: x\neffort: high\n---\nbody\n"))
        self.assertEqual(["mcpServers", "model"],
                         list(json_keys({"mcpServers": [{"model": "x"}]})))


class EveryAssistantWorksToTheSameDepth(unittest.TestCase):
    """The parity this file has always held, now over the one instruction text."""

    def test_every_assistant_has_the_same_stages_and_levels(self):
        reference = depth_rows(depth_block(skill_text("claude", GROUND_RULES)))
        self.assertEqual(12, len(reference))
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual(reference, depth_rows(depth_block(skill_text(host, GROUND_RULES))))

    def test_every_assistant_has_the_same_instructions(self):
        reference = depth_instructions(depth_block(skill_text("claude", GROUND_RULES)))
        self.assertEqual(2, len(reference))
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual(reference,
                                 depth_instructions(depth_block(skill_text(host, GROUND_RULES))))

    def test_all_five_are_built(self):
        self.assertEqual(5, len(HOSTS))


if __name__ == "__main__":
    unittest.main()
