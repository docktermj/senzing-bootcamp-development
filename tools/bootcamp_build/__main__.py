"""Command line for the bootcamp build.

    python3 -m tools.bootcamp_build build [--host ID ...] [--out DIR]
    python3 -m tools.bootcamp_build check [--host ID ...]
    python3 -m tools.bootcamp_build compare --host ID --against DIR

Run from the repository root. Standard library only.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from .emit import HostBuild, build_host, unmapped_hooks
from .model import REPO_ROOT, SOURCE_DIR, BuildError, host_ids, load_declaration, load_hosts
from .validate import compare_trees, lint_source, residue

DEFAULT_OUT = REPO_ROOT / "dist"


def _build_all(selected: list[str] | None, out_dir: Path) -> tuple[dict, list[HostBuild]]:
    declaration = load_declaration(SOURCE_DIR)
    known = set(host_ids())
    builds = [
        build_host(declaration, host, SOURCE_DIR, out_dir, known) for host in load_hosts(selected)
    ]
    return declaration, builds


def _summary(declaration: dict, build: HostBuild) -> str:
    points = sum(stats.variation_points for stats in build.stats.values())
    skipped = unmapped_hooks(declaration, build.host)
    line = (
        f"{build.host.id}: {len(build.files)} files, "
        f"{points} variation points in {len(build.stats)} files"
    )
    if skipped:
        events = sorted({hook["event"] for hook in skipped})
        line += f", no host event for: {', '.join(events)}"
    return line


def _command_build(arguments: argparse.Namespace) -> int:
    out_dir = Path(arguments.out).resolve()
    declaration, builds = _build_all(arguments.host, out_dir)
    for build in builds:
        print(_summary(declaration, build))
        print(f"  -> {build.root}")
    return 0


def _command_check(arguments: argparse.Namespace) -> int:
    """Build every host twice into scratch directories and run every check."""
    failures = 0
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        declaration, builds = _build_all(arguments.host, Path(first))
        _, again = _build_all(arguments.host, Path(second))
        source_findings = lint_source(SOURCE_DIR, [build.host for build in builds])
        print(f"source: {len(source_findings)} host-specific terms outside a host block")
        for finding in source_findings[: arguments.show]:
            print(f"  {finding}")
        failures += len(source_findings)
        for build, rebuilt in zip(builds, again):
            print(_summary(declaration, build))
            drift = compare_trees(build.root, rebuilt.root)
            if drift:
                failures += len(drift)
                print(f"  NOT DETERMINISTIC: {len(drift)} differences between two builds")
                for problem in drift[: arguments.show]:
                    print(f"    {problem}")
            findings = residue(build)
            print(f"  {len(findings)} references to other hosts")
            for finding in findings[: arguments.show]:
                print(f"    {finding}")
            failures += len(findings)
    print("OK" if not failures else f"FAILED: {failures} problems")
    return 0 if not failures else 1


def _command_compare(arguments: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory() as scratch:
        _, builds = _build_all([arguments.host], Path(scratch))
        problems = compare_trees(Path(arguments.against).resolve(), builds[0].root)
    for problem in problems:
        print(problem)
    if problems:
        print(f"FAILED: {len(problems)} differences")
        return 1
    print(f"identical: {len(builds[0].files)} files")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bootcamp_build", description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="write each host's package under --out")
    build.add_argument("--host", action="append", help="build only this host (repeatable)")
    build.add_argument("--out", default=str(DEFAULT_OUT), help="output directory (default: dist)")
    build.set_defaults(run=_command_build)

    check = commands.add_parser("check", help="build to a scratch directory and run every check")
    check.add_argument("--host", action="append", help="check only this host (repeatable)")
    check.add_argument("--show", type=int, default=10, help="findings to print per check")
    check.set_defaults(run=_command_check)

    compare = commands.add_parser("compare", help="compare one host's build with a directory")
    compare.add_argument("--host", required=True)
    compare.add_argument("--against", required=True, help="directory holding the expected package")
    compare.set_defaults(run=_command_compare)

    arguments = parser.parse_args(argv)
    try:
        return arguments.run(arguments)
    except BuildError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
