"""Promote a tested build into the public repository's working tree.

The public repository holds only what a bootcamper installs and reads: every assistant's
package, each assistant's catalog, and the pages published at hub.senzing.com/bootcamp/.
Promotion writes exactly those paths and nothing else, and it stops at the working tree: no
commit, no branch, no push. The maintainer reviews the diff and publishes it, so the diff is
the last gate before a bootcamper sees a change.

Managed paths in the public repository:

- ``plugins/``              every host's package (mirrored: stale files are removed)
- each host's catalog file  for example ``.claude-plugin/marketplace.json``
- ``docs/``                 from ``site/`` (mirrored, except the paths ``site/promote.json``
                            lists under ``preserve``, which live only in the public repository)
- each file under ``public/`` at the same path from the root, such as ``README.md``
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .model import BuildError

PUBLIC_REMOTE_RE = re.compile(r"[:/]senzing/bootcamp(?:\.git)?/?$", re.IGNORECASE)
SITE_CONFIG = "promote.json"


@dataclass
class Plan:
    """What a promotion would change in the public working tree."""

    added: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)

    @property
    def empty(self) -> bool:
        return not (self.added or self.changed or self.removed)

    def summary(self) -> str:
        return f"{len(self.added)} added, {len(self.changed)} changed, {len(self.removed)} removed"


def check_public_clone(public: Path) -> None:
    """Refuse any directory that is not a clone of the public repository."""
    if not (public / ".git").exists():
        raise BuildError(f"{public} is not a git working tree")
    done = subprocess.run(
        ["git", "-C", str(public), "remote", "get-url", "origin"],
        capture_output=True, text=True, check=False,
    )
    url = done.stdout.strip()
    if done.returncode != 0 or not PUBLIC_REMOTE_RE.search(url):
        raise BuildError(
            f"{public}: origin is {url or 'not set'!r}, not Senzing/bootcamp; "
            "promotion writes only into a clone of the public repository"
        )


def _files(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}
    return {path.relative_to(root).as_posix(): path for path in sorted(root.rglob("*")) if path.is_file()}


def _preserved(site_dir: Path) -> tuple[str, ...]:
    config = site_dir / SITE_CONFIG
    if not config.is_file():
        return ()
    try:
        value = json.loads(config.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise BuildError(f"{config}: invalid JSON: {error}") from error
    return tuple(value.get("preserve", ()))


def _mirror(source: Path, target_root: Path, target: str, plan: Plan, apply: bool,
            preserve: tuple[str, ...] = (), skip: tuple[str, ...] = ()) -> None:
    """Make ``target_root/target`` hold exactly the files under ``source``."""
    wanted = {name: path for name, path in _files(source).items() if name not in skip}
    present = _files(target_root / target)
    for name, path in wanted.items():
        relative = f"{target}/{name}"
        destination = target_root / relative
        if name not in present:
            plan.added.append(relative)
        elif present[name].read_bytes() != path.read_bytes():
            plan.changed.append(relative)
        else:
            continue
        if apply:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    for name, path in present.items():
        if name in wanted or any(name == kept or name.startswith(kept) for kept in preserve):
            continue
        plan.removed.append(f"{target}/{name}")
        if apply:
            path.unlink()
    if apply:
        _prune_empty(target_root / target)


def _prune_empty(root: Path) -> None:
    if not root.is_dir():
        return
    for directory in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()


def _single(source: Path, target_root: Path, relative: str, plan: Plan, apply: bool) -> None:
    destination = target_root / relative
    if not destination.exists():
        plan.added.append(relative)
    elif destination.read_bytes() != source.read_bytes():
        plan.changed.append(relative)
    else:
        return
    if apply:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def promote(dist: Path, catalogs: list[str], site_dir: Path, public: Path, *, apply: bool,
            root_files: Path | None = None) -> Plan:
    """Plan (and with ``apply``, perform) a promotion of ``dist`` and ``site_dir`` into ``public``.

    ``root_files`` is a directory whose files are written to the same paths at the root of the
    public repository. Only those files are managed there; nothing else at the root is touched.
    """
    check_public_clone(public)
    plan = Plan()
    if root_files is not None:
        for name, path in _files(root_files).items():
            _single(path, public, name, plan, apply)
    _mirror(dist / "plugins", public, "plugins", plan, apply)
    for catalog in catalogs:
        _single(dist / catalog, public, catalog, plan, apply)
    if site_dir.is_dir():
        _mirror(site_dir, public, "docs", plan, apply,
                preserve=_preserved(site_dir), skip=(SITE_CONFIG,))
    for names in (plan.added, plan.changed, plan.removed):
        names.sort()
    return plan
