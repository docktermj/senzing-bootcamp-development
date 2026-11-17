"""The feedback hook and the packager report the version of the package they ship in.

Issue #31. Two bundled scripts answer "which bootcamp version is this":

- `feedback-capture.py` writes the version into the text it injects when the bootcamper asks
  to give feedback, so the guide records it without resolving anything itself;
- `package_bootcamp.py` writes it as `plugin_version` in `PACKAGE_MANIFEST.json` and prints it
  on the last line of `OPEN_ME_FIRST.md`.

Each read only a manifest path. The hook read `<script dir>/../.claude-plugin/plugin.json`,
which only the Claude package has, so on the four other assistants it told the guide "the
plugin version, which is Unknown -- already resolved … do NOT go looking". The packager read
`<script dir>/../plugin.json` and then the Claude path, which finds no manifest in the ChatGPT
package (its manifest is `.codex-plugin/plugin.json`) or the Kiro package (its scripts sit two
directories deeper), so those archives recorded `"plugin_version": "unknown"`
(`dry-run-2026-11-17`, finding 4; `production-readiness-audit-2026-11-17`, finding 22).

The build already writes the version beside both scripts, in `bootcamp_host.json`, on every
assistant, and `feedback.md` already tells the guide to read it there first.

⛔ **A bundled script that reports the bootcamp's version reads `bootcamp_version` from the `bootcamp_host.json` beside it before any manifest.**

That line is queued as a `DEFERRED INVARIANT` block in this issue's entry of
`specs/IMPLEMENTED.md`, awaiting the maintainer's sign-off. Until then only this file holds it.

What this file asserts:

- **Every built package.** Each assistant's package is built from `source/`, and both scripts
  are run from it as their own processes, in a scratch project. The hook's injected text and
  the packager's archive (its `PACKAGE_MANIFEST.json` and its `OPEN_ME_FIRST.md`) must carry
  the version in `source/bootcamp.json`. The assistants come from the build's own list, so a
  sixth is covered the day it is added (INV-246).
- **The order.** `bootcamp_version` in the `bootcamp_host.json` beside the script, then the
  manifest lookup the script had before, then the unresolved value: "Unknown" from the hook,
  "unknown" from the packager. Neither spelling changes.
- **No version in the file.** `bootcamp_host.json` gives no version when it is missing, cannot
  be read, is not valid JSON, or holds no non-empty string under `bootcamp_version`. Each
  case runs with a manifest above the script and without one. The script must exit 0 with no
  traceback, and fall through.
- **The manifest lookups are the ones each script had.** The hook reads
  `../.claude-plugin/plugin.json` and still does not read `../plugin.json`. The packager reads
  `../plugin.json`, then `../.claude-plugin/plugin.json`.
- **Nothing is searched for (INV-252).** A `bootcamp_host.json` above the script's directory,
  below it, in the project, or in the project's own `scripts/` is not read.
- **The sentence in `onboarding-flow.md`.** It names the step that reads `bootcamp_host.json`
  first (the feedback entry) and the steps that resolve the manifest (the WELCOME banner, the
  recap header and the recap's provenance block), and no longer says all four resolve it one
  way. The texts of those other steps still name the manifest and not the file.

The fallback cases run scratch copies of the two scripts from `source/scripts/`. They hold for
every assistant because the code of the `plugin_version` function in each built copy is
compared with the source's in `TheFunctionIsTheSameInEveryPackage`. The docstring is left out
of that comparison: the hook's names a host value, which the build fills in per assistant.

**What this cannot establish.** That a live assistant runs the hook and hands the guide its
text: the hook is started here directly, and not through an assistant or through the hook
adapter four of the packages use. Nor what the guide then writes in a feedback entry. Only a
run on a real assistant observes those. It was run on Linux only; the "cannot be read" case
puts a directory where the file would be, which fails differently on Windows (a permission
error) and is caught there as the same `OSError`.

No phrase-level pattern is matched one line at a time here: the prose checks collapse
whitespace first, so a re-wrapped sentence is still found (INV-346).

Standard library only; nothing under `source/` is imported into this process (INV-108).

Run:  python3 -m unittest discover -s tests
"""
import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from _built import SOURCE_DIR, built, host_ids, load_declaration  # a package per assistant

HOSTS = tuple(host_ids())
VERSION = load_declaration(SOURCE_DIR)["version"]
HOOK = "feedback-capture.py"
PACKAGER = "package_bootcamp.py"
HOST_FILE = "bootcamp_host.json"
ONBOARDING = SOURCE_DIR / "skills" / "bootcamp-onboarding"
DATE = "20261117"

#: The modules beside each script that it cannot run without. A scratch copy takes them along.
#: Without its secret scanner the packager packages nothing, by design.
SIBLINGS = {HOOK: (), PACKAGER: ("secret_patterns.py",)}

#: The value each script reports when nothing resolves. The two spellings differ and #31 keeps
#: both.
UNRESOLVED = {HOOK: "Unknown", PACKAGER: "unknown"}

#: Fixture versions. None is a version this repository has released, so a result that carries
#: one says which file it was read from.
FROM_HOST_FILE = "31.0.1"
FROM_ROOT_MANIFEST = "31.0.2"
FROM_CLAUDE_MANIFEST = "31.0.3"

#: What a `bootcamp_host.json` that gives no version can hold. `None` is no file at all, and
#: `DIRECTORY` puts a directory where the file would be, so that opening it fails.
DIRECTORY = object()
NO_VERSION = {
    "missing": None,
    "cannot be read": DIRECTORY,
    "empty file": b"",
    "not valid JSON": b"{not json",
    "not valid UTF-8": b'\xff\xfe{"bootcamp_version": "31.0.1"}',
    "a JSON list": b'["31.0.1"]',
    "a JSON string": b'"31.0.1"',
    "a JSON null": b"null",
    "no such key": b'{"host": "claude", "version": "31.0.1"}',
    "the key is null": b'{"bootcamp_version": null}',
    "the key is a number": b'{"bootcamp_version": 31}',
    "the key is a list": b'{"bootcamp_version": ["31.0.1"]}',
    "the key is an object": b'{"bootcamp_version": {"version": "31.0.1"}}',
    "the key is an empty string": b'{"bootcamp_version": ""}',
    "the key is only whitespace": b'{"bootcamp_version": "  \\n"}',
}


def only(root, name):
    """The one file called ``name`` in a built package; more or fewer is an error."""
    found = sorted(root.rglob(name))
    if len(found) != 1:
        raise AssertionError("%s: expected one %s, found %s" % (root.name, name, found))
    return found[0]


def scratch_project(root):
    """A bootcamp project with something for the `share` profile to package."""
    root = Path(root)
    (root / "config").mkdir(parents=True)
    (root / "config" / "bootcamp_progress.json").write_text("{}\n", encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "bootcamp_recap.pdf").write_bytes(b"recap")
    return root


def run(script, project, *args, stdin=""):
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        input=stdin, capture_output=True, text=True, encoding="utf-8",
        cwd=str(project), timeout=120,
    )
    if proc.returncode != 0 or "Traceback" in proc.stderr:
        raise AssertionError("%s exited %d:\n%s" % (script, proc.returncode, proc.stderr))
    return proc


def hook_context(script, project):
    """The text the hook injects when the bootcamper asks to give feedback."""
    proc = run(script, project, stdin=json.dumps({"prompt": "I have feedback"}))
    return json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]


def hook_version(script, project):
    """The version the hook hands the guide, read out of the sentence that carries it."""
    found = re.findall(r"the plugin version, which is (.*?) -- already resolved",
                       hook_context(script, project))
    if len(found) != 1:
        raise AssertionError("the hook's version sentence was found %d times" % len(found))
    return found[0]


def packager_version(script, project):
    """`plugin_version` in the manifest the packager would write (`--dry-run` prints it)."""
    proc = run(script, project, "--profile", "share", "--dry-run", "--date", DATE,
               "--project-root", str(project))
    return json.loads(proc.stdout)["plugin_version"]


REPORTED = {HOOK: hook_version, PACKAGER: packager_version}


def plugin_version_code(path):
    """The code of the ``plugin_version`` function in a script, without its docstring."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    found = [node for node in ast.walk(tree)
             if isinstance(node, ast.FunctionDef) and node.name == "plugin_version"]
    if len(found) != 1:
        raise AssertionError("%s: expected one plugin_version(), found %d" % (path, len(found)))
    function = found[0]
    if ast.get_docstring(function) is not None:
        function.body = function.body[1:]
    return ast.dump(function)


def collapsed(path):
    """A file's text with every run of whitespace made one space, so a wrap changes nothing."""
    return " ".join(Path(path).read_text(encoding="utf-8").split())


def paragraphs(path):
    """The blank-line-separated blocks of a file, each with its whitespace collapsed."""
    text = Path(path).read_text(encoding="utf-8")
    return [" ".join(block.split()) for block in re.split(r"\n\s*\n", text) if block.strip()]


class Layout:
    """A scratch package directory holding a copy of one script, and a scratch project.

    ``host`` is what `bootcamp_host.json` beside the script holds: a version string, raw
    bytes, ``DIRECTORY``, or ``None`` for no file. ``root_manifest`` and ``claude_manifest``
    are the versions written to `../plugin.json` and `../.claude-plugin/plugin.json`, or
    ``None`` for no file.
    """

    def __init__(self, script, host=None, root_manifest=None, claude_manifest=None):
        self.name = script
        self.host = host
        self.root_manifest = root_manifest
        self.claude_manifest = claude_manifest

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.package = base / "package"
        self.scripts = self.package / "scripts"
        self.scripts.mkdir(parents=True)
        self.script = self.scripts / self.name
        for name in (self.name,) + SIBLINGS[self.name]:
            shutil.copyfile(SOURCE_DIR / "scripts" / name, self.scripts / name)
        self.project = scratch_project(base / "project")
        if self.host is DIRECTORY:
            (self.scripts / HOST_FILE).mkdir()
        elif isinstance(self.host, bytes):
            (self.scripts / HOST_FILE).write_bytes(self.host)
        elif self.host is not None:
            self.write_host_file(self.scripts, self.host)
        if self.root_manifest is not None:
            self.write_manifest(self.package / "plugin.json", self.root_manifest)
        if self.claude_manifest is not None:
            self.write_manifest(self.package / ".claude-plugin" / "plugin.json",
                                self.claude_manifest)
        return self

    def __exit__(self, *exc):
        self.tmp.cleanup()

    @staticmethod
    def write_host_file(directory, version):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / HOST_FILE).write_text(
            json.dumps({"host": "scratch", "bootcamp_version": version}), encoding="utf-8")

    @staticmethod
    def write_manifest(path, version):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"name": "scratch", "version": version}), encoding="utf-8")

    def reported(self):
        return REPORTED[self.name](self.script, self.project)


class EveryPackageCarriesTheVersionBesideBothScripts(unittest.TestCase):
    """What the fix reads has to be there, on every assistant, or it fixes nothing."""

    def test_the_build_lists_five_assistants_or_more(self):
        self.assertGreaterEqual(len(HOSTS), 5, HOSTS)
        self.assertEqual(len(HOSTS), len(set(HOSTS)))

    def test_the_declared_version_is_a_version(self):
        self.assertRegex(VERSION, r"^\d+\.\d+\.\d+")
        self.assertNotIn(VERSION, (FROM_HOST_FILE, FROM_ROOT_MANIFEST, FROM_CLAUDE_MANIFEST))

    def test_the_host_file_sits_beside_each_script_and_carries_the_version(self):
        for host in HOSTS:
            for name in (HOOK, PACKAGER):
                with self.subTest(host=host, script=name):
                    beside = only(built(host), name).parent / HOST_FILE
                    self.assertTrue(beside.is_file(),
                                    "%s has no %s beside %s" % (host, HOST_FILE, name))
                    data = json.loads(beside.read_text(encoding="utf-8"))
                    self.assertEqual(VERSION, data["bootcamp_version"])


class TheHookReportsTheBuiltVersionInEveryPackage(unittest.TestCase):
    def test_the_injected_text_carries_the_built_version(self):
        for host in HOSTS:
            with self.subTest(host=host), tempfile.TemporaryDirectory() as tmp:
                project = scratch_project(Path(tmp) / "project")
                context = hook_context(only(built(host), HOOK), project)
                self.assertIn(
                    "the plugin version, which is %s -- already resolved" % VERSION, context,
                    "on %s the feedback hook does not hand the guide the version of the "
                    "package it ships in" % host)
                self.assertNotIn("which is Unknown", context)

    def test_the_hook_still_says_nothing_outside_a_bootcamp(self):
        """The version lookup must not make the hook speak where it was silent."""
        for host in HOSTS:
            with self.subTest(host=host), tempfile.TemporaryDirectory() as tmp:
                proc = run(only(built(host), HOOK), tmp,
                           stdin=json.dumps({"prompt": "I have feedback"}))
                self.assertEqual("", proc.stdout)


class ThePackagerReportsTheBuiltVersionInEveryPackage(unittest.TestCase):
    def test_the_archive_records_and_prints_the_built_version(self):
        for host in HOSTS:
            with self.subTest(host=host), tempfile.TemporaryDirectory() as tmp:
                project = scratch_project(Path(tmp) / "project")
                run(only(built(host), PACKAGER), project, "--profile", "share",
                    "--date", DATE, "--project-root", str(project))
                root = "senzing-bootcamp-share-%s" % DATE
                archive = project / "backups" / "packages" / ("%s.zip" % root)
                with zipfile.ZipFile(archive) as bundle:
                    manifest = json.loads(bundle.read("%s/PACKAGE_MANIFEST.json" % root))
                    first = bundle.read("%s/OPEN_ME_FIRST.md" % root).decode("utf-8")
                self.assertEqual(
                    VERSION, manifest["plugin_version"],
                    "on %s the packager does not record the version of the package it "
                    "ships in" % host)
                self.assertIn(" %s on %s." % (VERSION, manifest["created"]), first)
                self.assertNotIn(" unknown on ", first)

    def test_the_dry_run_reports_the_same_version(self):
        for host in HOSTS:
            with self.subTest(host=host), tempfile.TemporaryDirectory() as tmp:
                project = scratch_project(Path(tmp) / "project")
                self.assertEqual(VERSION, packager_version(only(built(host), PACKAGER), project))
                self.assertFalse((project / "backups").exists(), "a dry run wrote something")


class TheFunctionIsTheSameInEveryPackage(unittest.TestCase):
    """Why the fallback cases below, run on copies from `source/`, hold on every assistant."""

    def test_each_built_copy_matches_the_source(self):
        for name in (HOOK, PACKAGER):
            expected = plugin_version_code(SOURCE_DIR / "scripts" / name)
            self.assertIn(HOST_FILE, expected)
            self.assertIn("bootcamp_version", expected)
            for host in HOSTS:
                with self.subTest(host=host, script=name):
                    self.assertEqual(
                        expected, plugin_version_code(only(built(host), name)),
                        "the build changed the code of plugin_version() in %s for %s, so the "
                        "fallback cases in this file no longer speak for that package"
                        % (name, host))


class TheHostFileComesFirst(unittest.TestCase):
    def test_it_wins_over_every_manifest(self):
        for name in (HOOK, PACKAGER):
            with self.subTest(script=name), Layout(
                    name, host=FROM_HOST_FILE, root_manifest=FROM_ROOT_MANIFEST,
                    claude_manifest=FROM_CLAUDE_MANIFEST) as layout:
                self.assertEqual(FROM_HOST_FILE, layout.reported())

    def test_it_is_enough_with_no_manifest_at_all(self):
        for name in (HOOK, PACKAGER):
            with self.subTest(script=name), Layout(name, host=FROM_HOST_FILE) as layout:
                self.assertEqual(FROM_HOST_FILE, layout.reported())


class NoVersionInTheHostFileFallsThrough(unittest.TestCase):
    """Each case exits 0 with no traceback: `run` fails the test otherwise."""

    def test_to_the_manifest_when_there_is_one(self):
        for name in (HOOK, PACKAGER):
            for case, content in NO_VERSION.items():
                with self.subTest(script=name, case=case), Layout(
                        name, host=content, claude_manifest=FROM_CLAUDE_MANIFEST) as layout:
                    self.assertEqual(FROM_CLAUDE_MANIFEST, layout.reported())

    def test_to_the_unresolved_value_when_there_is_none(self):
        for name in (HOOK, PACKAGER):
            for case, content in NO_VERSION.items():
                with self.subTest(script=name, case=case), Layout(name, host=content) as layout:
                    self.assertEqual(UNRESOLVED[name], layout.reported())

    def test_the_two_unresolved_spellings_are_kept(self):
        self.assertEqual({HOOK: "Unknown", PACKAGER: "unknown"}, UNRESOLVED)
        for name in (HOOK, PACKAGER):
            with self.subTest(script=name), Layout(name) as layout:
                self.assertEqual(UNRESOLVED[name], layout.reported())


class TheManifestLookupsAreTheOnesEachScriptHad(unittest.TestCase):
    def test_the_hook_reads_the_claude_path_only(self):
        with Layout(HOOK, claude_manifest=FROM_CLAUDE_MANIFEST) as layout:
            self.assertEqual(FROM_CLAUDE_MANIFEST, layout.reported())
        with Layout(HOOK, root_manifest=FROM_ROOT_MANIFEST,
                    claude_manifest=FROM_CLAUDE_MANIFEST) as layout:
            self.assertEqual(FROM_CLAUDE_MANIFEST, layout.reported())
        with Layout(HOOK, root_manifest=FROM_ROOT_MANIFEST) as layout:
            self.assertEqual(
                "Unknown", layout.reported(),
                "the hook read ../plugin.json, a manifest path #31 leaves out of its lookup")

    def test_the_packager_reads_the_root_manifest_then_the_claude_path(self):
        with Layout(PACKAGER, root_manifest=FROM_ROOT_MANIFEST,
                    claude_manifest=FROM_CLAUDE_MANIFEST) as layout:
            self.assertEqual(FROM_ROOT_MANIFEST, layout.reported())
        with Layout(PACKAGER, root_manifest=FROM_ROOT_MANIFEST) as layout:
            self.assertEqual(FROM_ROOT_MANIFEST, layout.reported())
        with Layout(PACKAGER, claude_manifest=FROM_CLAUDE_MANIFEST) as layout:
            self.assertEqual(FROM_CLAUDE_MANIFEST, layout.reported())

    def test_a_manifest_that_holds_no_version_gives_the_unresolved_value(self):
        for name in (HOOK, PACKAGER):
            with self.subTest(script=name), Layout(name) as layout:
                manifest = layout.package / ".claude-plugin" / "plugin.json"
                manifest.parent.mkdir()
                manifest.write_text(json.dumps({"name": "scratch"}), encoding="utf-8")
                self.assertEqual(UNRESOLVED[name], layout.reported())


class NothingIsSearchedFor(unittest.TestCase):
    """INV-252: a `bootcamp_host.json` anywhere but beside the script is not this script's."""

    def elsewhere(self, layout):
        return {
            "above the script's directory": layout.package,
            "below the script's directory": layout.scripts / "nested",
            "beside the package": layout.package.parent,
            "in the project": layout.project,
            "in the project's own scripts directory": layout.project / "scripts",
            "in the project's config directory": layout.project / "config",
        }

    def test_a_host_file_elsewhere_is_not_read(self):
        for name in (HOOK, PACKAGER):
            with Layout(name) as probe:
                places = sorted(self.elsewhere(probe))
            self.assertGreaterEqual(len(places), 6)
            for place in places:
                with self.subTest(script=name, place=place), Layout(name) as layout:
                    Layout.write_host_file(self.elsewhere(layout)[place], FROM_HOST_FILE)
                    self.assertEqual(
                        UNRESOLVED[name], layout.reported(),
                        "%s read a %s %s: it is looking for one" % (name, HOST_FILE, place))

    def test_a_manifest_elsewhere_is_not_read_either(self):
        for name in (HOOK, PACKAGER):
            with self.subTest(script=name), Layout(name) as layout:
                Layout.write_manifest(layout.project / "plugin.json", FROM_ROOT_MANIFEST)
                Layout.write_manifest(layout.project / ".claude-plugin" / "plugin.json",
                                      FROM_CLAUDE_MANIFEST)
                Layout.write_manifest(layout.package.parent / "plugin.json", FROM_ROOT_MANIFEST)
                self.assertEqual(UNRESOLVED[name], layout.reported())


class TheOnboardingSentenceSaysWhatTheStepsDo(unittest.TestCase):
    def setUp(self):
        self.flow = ONBOARDING / "onboarding-flow.md"
        naming = [block for block in paragraphs(self.flow) if HOST_FILE in block]
        self.assertEqual(1, len(naming), "one paragraph of onboarding-flow.md names the file")
        self.sentence = naming[0]

    def test_the_old_claim_is_gone(self):
        text = collapsed(self.flow)
        self.assertNotIn("all four report one version", text)
        self.assertNotIn(
            "Every other step needing the plugin version resolves it the same way", text)

    def test_it_names_the_step_that_reads_the_host_file_first(self):
        match = re.search(
            r"The feedback entry \(`feedback\.md`\) reads `bootcamp_version` from "
            r"`bootcamp_host\.json` first", self.sentence)
        self.assertIsNotNone(match, self.sentence)
        self.assertIn("resolves the manifest this way only if", self.sentence[match.end():])

    def test_it_names_the_steps_that_resolve_the_manifest(self):
        before = self.sentence[:self.sentence.index("The feedback entry")]
        self.assertIn("resolve the manifest the same way as the WELCOME banner", before)
        for step in ("the recap header (`module-completion.md`)",
                     "the recap's provenance block (`../graduation/SKILL.md`)"):
            self.assertIn(step, before)
        self.assertNotIn("feedback.md", before)

    def test_the_named_files_exist(self):
        for relative in ("feedback.md", "module-completion.md", "../graduation/SKILL.md"):
            self.assertTrue((ONBOARDING / relative).is_file(), relative)

    def test_the_feedback_entry_does_read_the_host_file_first(self):
        text = collapsed(ONBOARDING / "feedback.md")
        first = text.index("**Plugin version:** `bootcamp_version` in the `bootcamp_host.json`")
        fallback = text.index("Only if that file cannot be read", first)
        self.assertIn("plugin manifest", text[fallback:fallback + 200])

    def test_no_other_step_changed_how_it_resolves_the_version(self):
        """The banner, the recap header and the provenance block still name the manifest."""
        banner = collapsed(self.flow)
        self.assertIn("Read the plugin version from the plugin manifest", banner)
        for relative in ("module-completion.md", "../graduation/SKILL.md"):
            text = collapsed(ONBOARDING / relative)
            self.assertIn("plugin manifest", text, relative)
            self.assertNotIn("bootcamp_version", text, relative)
            self.assertNotIn(HOST_FILE, text, relative)


if __name__ == "__main__":
    unittest.main()
