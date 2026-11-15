"""Checks that keep the bootcamp the same on every assistant.

Three questions, each answered mechanically:

- **Is the source host-neutral?** A host's name in the source, outside a host block for
  that host, is text every assistant would be shown.
- **Is each built package free of other hosts?** The same question asked of the output,
  which also covers what a host's own profile and fragments contribute.
- **Did two trees come out the same?** Used to prove an import or a rebuild changed
  nothing.
"""

from __future__ import annotations

import hashlib
import re
import stat
from dataclasses import dataclass
from pathlib import Path

from .emit import IGNORED_NAMES, MARKDOWN_SUFFIXES, HostBuild, _is_text
from .model import Host
from .render import DIRECTIVE_RE


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    term: str
    text: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.term!r}: {self.text.strip()[:140]}"


def _term_pattern(terms: tuple[str, ...] | list[str]) -> re.Pattern[str] | None:
    if not terms:
        return None
    return re.compile("|".join(f"(?:{term})" for term in terms))


def residue(build: HostBuild) -> list[Finding]:
    """Text in a built package that names a different host."""
    pattern = _term_pattern(build.host.foreign_terms)
    if pattern is None:
        return []
    findings: list[Finding] = []
    for relative in build.files:
        path = Path(relative)
        if not _is_text(path):
            continue
        text = (build.root / path).read_bytes().decode("utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            for match in pattern.finditer(line):
                findings.append(Finding(relative, number, match.group(0), line))
    return findings


def lint_source(source_dir: Path, hosts: list[Host]) -> list[Finding]:
    """Host-specific terms in the source that are not inside a block for that host.

    Each host profile lists the terms that identify *other* hosts (``foreign_terms``). A
    term is host-specific when any host calls it foreign; it is allowed in the source only
    on lines kept solely for hosts that do not.
    """
    patterns = {host.id: _term_pattern(host.foreign_terms) for host in hosts}
    all_ids = {host.id for host in hosts}
    findings: list[Finding] = []
    for path in sorted(source_dir.rglob("*")):
        relative = path.relative_to(source_dir)
        if not path.is_file() or IGNORED_NAMES & set(relative.parts) or not _is_text(relative):
            continue
        text = path.read_bytes().decode("utf-8")
        kept_for = all_ids
        for number, line in enumerate(text.splitlines(), start=1):
            if relative.suffix in MARKDOWN_SUFFIXES:
                match = DIRECTIVE_RE.match(line)
                if match:
                    kind, argument = match.group(1), match.group(2) or ""
                    names = {part.strip() for part in argument.split(",") if part.strip()}
                    if kind == "only":
                        kept_for = names & all_ids
                    elif kind == "except":
                        kept_for = all_ids - names
                    elif kind == "end":
                        kept_for = all_ids
                    continue
            terms: set[str] = set()
            for host_id in sorted(kept_for):
                pattern = patterns[host_id]
                if pattern is not None:
                    terms.update(found.group(0) for found in pattern.finditer(line))
            for term in sorted(terms):
                findings.append(Finding(f"source/{relative.as_posix()}", number, term, line))
    return findings


def tree_digest(root: Path) -> dict[str, tuple[str, bool]]:
    """SHA-256 and executable bit of every file under ``root``."""
    digest: dict[str, tuple[str, bool]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or IGNORED_NAMES & set(path.relative_to(root).parts):
            continue
        executable = bool(path.stat().st_mode & stat.S_IXUSR)
        digest[path.relative_to(root).as_posix()] = (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            executable,
        )
    return digest


def compare_trees(expected: Path, actual: Path) -> list[str]:
    """Differences between two trees, as readable lines. Empty means identical."""
    want, have = tree_digest(expected), tree_digest(actual)
    problems = [f"missing from build: {name}" for name in sorted(set(want) - set(have))]
    problems += [f"extra in build: {name}" for name in sorted(set(have) - set(want))]
    for name in sorted(set(want) & set(have)):
        if want[name][0] != have[name][0]:
            problems.append(f"content differs: {name}")
        elif want[name][1] != have[name][1]:
            problems.append(f"executable bit differs: {name}")
    return problems
