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

from .emit import FRONTMATTER_RE, IGNORED_NAMES, MARKDOWN_SUFFIXES, HostBuild, _is_text, placed_files
from .model import Host
from .render import DIRECTIVE_RE

#: The skill frontmatter every assistant accepts: the open Agent Skills format, held to the
#: tightest limits any of the hosts documents.
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_NAME_MAX = 64
SKILL_DESCRIPTION_MAX = 1024
SKILL_FRONTMATTER_KEYS = {"name", "description"}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    term: str
    text: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.term!r}: {self.text.strip()[:140]}"


def _term_pattern(terms: tuple[str, ...] | list[str]) -> re.Pattern[str] | None:
    """One pattern for a host's foreign terms, matched whatever their letter case.

    A model ID, a directory and an environment variable spell an assistant's name in lower or
    upper case, and each is as much another host's text as the capitalized name is.
    """
    if not terms:
        return None
    return re.compile("|".join(f"(?:{term})" for term in terms), re.IGNORECASE)


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


def frontmatter(text: str) -> dict[str, str] | None:
    """The top-level ``key: value`` pairs of a Markdown file's frontmatter, unquoted."""
    match = FRONTMATTER_RE.match(text)
    if match is None:
        return None
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line[0] in " \t#":
            continue
        key, separator, value = line.partition(":")
        if not separator:
            return None
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            quote = value[0]
            value = value[1:-1]
            value = value.replace("''", "'") if quote == "'" else value.replace('\\"', '"')
        values[key.strip()] = value
    return values


def skill_problems(build: HostBuild) -> list[str]:
    """Skills in a built package that some assistant would reject or misread."""
    problems: list[str] = []
    skills = build.root / "skills"
    for skill in sorted(path for path in skills.iterdir() if path.is_dir()) if skills.is_dir() else []:
        relative = f"skills/{skill.name}/SKILL.md"
        path = skill / "SKILL.md"
        if not path.is_file():
            problems.append(f"{relative}: missing")
            continue
        values = frontmatter(path.read_bytes().decode("utf-8"))
        if values is None:
            problems.append(f"{relative}: no readable frontmatter")
            continue
        name, description = values.get("name", ""), values.get("description", "")
        if name != skill.name:
            problems.append(f"{relative}: name {name!r} does not match its directory")
        if not SKILL_NAME_RE.match(name) or len(name) > SKILL_NAME_MAX:
            problems.append(f"{relative}: name must be lowercase-hyphen, at most {SKILL_NAME_MAX} characters")
        if not 1 <= len(description) <= SKILL_DESCRIPTION_MAX:
            problems.append(
                f"{relative}: description is {len(description)} characters; "
                f"every host accepts 1 to {SKILL_DESCRIPTION_MAX}"
            )
        extra = sorted(set(values) - SKILL_FRONTMATTER_KEYS)
        if extra:
            problems.append(f"{relative}: frontmatter keys not every host reads: {', '.join(extra)}")
    return problems


def lint_source(source_dir: Path, hosts: list[Host]) -> list[Finding]:
    """Host-specific terms in the source that are not inside a block for that host.

    Each host profile lists the terms that identify *other* hosts (``foreign_terms``). A
    term is host-specific when any host calls it foreign; it is allowed in the source only
    on lines kept solely for hosts that do not: inside a host block, or in a file that only
    those hosts' packages carry.
    """
    patterns = {host.id: _term_pattern(host.foreign_terms) for host in hosts}
    placed = {host.id: placed_files(host, source_dir) for host in hosts}
    findings: list[Finding] = []
    for path in sorted(source_dir.rglob("*")):
        relative = path.relative_to(source_dir)
        if not path.is_file() or IGNORED_NAMES & set(relative.parts) or not _is_text(relative):
            continue
        text = path.read_bytes().decode("utf-8")
        # A file only some hosts carry may speak about those hosts freely.
        all_ids = {host_id for host_id, files in placed.items() if relative in files}
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
