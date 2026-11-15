"""Write one host's installable package from the host-neutral source.

A build is: copy every source file to where the host expects it (rendering the text
ones), then write the files only that host's package format has (manifest, MCP server
registration, hook configuration).
"""

from __future__ import annotations

import json
import shutil
import stat
from dataclasses import dataclass, field
from pathlib import Path

from .model import BuildError, Host
from .render import RenderStats, render_text, substitute_tokens

#: Files rendered as text. Everything else (images, PDFs, vendored JavaScript) is copied
#: byte for byte.
TEXT_SUFFIXES = {".md", ".py", ".json", ".toml"}
MARKDOWN_SUFFIXES = {".md"}
#: Third-party files are never rendered, whatever their suffix.
VERBATIM_DIRS = {"vendor"}
IGNORED_NAMES = {"__pycache__", ".DS_Store"}

PACKAGE_DIR = "senzing-bootcamp"


@dataclass
class HostBuild:
    """What a build of one host produced."""

    host: Host
    root: Path
    files: list[str] = field(default_factory=list)
    stats: dict[str, RenderStats] = field(default_factory=dict)


def _dump_json(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def _is_text(relative: Path) -> bool:
    return relative.suffix in TEXT_SUFFIXES and not (VERBATIM_DIRS & set(relative.parts))


def _source_files(source_dir: Path, entry: str) -> list[Path]:
    """Files under one layout entry, relative to ``source_dir``, in a stable order."""
    start = source_dir / entry
    if start.is_file():
        return [Path(entry)]
    if not start.is_dir():
        raise BuildError(f"layout entry {entry!r} does not exist under {source_dir}")
    return sorted(
        path.relative_to(source_dir)
        for path in start.rglob("*")
        if path.is_file() and not (IGNORED_NAMES & set(path.parts))
    )


def _write(build: HostBuild, relative: Path, data: bytes, mode: int | None = None) -> None:
    target = build.root / relative
    if target.exists():
        raise BuildError(f"{build.host.id}: two build steps both write {relative}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    if mode is not None:
        target.chmod(mode)
    build.files.append(relative.as_posix())


def _copy_layout(build: HostBuild, source_dir: Path, known_hosts: set[str]) -> None:
    host = build.host
    covered: set[Path] = set()
    for entry, destination in host.layout.items():
        files = _source_files(source_dir, entry)
        covered.update(files)
        if destination is None:
            continue
        for relative in files:
            suffix = relative.relative_to(entry) if (source_dir / entry).is_dir() else None
            target = Path(destination) / suffix if suffix is not None else Path(destination)
            source = source_dir / relative
            data = source.read_bytes()
            if _is_text(relative):
                stats = RenderStats()
                rendered = render_text(
                    data.decode("utf-8"),
                    host,
                    f"source/{relative.as_posix()}",
                    directives=relative.suffix in MARKDOWN_SUFFIXES,
                    known_hosts=known_hosts,
                    stats=stats,
                )
                data = rendered.encode("utf-8")
                if stats.variation_points:
                    build.stats[relative.as_posix()] = stats
            executable = source.stat().st_mode & stat.S_IXUSR
            _write(build, target, data, 0o755 if executable else 0o644)

    # Every source file must be placed or dropped on purpose by every host, so a new file
    # can never reach some assistants and silently miss others.
    declaration = Path("bootcamp.json")
    for path in sorted(source_dir.rglob("*")):
        relative = path.relative_to(source_dir)
        if not path.is_file() or IGNORED_NAMES & set(relative.parts) or relative == declaration:
            continue
        if relative not in covered:
            raise BuildError(
                f"{host.id}: source/{relative.as_posix()} is not covered by the host's layout; "
                "map it to a destination, or to null to drop it on purpose"
            )


def _hook_command(host: Host, script: str) -> str:
    template = host.hooks["command"]
    command = substitute_tokens(template, host, f"hosts/{host.id}/host.json: hooks.command")
    return command.replace("{script}", script)


def _matcher(host: Host, tools: list[str]) -> str | None:
    if not tools:
        return None
    return "|".join(host.hooks["tools"][tool] for tool in tools)


def claude_style_hooks(declaration: dict, host: Host) -> dict:
    """Hook configuration in the matcher-group shape Claude Code defined.

    Consecutive declarations for the same event and the same tools share one group, which
    is how the hand-written configuration this replaces was laid out.
    """
    events: dict[str, list[dict]] = {}
    previous: tuple[str, str | None] | None = None
    for hook in declaration["hooks"]:
        event = host.hooks["events"][hook["event"]]
        if event is None:
            continue
        matcher = _matcher(host, hook.get("tools", []))
        entry = {"type": "command", "command": _hook_command(host, hook["script"])}
        groups = events.setdefault(event, [])
        if previous == (event, matcher) and groups:
            groups[-1]["hooks"].append(entry)
        else:
            group: dict = {}
            if matcher is not None:
                group["matcher"] = matcher
            group["hooks"] = [entry]
            groups.append(group)
        previous = (event, matcher)
    return {"hooks": events}


def unmapped_hooks(declaration: dict, host: Host) -> list[dict]:
    """Declared hooks this host has no event for; each needs an instruction-level fallback."""
    return [hook for hook in declaration["hooks"] if host.hooks["events"][hook["event"]] is None]


def _text(declaration: dict, key: str, host: Host) -> str:
    return substitute_tokens(declaration[key], host, f"source/bootcamp.json: {key}")


def _emit_claude_plugin(build: HostBuild, declaration: dict) -> None:
    host = build.host
    manifest = {
        "name": declaration["name"],
        "version": declaration["version"],
        "description": _text(declaration, "description", host),
        "author": declaration["author"],
        "homepage": declaration["homepage"],
        "repository": declaration["repository"],
        "license": declaration["license"],
    }
    _write(build, Path(".claude-plugin/plugin.json"), _dump_json(manifest).encode("utf-8"), 0o644)
    servers = {
        name: {"type": "http", "url": server["url"]}
        for name, server in declaration["mcp_servers"].items()
    }
    _write(build, Path(".mcp.json"), _dump_json({"mcpServers": servers}).encode("utf-8"), 0o644)
    hooks = claude_style_hooks(declaration, host)
    _write(build, Path("hooks/hooks.json"), _dump_json(hooks).encode("utf-8"), 0o644)


EMITTERS = {
    "claude-plugin": _emit_claude_plugin,
}


def build_host(
    declaration: dict,
    host: Host,
    source_dir: Path,
    out_dir: Path,
    known_hosts: set[str],
) -> HostBuild:
    """Build ``host``'s package under ``out_dir/plugins/<host>/senzing-bootcamp``."""
    emitter = EMITTERS.get(host.package_format)
    if emitter is None:
        raise BuildError(f"{host.id}: unknown package format {host.package_format!r}")
    root = out_dir / "plugins" / host.id / PACKAGE_DIR
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    build = HostBuild(host=host, root=root)
    _copy_layout(build, source_dir, known_hosts)
    emitter(build, declaration)
    build.files.sort()
    return build
