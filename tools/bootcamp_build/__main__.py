"""Command line for the bootcamp build.

    python3 -m tools.bootcamp_build build [--host ID ...] [--out DIR]
    python3 -m tools.bootcamp_build check [--host ID ...]
    python3 -m tools.bootcamp_build compare --host ID --against DIR
    python3 -m tools.bootcamp_build promote --to PUBLIC_CLONE [--apply]

Run from the repository root. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from .emit import HostBuild, build_host, unmapped_hooks, write_catalogs
from .model import REPO_ROOT, SOURCE_DIR, BuildError, host_ids, load_declaration, load_hosts
from .promote import promote
from .site import build_public, build_site
from .validate import compare_trees, lint_source, residue, skill_problems

DEFAULT_OUT = REPO_ROOT / "dist"
SITE_DIR = REPO_ROOT / "site"
PUBLIC_DIR = REPO_ROOT / "public"
NEUTRALITY = Path(__file__).resolve().parent / "neutrality.json"


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
    for catalog in write_catalogs(declaration, [build.host for build in builds], out_dir):
        print(f"catalog: {out_dir / catalog}")
    if not arguments.host and SITE_DIR.is_dir():
        pages = build_site(SITE_DIR, [build.host for build in builds], declaration, out_dir / "site")
        print(f"site: {len(pages)} files -> {out_dir / 'site'}")
    if not arguments.host and PUBLIC_DIR.is_dir():
        files = build_public(PUBLIC_DIR, [build.host for build in builds], out_dir / "public")
        print(f"public root: {len(files)} files -> {out_dir / 'public'}")
    return 0


def _allowed(baseline: dict, *keys: str) -> int:
    value: object = baseline
    for key in keys:
        value = value.get(key, 0) if isinstance(value, dict) else 0
    return value if isinstance(value, int) else 0


def _ratchet(label: str, found: int, allowed: int, strict: bool) -> int:
    """How many problems this count adds: none while it stays at or under its recorded ceiling.

    The source was imported from a Claude-only plugin, so it began with text that names an
    assistant. The ceiling records how much is left. It can only come down: a count above it
    fails, and a count below it fails too, until the ceiling is lowered to match.
    """
    if strict:
        return found
    if found > allowed:
        print(f"  {label}: {found} is above the recorded ceiling of {allowed}; a change added "
              "text that names an assistant")
        return found - allowed
    if found < allowed:
        print(f"  {label}: {found} is below the recorded ceiling of {allowed}; lower the ceiling "
              f"to {found} in tools/bootcamp_build/neutrality.json so it cannot creep back")
        return 1
    return 0


def _command_check(arguments: argparse.Namespace) -> int:
    """Build every host twice into scratch directories and run every check."""
    failures = 0
    baseline = json.loads(NEUTRALITY.read_text(encoding="utf-8")) if NEUTRALITY.is_file() else {}
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        declaration, builds = _build_all(arguments.host, Path(first))
        _, again = _build_all(arguments.host, Path(second))
        source_findings = lint_source(SOURCE_DIR, [build.host for build in builds])
        print(f"source: {len(source_findings)} host-specific terms outside a host block")
        for finding in source_findings[: arguments.show]:
            print(f"  {finding}")
        failures += _ratchet("source", len(source_findings), _allowed(baseline, "source"), arguments.strict)
        for build, rebuilt in zip(builds, again):
            print(_summary(declaration, build))
            drift = compare_trees(build.root, rebuilt.root)
            if drift:
                failures += len(drift)
                print(f"  NOT DETERMINISTIC: {len(drift)} differences between two builds")
                for problem in drift[: arguments.show]:
                    print(f"    {problem}")
            skills = skill_problems(build)
            print(f"  {len(skills)} skill frontmatter problems")
            for problem in skills[: arguments.show]:
                print(f"    {problem}")
            failures += len(skills)
            findings = residue(build)
            print(f"  {len(findings)} references to other hosts")
            for finding in findings[: arguments.show]:
                print(f"    {finding}")
            failures += _ratchet(
                build.host.id, len(findings), _allowed(baseline, "hosts", build.host.id), arguments.strict)
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


def _command_promote(arguments: argparse.Namespace) -> int:
    """Build every host fresh, then plan or apply the change to the public working tree."""
    public = Path(arguments.to).expanduser().resolve()
    with tempfile.TemporaryDirectory() as scratch:
        declaration, builds = _build_all(None, Path(scratch))
        catalogs = write_catalogs(declaration, [build.host for build in builds], Path(scratch))
        site = Path(scratch) / "site"
        if SITE_DIR.is_dir():
            build_site(SITE_DIR, [build.host for build in builds], declaration, site)
        root_files = Path(scratch) / "public"
        build_public(PUBLIC_DIR, [build.host for build in builds], root_files)
        version = declaration["version"]
        allowed = set(host_ids()) if arguments.allow_preview == ["all"] else set(arguments.allow_preview)
        refused = [
            build.host.id for build in builds
            if build.host.id not in allowed and not any(
                check and check["result"] == "pass"
                for check in (build.host.check_for(version, "install"), build.host.check_for(version, "full"))
            )
        ]
        writing = arguments.apply and not refused
        plan = promote(Path(scratch), catalogs, site, public, apply=writing, root_files=root_files)
    version = declaration["version"]
    unchecked = []
    print(f"On-assistant checks recorded for version {version}:")
    for build in builds:
        host = build.host
        best = next((host.check_for(version, scope) for scope in ("full", "install", "first-turn")
                     if host.check_for(version, scope)), None)
        if best is None:
            print(f"  {host.id:<8} none")
        else:
            print(f"  {host.id:<8} {best['scope']}: {best['result']} in {best['client']} on {best['date']}")
        installed = any(
            check["result"] == "pass" for scope in ("install", "full")
            for check in [host.check_for(version, scope)] if check
        )
        if not installed:
            unchecked.append(host.id)
    allowed = set(host_ids()) if arguments.allow_preview == ["all"] else set(arguments.allow_preview)
    blocked = [host_id for host_id in unchecked if host_id not in allowed]
    if arguments.apply and blocked:
        raise BuildError(
            f"version {version} has not been installed and started on: {', '.join(blocked)}. "
            "Record the check in hosts/<assistant>/checks.json, or promote it as a preview with "
            f"--allow-preview {','.join(blocked)}"
        )
    for label, names in (("add", plan.added), ("change", plan.changed), ("remove", plan.removed)):
        for name in names[: arguments.show]:
            print(f"  {label:<6} {name}")
        if len(names) > arguments.show:
            print(f"  {label:<6} ... and {len(names) - arguments.show} more")
    if plan.empty:
        print(f"{public} already holds version {version}; nothing to promote")
    elif arguments.apply:
        print(f"promoted version {version} into {public}: {plan.summary()}")
        print("Nothing was committed or pushed. Review the diff there, then publish it.")
    else:
        print(f"would promote version {version} into {public}: {plan.summary()}")
        print("Nothing was written. Run again with --apply to write the working tree.")
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
    check.add_argument("--strict", action="store_true",
                       help="fail on any text that names an assistant, ignoring the recorded ceilings")
    check.set_defaults(run=_command_check)

    compare = commands.add_parser("compare", help="compare one host's build with a directory")
    compare.add_argument("--host", required=True)
    compare.add_argument("--against", required=True, help="directory holding the expected package")
    compare.set_defaults(run=_command_compare)

    promotion = commands.add_parser(
        "promote", help="write the build into a clone of the public repository (no commit)")
    promotion.add_argument("--to", required=True, help="path to a clone of Senzing/bootcamp")
    promotion.add_argument("--apply", action="store_true", help="write the working tree (default: only plan)")
    promotion.add_argument("--show", type=int, default=15, help="paths to print per kind of change")
    promotion.add_argument(
        "--allow-preview", default=[], type=lambda value: [part for part in value.split(",") if part],
        metavar="HOSTS", help="promote these assistants (comma-separated, or 'all') although this "
        "version has no recorded install check on them; their pages say so")
    promotion.set_defaults(run=_command_promote)

    arguments = parser.parse_args(argv)
    try:
        return arguments.run(arguments)
    except BuildError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
