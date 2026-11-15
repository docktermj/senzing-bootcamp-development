"""Render host-neutral source text for one host.

The source marks every place where assistants differ. There are three markers, and text
outside them is copied unchanged, which is what makes the bootcamp the same on every
assistant by construction:

``{{host.name}}``
    A value from the host profile's ``vars``. Every host must define every variable the
    source uses, so a new variable cannot be added for one assistant only.

``<!-- host:only a, b -->`` … ``<!-- host:end -->``  (also ``host:except``)
    Lines kept only for the listed hosts (or for every host but those). Markdown only.
    Each marker sits on a line of its own and the marker lines are never emitted.

``<!-- host:include name -->``
    Replaced by ``hosts/<id>/fragments/<name>.md``. Every host must supply the fragment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .model import BuildError, Host

TOKEN_RE = re.compile(r"\{\{host\.([a-z][a-z0-9_]*)\}\}")
#: Anything that looks like an attempt at a token but is not a well-formed one.
MALFORMED_TOKEN_RE = re.compile(r"\{\{\s*host\b[^}]*\}\}")
DIRECTIVE_RE = re.compile(
    r"^[ \t]*<!-- host:(only|except|end|include)(?: ([a-z0-9][a-z0-9, -]*?))? -->[ \t]*$"
)
#: A line that mentions a directive without being one (indented oddly, extra text, …).
DIRECTIVE_HINT_RE = re.compile(r"<!--\s*host:")


@dataclass
class RenderStats:
    """Every variation point met while rendering one file, for the parity report."""

    tokens: dict[str, int] = field(default_factory=dict)
    blocks: list[tuple[str, tuple[str, ...], int]] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)

    @property
    def variation_points(self) -> int:
        return sum(self.tokens.values()) + len(self.blocks) + len(self.includes)


def substitute_tokens(text: str, host: Host, where: str, stats: RenderStats | None = None) -> str:
    """Replace every ``{{host.name}}`` with the host's value."""

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in host.vars:
            raise BuildError(f"{where}: host {host.id!r} does not define variable {name!r}")
        if stats is not None:
            stats.tokens[name] = stats.tokens.get(name, 0) + 1
        return host.vars[name]

    rendered = TOKEN_RE.sub(replace, text)
    leftover = MALFORMED_TOKEN_RE.search(rendered)
    if leftover:
        raise BuildError(f"{where}: malformed host token {leftover.group(0)!r}")
    return rendered


def _parse_hosts(argument: str | None, where: str, known: set[str] | None) -> tuple[str, ...]:
    names = tuple(part.strip() for part in (argument or "").split(",") if part.strip())
    if not names:
        raise BuildError(f"{where}: a host block must name at least one host")
    if known is not None:
        for name in names:
            if name not in known:
                raise BuildError(f"{where}: unknown host {name!r} in a host block")
    return names


def render_text(
    text: str,
    host: Host,
    where: str,
    *,
    directives: bool,
    known_hosts: set[str] | None = None,
    stats: RenderStats | None = None,
) -> str:
    """Render one text file for ``host``.

    ``directives`` is true for Markdown, where host blocks and includes are honored; other
    text files get token substitution only, and a directive in one is an error rather than
    something silently left in the output.
    """
    stats = stats if stats is not None else RenderStats()
    output: list[str] = []
    block: tuple[str, int, bool] | None = None  # (kind, opening line number, keep?)

    for number, line in enumerate(text.splitlines(keepends=True), start=1):
        here = f"{where}:{number}"
        body = line.rstrip("\r\n")
        match = DIRECTIVE_RE.match(body)
        if match is None:
            if DIRECTIVE_HINT_RE.search(body):
                raise BuildError(
                    f"{here}: malformed host directive; it must be alone on its line, "
                    "written exactly as '<!-- host:only a, b -->'"
                )
            if block is None or block[2]:
                output.append(substitute_tokens(line, host, here, stats))
            continue
        if not directives:
            raise BuildError(f"{here}: host directives are supported in Markdown files only")
        kind, argument = match.group(1), match.group(2)
        if kind in ("only", "except"):
            if block is not None:
                raise BuildError(f"{here}: host blocks cannot nest (open since line {block[1]})")
            names = _parse_hosts(argument, here, known_hosts)
            listed = host.id in names
            block = (kind, number, listed if kind == "only" else not listed)
            stats.blocks.append((kind, names, number))
        elif kind == "end":
            if argument:
                raise BuildError(f"{here}: 'host:end' takes no argument")
            if block is None:
                raise BuildError(f"{here}: 'host:end' without an open host block")
            block = None
        else:  # include
            if not argument or "," in argument or " " in argument:
                raise BuildError(f"{here}: 'host:include' takes exactly one fragment name")
            stats.includes.append(argument)
            if block is not None and not block[2]:
                continue
            output.append(_fragment(argument, host, here, stats))

    if block is not None:
        raise BuildError(f"{where}:{block[1]}: host block is never closed")
    return "".join(output)


def _fragment(name: str, host: Host, where: str, stats: RenderStats) -> str:
    path = host.fragment_path(name)
    try:
        text = path.read_bytes().decode("utf-8")
    except FileNotFoundError as error:
        raise BuildError(
            f"{where}: host {host.id!r} has no fragment {name!r} (expected {path})"
        ) from error
    if DIRECTIVE_HINT_RE.search(text):
        raise BuildError(f"{path}: a fragment cannot contain host directives")
    if text and not text.endswith("\n"):
        raise BuildError(f"{path}: a fragment must end with a newline")
    return substitute_tokens(text, host, str(path), stats)
