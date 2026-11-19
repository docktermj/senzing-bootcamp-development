"""Every source file that ships to some assistants and not others has a recorded reason (#12).

A file under `source/` normally reaches every assistant's package. A host's layout can drop one
(`"<path>": null` in `hosts/<assistant>/host.json`), and the build accepts that silently. That is
how `model-selection.md`, a maintainer page, stayed in the Claude package after the other four
assistants dropped it: nothing asked why one package carried a file the others did not.

⛔ **(INV-430) A source file that ships to some assistants and not others has a recorded reason.**

⛔ **(INV-430) No package carries the maintainer page `model-selection.md`, and no package names `effort-mechanisms`.**

⛔ **(INV-430) No package names a partial source file it drops.** Added by #26 as INV-430's
dated note of 2026-11-17, applied by the maintainer on 2026-11-18.

Enforces **INV-430** (registered 2026-11-16), and **INV-055** where it says the opt-out is
documented: item 9 below holds that in every package.

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
7. No file in a package names a partial source file that package drops (#26): neither its path
   under `source/` nor the path a package that carries it uses. The files come from the shipped
   sets, and each is one a `PARTIAL` entry covers. The match is on a file's bytes, so a script's
   comment counts as a skill's prose does, and `../../hooks/README.md` is found as
   `hooks/README.md` is.
8. No file in any package names `hooks/README.md`, except that page itself in a package that
   carries it (#26). Item 7 does not reach a package that carries the page, and the pointers
   #26 removed were in all five.
9. The ground rules in every package state both switches that turn the closing-question safety
   net off (INV-055, #26), in one list item that names no assistant's hook event. The hooks page
   was the only place that documented them, and four packages do not carry it.

The shipped sets are not a hand list. `placed_files()` is the build's own answer to "which source
files does this host's package carry", computed from the layouts, and
`test_what_the_layouts_place_is_in_the_built_package` holds it against all five built packages.

**What this cannot establish.** That a recorded reason is true or still current: the table
makes a partial path a decision somebody wrote down, and a reviewer reads the reason. Nor does
it cover a path one package gets from `hosts/<assistant>/files/`, which is one assistant's by
construction, or a general rule that every path a package names resolves inside that package.
Item 7 finds a path written out in full with forward slashes: a path put together at run time,
or a file named by its base name alone, is not found. Item 9 shows the switches are named, not
that a hook reads them on any assistant: `tests/test_stop_nudge_silence_and_opt_outs.py` holds
what the script does with each.

No phrase-level pattern (#12): the package scans search each file's bytes for a path or a file
name, and nothing here reads text one line at a time. The off-switch item (#26) is read through
`tests/_wrapped_text.py`, one list item at a time with whitespace collapsed (INV-346).

Run:  python3 -m unittest discover -s tests
"""

import re
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from _built import REPO_ROOT, built
from _wrapped_text import collapsed_items

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

#: The hooks page, relative to `source/`. Shared text pointed at it in all five packages while
#: four of them dropped it (#26).
HOOKS_PAGE = "hooks/README.md"
#: The ground rules, relative to `source/`: text every package carries.
GROUND_RULES = "skills/bootcamp-onboarding/ground-rules.md"
#: The two switches `source/scripts/stop-nudge.py` reads in `nudge_disabled()` (INV-055).
OFF_SWITCH_VARIABLE = "SENZING_BOOTCAMP_DISABLE_STOP_NUDGE"
OFF_SWITCH_KEY = "disable_stop_nudge: true"
#: The values the script's `truthy()` reads as on.
OFF_SWITCH_VALUES = ("`1`", "`true`", "`yes`", "`on`")


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


def names_of(relative, carriers, by_id):
    """The byte strings that name one source file: its path, and where each carrier puts it."""
    paths = {relative} | {package_path(by_id[host_id], relative).as_posix() for host_id in carriers}
    return sorted(path.encode("utf-8") for path in paths)


def dropped_references(shipped, hosts, root_of):
    """``(problems, partial files checked, {package read: its file count})``.

    A problem is one file, in a package that drops a partial source file, whose bytes hold a name
    of that file. ``root_of(host id)`` gives the root of that host's package.
    """
    by_id = {host.id: host for host in hosts}
    contents, problems, checked = {}, [], []
    for relative, carriers in sorted(shipped.items()):
        if not is_partial(carriers, by_id):
            continue
        checked.append(relative)
        needles = names_of(relative, carriers, by_id)
        for host_id in sorted(set(by_id) - carriers):
            if host_id not in contents:
                root = root_of(host_id)
                contents[host_id] = {path.relative_to(root).as_posix(): path.read_bytes()
                                     for path in package_files(root)}
            for name, data in sorted(contents[host_id].items()):
                found = [needle.decode("utf-8") for needle in needles if needle in data]
                if found:
                    problems.append("%s: %s names %s" % (host_id, name, ", ".join(found)))
    return problems, checked, {host_id: len(files) for host_id, files in contents.items()}


def hook_events(hosts):
    """Every hook event name any assistant's mapping holds."""
    return sorted({name for host in hosts for name in host.hooks["events"].values() if name})


def events_named(text, events):
    """The event names ``text`` holds as words of their own, in the case the mapping gives."""
    return [name for name in events
            if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(name), text)]


def off_switch_items(text):
    """The list items of ``text`` that name the off-switch variable, whitespace collapsed."""
    return [flat for flat, _origin in collapsed_items(text) if OFF_SWITCH_VARIABLE in flat]


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


class NoPackageNamesAFileItDrops(unittest.TestCase):
    """#26: a package that drops a partial source file holds no pointer at it."""

    @classmethod
    def setUpClass(cls):
        cls.hosts = load_hosts()
        cls.ids = [host.id for host in cls.hosts]
        cls.by_id = {host.id: host for host in cls.hosts}
        cls.shipped = shipped_to(cls.hosts)

    def test_no_package_names_a_partial_file_it_drops(self):
        problems, checked, read = dropped_references(self.shipped, self.hosts, built)
        # It cannot pass on nothing (INV-265): every package is built, at least one partial file
        # was looked for, and every package that drops one was read in full.
        self.assertEqual(sorted(host_ids()), sorted(self.ids))
        for host_id in self.ids:
            with self.subTest(host=host_id):
                self.assertGreaterEqual(len(package_files(built(host_id))), 40, "the package was not built")
        self.assertGreaterEqual(
            len(checked), 1,
            "no partial source file was checked. If no source file is partial any more, this check "
            "holds nothing: remove it with the last PARTIAL entry.")
        self.assertEqual(sorted(r for r, carriers in self.shipped.items() if is_partial(carriers, self.ids)),
                         checked)
        for relative in checked:
            with self.subTest(path=relative):
                self.assertTrue(any(covers(entry, relative) for entry in PARTIAL))
        for entry in PARTIAL:
            with self.subTest(entry=entry):
                self.assertTrue([r for r in checked if covers(entry, r)], "no file under the entry was checked")
        droppers = set().union(*(set(self.ids) - self.shipped[relative] for relative in checked))
        self.assertTrue(droppers)
        self.assertEqual(droppers, set(read))
        for host_id, count in read.items():
            with self.subTest(host=host_id):
                self.assertEqual(len(package_files(built(host_id))), count)
        self.assertEqual(
            [], problems,
            "file(s) in a package that name a source file the package does not carry. State the fact "
            "the reader needs where the pointer is, or drop the pointer: text outside a host marker "
            "reaches every package.")

    def test_only_the_hooks_page_holds_its_own_path(self):
        """In every package, carriers included: the pointers #26 removed were in all five."""
        self.assertIn(HOOKS_PAGE, self.shipped)
        carriers = self.shipped[HOOKS_PAGE]
        self.assertTrue(carriers, "the hooks page ships to no assistant, so this check holds nothing")
        needles = names_of(HOOKS_PAGE, carriers, self.by_id)
        self.assertIn(HOOKS_PAGE.encode("utf-8"), needles)
        for host in self.hosts:
            root = built(host.id)
            files = package_files(root)
            own = package_path(host, HOOKS_PAGE)
            with self.subTest(host=host.id):
                self.assertGreaterEqual(len(files), 40, "the package was not built")
                self.assertEqual(host.id in carriers, own is not None and (root / own).is_file())
                self.assertEqual([], [path.relative_to(root).as_posix() for path in files
                                      if path.relative_to(root) != own
                                      and any(needle in path.read_bytes() for needle in needles)])


class TheReferenceScanReportsEachCase(unittest.TestCase):
    """Negative controls for `dropped_references` (INV-265): a reference is reported when present."""

    def setUp(self):
        self.scratch = Path(tempfile.mkdtemp(prefix="bootcamp-partial-"))
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

    def package(self, name, files):
        root = self.scratch / name
        for relative, data in files.items():
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_bytes(data)
        return root

    def test_a_reference_in_a_package_that_drops_the_file_is_reported(self):
        hosts = [SimpleNamespace(id="a", layout={"skills": "skills", "hooks/README.md": "hooks/README.md"}),
                 SimpleNamespace(id="b", layout={"skills": "skills", "hooks/README.md": None})]
        shipped = {"hooks/README.md": {"a"}, "skills/x/SKILL.md": {"a", "b"}}
        pointer = b"the gate, and why: [`hooks/README.md`](../../hooks/README.md).\n"
        roots = {"a": self.package("a", {"hooks/README.md": b"# Hooks\n", "skills/x/SKILL.md": pointer}),
                 "b": self.package("b", {"skills/x/SKILL.md": pointer, "scripts/gate.py": b"# no pointer\n"})}
        problems, checked, read = dropped_references(shipped, hosts, roots.__getitem__)
        self.assertEqual(["b: skills/x/SKILL.md names hooks/README.md"], problems)
        self.assertEqual(["hooks/README.md"], checked)
        self.assertEqual({"b": 2}, read, "the carrier is not read, and the dropper is read in full")

    def test_a_reference_in_a_script_comment_is_reported(self):
        hosts = [SimpleNamespace(id="a", layout={"scripts": "scripts", "hooks/README.md": "hooks/README.md"}),
                 SimpleNamespace(id="b", layout={"scripts": "scripts", "hooks/README.md": None})]
        shipped = {"hooks/README.md": {"a"}}
        roots = {"a": self.package("a", {"hooks/README.md": b"# Hooks\n"}),
                 "b": self.package("b", {"scripts/gate.py": b"# see (hooks/README.md, Gate column).\n"})}
        self.assertEqual(["b: scripts/gate.py names hooks/README.md"],
                         dropped_references(shipped, hosts, roots.__getitem__)[0])

    def test_the_path_a_carrier_uses_is_a_name_too(self):
        hosts = [SimpleNamespace(id="a", layout={"commands": "cmds"}),
                 SimpleNamespace(id="b", layout={"commands": None})]
        shipped = {"commands/go.md": {"a"}}
        roots = {"a": self.package("a", {"cmds/go.md": b"go\n"}),
                 "b": self.package("b", {"one.md": b"run `cmds/go.md`\n", "two.md": b"run `commands/go.md`\n",
                                         "three.md": b"run the go skill\n"})}
        self.assertEqual(["b: one.md names cmds/go.md", "b: two.md names commands/go.md"],
                         dropped_references(shipped, hosts, roots.__getitem__)[0])

    def test_no_reference_and_no_partial_file_report_nothing(self):
        hosts = [SimpleNamespace(id="a", layout={"hooks/README.md": "hooks/README.md"}),
                 SimpleNamespace(id="b", layout={"hooks/README.md": None})]
        roots = {"a": self.package("a", {"hooks/README.md": b"# Hooks\n"}),
                 "b": self.package("b", {"skills/x/SKILL.md": b"the hooks, and README.md\n"})}
        self.assertEqual(([], ["hooks/README.md"], {"b": 1}),
                         dropped_references({"hooks/README.md": {"a"}}, hosts, roots.__getitem__))
        # A file every assistant carries, or none does, is not looked for, and no package is read.
        self.assertEqual(([], [], {}),
                         dropped_references({"hooks/README.md": {"a", "b"}, "hooks/fallbacks/x.md": set()},
                                            hosts, roots.__getitem__))

    def test_a_pointer_put_back_into_a_built_package_is_reported(self):
        """On the live build: one pointer written into a package that drops the file is found."""
        hosts = load_hosts()
        ids = [host.id for host in hosts]
        by_id = {host.id: host for host in hosts}
        shipped = shipped_to(hosts)
        partial = sorted(r for r, carriers in shipped.items() if is_partial(carriers, ids))
        self.assertTrue(partial, "no partial source file to put a pointer back for")
        for relative in partial:
            dropper = sorted(set(ids) - shipped[relative])[0]
            copy = self.scratch / ("%s-%d" % (dropper, partial.index(relative)))
            shutil.copytree(built(dropper), copy)
            target = copy / package_path(by_id[dropper], GROUND_RULES)
            self.assertTrue(target.is_file(), "the package's ground rules were not found")
            target.write_bytes(target.read_bytes() + ("\n(`../../%s`)\n" % relative).encode("utf-8"))
            roots = {host_id: copy if host_id == dropper else built(host_id) for host_id in ids}
            with self.subTest(path=relative, host=dropper):
                self.assertEqual(
                    ["%s: %s names %s" % (dropper, target.relative_to(copy).as_posix(), relative)],
                    dropped_references(shipped, hosts, roots.__getitem__)[0])


class EveryPackageStatesTheOffSwitch(unittest.TestCase):
    """#26: the two switches are in the ground rules of every package (INV-055)."""

    @classmethod
    def setUpClass(cls):
        cls.hosts = load_hosts()
        cls.events = hook_events(cls.hosts)

    def ground_rules(self, host):
        target = package_path(host, GROUND_RULES)
        self.assertIsNotNone(target, "%s drops the ground rules" % host.id)
        path = built(host.id) / target
        self.assertTrue(path.is_file(), "%s is not in the package" % target)
        return path

    def test_both_switches_are_named_in_every_package(self):
        self.assertEqual(5, len(self.hosts))
        for host in self.hosts:
            data = self.ground_rules(host).read_bytes()
            with self.subTest(host=host.id):
                self.assertIn(OFF_SWITCH_VARIABLE.encode("utf-8"), data)
                self.assertIn(OFF_SWITCH_KEY.encode("utf-8"), data)

    def test_one_item_states_the_switches_their_values_and_the_way_back(self):
        for host in self.hosts:
            items = off_switch_items(self.ground_rules(host).read_text(encoding="utf-8"))
            with self.subTest(host=host.id):
                self.assertEqual(1, len(items), "the off switch is stated in one place in the ground rules")
                item = items[0]
                self.assertIn("`%s` environment variable" % OFF_SWITCH_VARIABLE, item)
                self.assertIn("top-level key `%s` in `config/bootcamp_preferences.yaml`" % OFF_SWITCH_KEY, item)
                for value in OFF_SWITCH_VALUES:
                    self.assertIn(value, item)
                self.assertIn("To turn it back on", item)
                self.assertIn("unset the variable", item)
                self.assertIn("set the key to `false` or remove it", item)

    def test_the_item_is_conditional_and_names_no_hook_event(self):
        """Hooks do not run on every assistant, and the event has no one name (#26)."""
        self.assertGreaterEqual(len(self.events), 5, "the hosts' mappings name too few events")
        self.assertGreater(len({host.hooks["events"]["stop"] for host in self.hosts}), 1,
                           "every assistant now gives the event one name")
        for host in self.hosts:
            items = off_switch_items(self.ground_rules(host).read_text(encoding="utf-8"))
            with self.subTest(host=host.id):
                self.assertEqual(1, len(items))
                self.assertEqual([], events_named(items[0], self.events))
                self.assertIn("Where the hook that re-opens a turn", items[0])
                self.assertNotIn(HOOKS_PAGE, items[0])

    def test_the_values_are_the_ones_the_script_reads(self):
        """The four values in the item are the set `truthy()` holds in `stop-nudge.py`."""
        source = (SOURCE_DIR / "scripts" / "stop-nudge.py").read_text(encoding="utf-8")
        self.assertIn('in {"1", "true", "yes", "on"}', source)
        self.assertEqual({"`1`", "`true`", "`yes`", "`on`"}, set(OFF_SWITCH_VALUES))
        self.assertIn('os.environ.get("%s"' % OFF_SWITCH_VARIABLE, source)
        self.assertIn('pref_flag("%s")' % OFF_SWITCH_KEY.split(":")[0], source)

    def test_the_event_check_reports_an_event_name(self):
        """Negative control: an event name is found as a word, and the switch names are not one."""
        self.assertEqual(["Stop"], events_named("The plugin's `Stop` hook is a safety net", self.events))
        self.assertEqual(["agentStop"], events_named("the `agentStop` event", self.events))
        self.assertEqual([], events_named("`%s` and `%s` stop it" % (OFF_SWITCH_VARIABLE, OFF_SWITCH_KEY),
                                          self.events))

    def test_the_item_is_found_by_the_variable_it_names(self):
        """Negative control: the item is found by the variable, and one switch alone is seen as one."""
        text = "- one\n- **Off.** Set the\n  `%s` environment variable.\n- three\n" % OFF_SWITCH_VARIABLE
        self.assertEqual(["- **Off.** Set the `%s` environment variable." % OFF_SWITCH_VARIABLE],
                         off_switch_items(text))
        self.assertNotIn(OFF_SWITCH_KEY, off_switch_items(text)[0])
        self.assertEqual([], off_switch_items("- one\n- two\n"))


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
