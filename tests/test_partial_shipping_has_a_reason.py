"""Every source file that ships to some assistants and not others has a recorded reason (#12).

A file under `source/` normally reaches every assistant's package. A host's layout can drop one
(`"<path>": null` in `hosts/<assistant>/host.json`), and the build accepts that silently. That is
how `model-selection.md`, a maintainer page, stayed in the Claude package after the other four
assistants dropped it: nothing asked why one package carried a file the others did not.

⛔ **(INV-430) A source file that ships to some assistants and not others has a recorded reason.**

⛔ **(INV-430) No package carries the maintainer page `model-selection.md`, and no package names `effort-mechanisms`.**

Enforces **INV-430** (registered 2026-11-16).

What must hold:

1. `PARTIAL` is the one table of the source paths that ship to some assistants and not others,
   with the reason for each. A partial file that no entry covers fails.
2. An entry may name a directory, and then covers every file under it.
3. An entry whose path is no longer partial fails, so the table cannot go stale: the path is
   gone, it now ships to every assistant, or it ships to none.
4. A file that ships to no assistant is not partial and needs no reason. `source/hooks/fallbacks/`
   is the standing case: the build reads those files and writes none of them into a package.
5. No package carries `model-selection.md`. The page is at `docs/model-selection.md` in this
   repository, beside `docs/effort-mechanisms.md`.
6. No file in any package names `effort-mechanisms`, the research page no package carries.

The shipped sets are not a hand list. `placed_files()` is the build's own answer to "which source
files does this host's package carry", computed from the layouts, and
`test_what_the_layouts_place_is_in_the_built_package` holds it against all five built packages.

**What this cannot establish.** That a recorded reason is true or still current: the table
makes a partial path a decision somebody wrote down, and a reviewer reads the reason. Nor does
it cover a path one package gets from `hosts/<assistant>/files/`, which is one assistant's by
construction, or a general rule that every path a package names resolves inside that package.

No phrase-level pattern (#12): the package scan searches each file's bytes for a file name, and
nothing here reads text one line at a time.

Run:  python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

from _built import REPO_ROOT, built

from tools.bootcamp_build.emit import IGNORED_NAMES, placed_files
from tools.bootcamp_build.model import SOURCE_DIR, host_ids, load_hosts

#: Source paths (relative to `source/`) that ship to some assistants and not others, and why.
#: A directory covers every file under it. Add an entry in the same change that makes a path
#: partial, and remove it in the change that ends that.
PARTIAL = {
    "commands": (
        "Claude installs a plugin's commands as files in `commands/`. The other four packages "
        "carry no commands directory: the build writes each command there as a skill of the same "
        "name, from the same source file (`_commands_as_skills` in `tools/bootcamp_build/emit.py`)."
    ),
    "hooks/README.md": (
        "The page documents the hooks under Claude's event names and Claude's `hooks.json`. Each "
        "of the other four assistants has no event for at least one hook it lists "
        "(`python3 -m tools.bootcamp_build check` names them), so the page would describe hooks "
        "their packages do not register."
    ),
}

#: The maintainer page issue #12 moved out of `source/`, and the research page it points at.
MAINTAINER_PAGE = "model-selection.md"
RESEARCH_PAGE = b"effort-mechanisms"


def source_files(source_dir=SOURCE_DIR):
    """Every file the build considers under ``source_dir``, as posix paths relative to it."""
    return sorted(
        path.relative_to(source_dir).as_posix() for path in source_dir.rglob("*")
        if path.is_file() and not (IGNORED_NAMES & set(path.relative_to(source_dir).parts))
        and path.relative_to(source_dir).as_posix() != "bootcamp.json")


def shipped_to(hosts=None, source_dir=SOURCE_DIR):
    """``{source path: the set of assistants whose package carries it}``, for every source file."""
    hosts = load_hosts() if hosts is None else hosts
    placed = {host.id: {path.as_posix() for path in placed_files(host, source_dir)} for host in hosts}
    return {relative: {host_id for host_id, files in placed.items() if relative in files}
            for relative in source_files(source_dir)}


def is_partial(carriers, hosts):
    """True when some assistants carry the file and some do not. None carrying it is not partial."""
    return 0 < len(carriers) < len(hosts)


def covers(entry, relative):
    return relative == entry or relative.startswith(entry + "/")


def unexplained(shipped, table, hosts):
    """Partial source paths no table entry covers, each with the assistants that carry it."""
    return ["%s (only in: %s)" % (relative, ", ".join(sorted(carriers)))
            for relative, carriers in sorted(shipped.items())
            if is_partial(carriers, hosts) and not any(covers(entry, relative) for entry in table)]


def stale(shipped, table, hosts):
    """Table entries that no longer name a partial path, each with what is true of it now."""
    problems = []
    for entry in sorted(table):
        covered = {relative: carriers for relative, carriers in shipped.items() if covers(entry, relative)}
        if not covered:
            problems.append("%s: no source file is at or under this path" % entry)
        for relative, carriers in sorted(covered.items()):
            if len(carriers) == len(hosts):
                problems.append("%s: %s now ships to every assistant" % (entry, relative))
            elif not carriers:
                problems.append("%s: %s ships to no assistant, which is not partial" % (entry, relative))
    return problems


def package_path(host, relative):
    """Where ``host``'s layout puts one source file inside its package, or None when it drops it."""
    entries = [entry for entry in host.layout if covers(entry, relative)]
    if not entries:
        return None
    entry = max(entries, key=len)   # the most specific entry wins, as in the build
    destination = host.layout[entry]
    if destination is None:
        return None
    return Path(destination) if relative == entry else Path(destination) / Path(relative).relative_to(entry)


def package_files(root):
    return sorted(path for path in root.rglob("*") if path.is_file())


class EveryPartialPathHasAReason(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hosts = load_hosts()
        cls.ids = [host.id for host in cls.hosts]
        cls.shipped = shipped_to(cls.hosts)

    def test_the_scan_reads_every_assistant_and_the_whole_source(self):
        """It cannot pass on nothing: five assistants and the source tree, each file in one outcome.

        The floors are well under what was measured on 2026-11-16 (97 source files: 81 in every
        package, 6 partial, 10 in none), and none requires a partial path to exist: a tree with
        no partial path and an empty table is a pass.
        """
        self.assertEqual(sorted(host_ids()), sorted(self.ids))
        self.assertEqual(5, len(self.ids))
        self.assertGreaterEqual(len(self.shipped), 80, "far fewer source files found than exist")
        everywhere = [r for r, carriers in self.shipped.items() if len(carriers) == len(self.ids)]
        partial = [r for r, carriers in self.shipped.items() if is_partial(carriers, self.ids)]
        nowhere = [r for r, carriers in self.shipped.items() if not carriers]
        self.assertGreaterEqual(len(everywhere), 50)
        self.assertIn("skills/bootcamp-onboarding/SKILL.md", everywhere)
        self.assertEqual(len(self.shipped), len(everywhere) + len(partial) + len(nowhere))
        for carriers in self.shipped.values():
            self.assertLessEqual(carriers, set(self.ids))

    def test_a_partial_path_with_no_reason_fails(self):
        self.assertEqual(
            [], unexplained(self.shipped, PARTIAL, self.ids),
            "source file(s) that ship to some assistants and not others, with no entry in PARTIAL. "
            "Either ship the file to every assistant (or to none), or add its path to PARTIAL in "
            "this file with the reason.")

    def test_a_table_entry_that_is_no_longer_partial_fails(self):
        self.assertEqual(
            [], stale(self.shipped, PARTIAL, self.ids),
            "PARTIAL entries that no longer name a path shipping to only some assistants. Remove "
            "the entry, or narrow a directory entry to the files that are still partial.")

    def test_every_reason_is_written_out(self):
        for entry, reason in PARTIAL.items():
            with self.subTest(entry=entry):
                self.assertIsInstance(reason, str)
                self.assertGreaterEqual(len(reason.split()), 8, "a reason is a sentence, not a tag")

    def test_a_file_that_ships_to_no_assistant_needs_no_reason(self):
        """With an empty table, no file that ships nowhere is reported, and none has an entry."""
        nowhere = sorted(r for r, carriers in self.shipped.items() if not carriers)
        if (SOURCE_DIR / "hooks" / "fallbacks").is_dir():
            # The standing case: the build reads these files and places none of them.
            self.assertTrue([r for r in nowhere if r.startswith("hooks/fallbacks/")],
                            "source/hooks/fallbacks/ now ships somewhere, or holds no file")
        reported = {line.split(" (only in: ")[0] for line in unexplained(self.shipped, {}, self.ids)}
        for relative in nowhere:
            with self.subTest(path=relative):
                self.assertNotIn(relative, reported)
                self.assertFalse(any(covers(entry, relative) for entry in PARTIAL))

    def test_a_directory_entry_covers_the_files_under_it(self):
        """On the live tree: remove a directory entry, and every file under it is reported.

        `TheChecksReportEachCase` holds the same rule on synthetic sets, so this still means
        something on a day the table names no directory.
        """
        for entry in PARTIAL:
            if not (SOURCE_DIR / entry).is_dir():
                continue
            under = {r for r in self.shipped if covers(entry, r)}
            without = {key: value for key, value in PARTIAL.items() if key != entry}
            reported = {line.split(" (only in: ")[0]
                        for line in set(unexplained(self.shipped, without, self.ids))
                        - set(unexplained(self.shipped, PARTIAL, self.ids))}
            with self.subTest(entry=entry):
                self.assertTrue(under)
                self.assertEqual(under, reported)

    def test_removing_an_entry_reports_its_path(self):
        """Negative control on the live tree: each entry is what keeps its path from failing."""
        for entry in PARTIAL:
            with self.subTest(entry=entry):
                without = {key: value for key, value in PARTIAL.items() if key != entry}
                reported = (set(unexplained(self.shipped, without, self.ids))
                            - set(unexplained(self.shipped, PARTIAL, self.ids)))
                self.assertTrue(reported, "removing the entry reported nothing, so it explains nothing")
                self.assertTrue(all(covers(entry, line.split(" (only in: ")[0]) for line in reported),
                                reported)

    def test_what_the_layouts_place_is_in_the_built_package(self):
        """The shipped sets are the build's: every placed file is in that assistant's package."""
        checked = 0
        for host in self.hosts:
            root = built(host.id)
            for relative, carriers in self.shipped.items():
                target = package_path(host, relative)
                with self.subTest(host=host.id, path=relative):
                    self.assertEqual(host.id in carriers, target is not None)
                    if target is not None:
                        self.assertTrue((root / target).is_file(), "%s is not in the package" % target)
                        checked += 1
        self.assertGreaterEqual(checked, len(self.hosts) * 50)

    def test_a_partial_path_is_absent_from_the_packages_that_drop_it(self):
        """For each partial file, a package that drops it has nothing at the path a carrier uses."""
        checked = owed = 0
        by_id = {host.id: host for host in self.hosts}
        for relative, carriers in sorted(self.shipped.items()):
            if not is_partial(carriers, self.ids):
                continue
            owed += len(self.ids) - len(carriers)
            where = {package_path(by_id[host_id], relative) for host_id in carriers}
            for host_id in sorted(set(self.ids) - carriers):
                for target in where:
                    with self.subTest(host=host_id, path=relative):
                        self.assertFalse((built(host_id) / target).exists())
                        checked += 1
        self.assertGreaterEqual(checked, owed, "a partial path was not looked for where it is dropped")


class TheChecksReportEachCase(unittest.TestCase):
    """Negative controls on synthetic shipped sets (INV-265): each rule fails when it should."""

    HOSTS = ["a", "b", "c"]

    def test_a_file_one_assistant_carries_is_reported(self):
        shipped = {"docs/model-selection.md": {"a"}, "skills/x/SKILL.md": {"a", "b", "c"}}
        self.assertEqual(["docs/model-selection.md (only in: a)"], unexplained(shipped, {}, self.HOSTS))

    def test_a_file_all_but_one_assistant_carry_is_reported(self):
        shipped = {"scripts/x.py": {"a", "b"}}
        self.assertEqual(["scripts/x.py (only in: a, b)"], unexplained(shipped, {}, self.HOSTS))

    def test_an_entry_for_the_file_or_a_directory_above_it_explains_it(self):
        shipped = {"commands/go.md": {"a"}, "commands/deep/stop.md": {"a"}}
        self.assertEqual([], unexplained(shipped, {"commands": "why"}, self.HOSTS))
        self.assertEqual(["commands/deep/stop.md (only in: a)"],
                         unexplained(shipped, {"commands/go.md": "why"}, self.HOSTS))

    def test_a_directory_entry_does_not_cover_a_path_that_only_starts_with_its_name(self):
        shipped = {"commands-extra/go.md": {"a"}}
        self.assertEqual(["commands-extra/go.md (only in: a)"],
                         unexplained(shipped, {"commands": "why"}, self.HOSTS))

    def test_a_file_no_assistant_carries_is_not_reported(self):
        shipped = {"hooks/fallbacks/x.md": set()}
        self.assertEqual([], unexplained(shipped, {}, self.HOSTS))

    def test_a_file_every_assistant_carries_is_not_reported(self):
        shipped = {"skills/x/SKILL.md": {"a", "b", "c"}}
        self.assertEqual([], unexplained(shipped, {}, self.HOSTS))

    def test_an_entry_for_a_path_that_is_gone_is_stale(self):
        self.assertEqual(["docs/model-selection.md: no source file is at or under this path"],
                         stale({"skills/x/SKILL.md": {"a", "b", "c"}},
                               {"docs/model-selection.md": "why"}, self.HOSTS))

    def test_an_entry_for_a_path_every_assistant_now_carries_is_stale(self):
        self.assertEqual(["hooks/README.md: hooks/README.md now ships to every assistant"],
                         stale({"hooks/README.md": {"a", "b", "c"}}, {"hooks/README.md": "why"},
                               self.HOSTS))

    def test_an_entry_for_a_path_no_assistant_carries_is_stale(self):
        self.assertEqual(["hooks/README.md: hooks/README.md ships to no assistant, which is not partial"],
                         stale({"hooks/README.md": set()}, {"hooks/README.md": "why"}, self.HOSTS))

    def test_a_directory_entry_is_stale_for_each_file_under_it_that_is_not_partial(self):
        shipped = {"commands/go.md": {"a"}, "commands/stop.md": {"a", "b", "c"}}
        self.assertEqual(["commands: commands/stop.md now ships to every assistant"],
                         stale(shipped, {"commands": "why"}, self.HOSTS))

    def test_an_entry_that_is_still_partial_is_not_stale(self):
        self.assertEqual([], stale({"commands/go.md": {"a"}}, {"commands": "why"}, self.HOSTS))


class NoPackageCarriesTheMaintainerPage(unittest.TestCase):
    def test_the_page_is_in_this_repository_and_not_under_source(self):
        self.assertTrue((REPO_ROOT / "docs" / MAINTAINER_PAGE).is_file())
        self.assertTrue((REPO_ROOT / "docs" / "effort-mechanisms.md").is_file())
        self.assertEqual([], [path.relative_to(REPO_ROOT).as_posix()
                              for path in SOURCE_DIR.rglob(MAINTAINER_PAGE)])

    def test_the_paths_the_page_names_from_its_new_home_resolve(self):
        """The move changed where its relative paths start: each one is a file, counted from `docs/`."""
        text = (REPO_ROOT / "docs" / MAINTAINER_PAGE).read_text(encoding="utf-8")
        relative = re.findall(r"`(\.\./[^`\s]+)`", text)
        self.assertGreaterEqual(len(relative), 2, "the page names no path outside `docs/`")
        for path in relative + ["effort-mechanisms.md"]:
            with self.subTest(path=path):
                self.assertTrue((REPO_ROOT / "docs" / path).resolve().is_file())
        self.assertNotIn("`../skills/", text, "a path still counted from inside a package")
        self.assertIn("`effort-mechanisms.md`, beside this file", " ".join(text.split()))

    def test_no_package_carries_it(self):
        for host_id in host_ids():
            files = package_files(built(host_id))
            with self.subTest(host=host_id):
                self.assertGreaterEqual(len(files), 40, "the package was not built")
                self.assertEqual([], [path.relative_to(built(host_id)).as_posix()
                                      for path in files if path.name == MAINTAINER_PAGE])

    def test_no_file_in_any_package_names_the_research_page(self):
        """`docs/effort-mechanisms.md` is in no package, so a package naming it points nowhere."""
        for host_id in host_ids():
            root = built(host_id)
            files = package_files(root)
            with self.subTest(host=host_id):
                self.assertGreaterEqual(len(files), 40, "the package was not built")
                self.assertEqual([], [path.relative_to(root).as_posix() for path in files
                                      if RESEARCH_PAGE in path.read_bytes()])

    def test_the_needle_finds_the_reference_where_it_is_written(self):
        """Negative control: the maintainer page names the research page, and the scan sees it."""
        self.assertIn(RESEARCH_PAGE, (REPO_ROOT / "docs" / MAINTAINER_PAGE).read_bytes())
        self.assertIn(RESEARCH_PAGE, b"`docs/effort-mechanisms.md` records the research")


if __name__ == "__main__":
    unittest.main()
