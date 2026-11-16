"""Write one host's installable package from the host-neutral source.

A build is: copy every source file to where the host expects it (rendering the text
ones), then write the files only that host's package format has (manifest, MCP server
registration, hook configuration).
"""

from __future__ import annotations

import json
import re
import shutil
import stat
from dataclasses import dataclass, field
from pathlib import Path

from .model import HOSTS_DIR, BuildError, Host
from .render import RenderStats, render_text, substitute_tokens

#: Files rendered as text. Everything else (images, PDFs, vendored JavaScript) is copied
#: byte for byte.
TEXT_SUFFIXES = {".md", ".py", ".json", ".toml"}
MARKDOWN_SUFFIXES = {".md"}
#: Third-party files are never rendered, whatever their suffix.
VERBATIM_DIRS = {"vendor"}
IGNORED_NAMES = {"__pycache__", ".DS_Store"}

PACKAGE_DIR = "senzing-bootcamp"
AGENT_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_PLUGIN_MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
ADAPTER = HOSTS_DIR / "_shared" / "hook_adapter.py"
HOST_FILE = "bootcamp_host.json"
FALLBACK_DIR = "hooks/fallbacks"
HOST_RULES = "bootcamp-onboarding/host-rules.md"
FRONTMATTER_OPEN = "---\n"
#: Appended to a command rendered as a skill. A command names another skill's file by the skill's
#: name; as a skill it must say where that is, or an assistant searches the disk and can find
#: another copy of the bootcamp (seen on Copilot CLI 1.0.111, 2026-11-15).
SIBLING_SKILLS_NOTE = (
    "**Where the files this names are.** Every bootcamp skill is a directory beside this one, so "
    "the `bootcamp-onboarding` skill's files are in `../bootcamp-onboarding/`, counted from the "
    "directory of this `SKILL.md`, and the `graduation` skill's are in `../graduation/`. "
    "⛔ Read them from there. Never search the filesystem for a skill file: a second copy of the "
    "bootcamp on the same machine is normal, and it is not the one running.\n"
)


@dataclass(frozen=True)
class BuildContext:
    """What a package writer needs besides the declaration and the host."""

    source_dir: Path
    known_hosts: set[str]


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


def placed_files(host: Host, source_dir: Path) -> set[Path]:
    """The source files this host's package carries (relative to ``source_dir``)."""
    placed: set[Path] = set()
    for entry, destination in host.layout.items():
        if destination is not None:
            narrower = [other for other in host.layout if other != entry and other.startswith(entry + "/")]
            placed.update(
                path for path in _source_files(source_dir, entry)
                if not any(path.as_posix() == other or path.as_posix().startswith(other + "/") for other in narrower)
            )
    return placed


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
        # A more specific entry wins: "docs/notes.md" takes that file out of "docs".
        narrower = [other for other in host.layout if other != entry and other.startswith(entry + "/")]
        files = [
            path for path in _source_files(source_dir, entry)
            if not any(path.as_posix() == other or path.as_posix().startswith(other + "/") for other in narrower)
        ]
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


def _hook_command(host: Host, **values: str) -> str:
    template = host.hooks["command"]
    command = substitute_tokens(template, host, f"hosts/{host.id}/host.json: hooks.command")
    for name, value in values.items():
        command = command.replace("{" + name + "}", value)
    return command


def _matcher(host: Host, tools: list[str]) -> str | None:
    if not tools or not host.hooks.get("matchers", True):
        return None
    names: list[str] = []
    for tool in tools:
        for name in host.hooks["tools"][tool].split("|"):
            if name not in names:
                names.append(name)
    return "|".join(names)


def uses_adapter(host: Host) -> bool:
    """True when the host's hooks go through the adapter rather than straight to the scripts."""
    return "adapter" in host.options


def hook_entries(declaration: dict, host: Host) -> list[tuple[str, str | None, dict]]:
    """``(host event, matcher, declared hook)`` for every hook the host can run.

    A host that calls the scripts directly gets one entry per declared hook. A host that
    goes through the adapter gets one entry per event, since the adapter runs every script
    declared for it; that entry's tools are the union of the scripts' tools.
    """
    entries: list[tuple[str, str | None, dict]] = []
    if not uses_adapter(host):
        for hook in declaration["hooks"]:
            event = host.hooks["events"][hook["event"]]
            if event is not None:
                entries.append((event, _matcher(host, hook.get("tools", [])), hook))
        return entries
    seen: dict[str, dict] = {}
    for hook in declaration["hooks"]:
        if host.hooks["events"][hook["event"]] is None:
            continue
        merged = seen.setdefault(hook["event"], {"event": hook["event"], "tools": []})
        for tool in hook.get("tools", []):
            if tool not in merged["tools"]:
                merged["tools"].append(tool)
    for canonical, merged in seen.items():
        entries.append((host.hooks["events"][canonical], _matcher(host, merged["tools"]), merged))
    return entries


def _command_for(host: Host, hook: dict) -> str:
    if uses_adapter(host):
        return _hook_command(host, script="hook_adapter.py", event=hook["event"]) + (
            "" if "{event}" in host.hooks["command"] else f" {hook['event']}"
        )
    return _hook_command(host, script=hook["script"])


def claude_style_hooks(declaration: dict, host: Host) -> dict:
    """Hook configuration in the matcher-group shape Claude Code defined.

    Consecutive entries for the same event and the same tools share one group, which is how
    the hand-written configuration this replaces was laid out.
    """
    events: dict[str, list[dict]] = {}
    previous: tuple[str, str | None] | None = None
    for event, matcher, hook in hook_entries(declaration, host):
        entry = {"type": "command", "command": _command_for(host, hook)}
        entry.update(host.hooks.get("entry", {}))
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


def flat_hooks(declaration: dict, host: Host) -> dict:
    """Hook configuration as a flat list of handlers per event (``version: 1``)."""
    events: dict[str, list[dict]] = {}
    for event, _matcher_unused, hook in hook_entries(declaration, host):
        entry = {"type": "command", "command": _command_for(host, hook)}
        entry.update(host.hooks.get("entry", {}))
        events.setdefault(event, []).append(entry)
    return {"version": 1, "hooks": events}


def named_group_hooks(declaration: dict, host: Host, group_name: str) -> dict:
    """Hook configuration as one named group; tool events carry matcher groups, others do not."""
    group: dict = {"enabled": True}
    for event, matcher, hook in hook_entries(declaration, host):
        entry = {"type": "command", "command": _command_for(host, hook)}
        entry.update(host.hooks.get("entry", {}))
        if hook["event"] in ("pre_tool_use", "post_tool_use", "post_tool_use_failure"):
            group.setdefault(event, []).append({"matcher": matcher or ".*", "hooks": [entry]})
        else:
            group.setdefault(event, []).append(entry)
    return {group_name: group}


def unmapped_hooks(declaration: dict, host: Host) -> list[dict]:
    """Declared hooks this host has no event for; each needs an instruction-level fallback."""
    return [hook for hook in declaration["hooks"] if host.hooks["events"][hook["event"]] is None]


def _text(declaration: dict, key: str, host: Host) -> str:
    return substitute_tokens(declaration[key], host, f"source/bootcamp.json: {key}")


def _json(build: HostBuild, relative: str, value: object) -> None:
    _write(build, Path(relative), _dump_json(value).encode("utf-8"), 0o644)


def _scripts_dir(host: Host) -> str:
    destination = host.layout.get("scripts")
    if destination is None:
        raise BuildError(f"{host.id}: the layout drops scripts/, which every host needs")
    return destination


def _emit_host_file(build: HostBuild, declaration: dict) -> None:
    """``bootcamp_host.json``: which assistant this package is for.

    The feedback workflow reads it so every report names the assistant it came from, and the
    hook adapter reads it to translate that assistant's hook payloads.
    """
    host = build.host
    scripts = _scripts_dir(host)
    value: dict = {
        "host": host.id,
        "name": host.name,
        "product": host.vars.get("product", host.name),
        "package_noun": host.vars.get("package_noun", "plugin"),
        "bootcamp_version": declaration["version"],
        "scripts_dir": scripts,
    }
    if uses_adapter(host):
        hooks: dict[str, list[dict]] = {}
        for hook in declaration["hooks"]:
            if host.hooks["events"][hook["event"]] is None:
                continue
            entry = {"script": hook["script"]}
            if hook.get("tools"):
                entry["tools"] = hook["tools"]
            hooks.setdefault(hook["event"], []).append(entry)
        value.update(host.options["adapter"])
        value["hooks"] = hooks
        value["host_events"] = dict(host.hooks["events"])
        value["host_tools"] = dict(host.hooks["tools"])
        _write(build, Path(scripts) / ADAPTER.name, ADAPTER.read_bytes(), 0o644)
    _json(build, f"{scripts}/{HOST_FILE}", value)


def _commands_as_skills(build: HostBuild, context: BuildContext) -> None:
    """Each command becomes a skill of the same name, for hosts whose packages carry no commands.

    The body is the command's own text, so what the assistant is told to do is identical; only
    the way the bootcamper invokes it differs, and the host's profile says how.
    """
    host = build.host
    commands = context.source_dir / "commands"
    for path in sorted(commands.glob("*.md")):
        where = f"source/commands/{path.name}"
        text = render_text(
            path.read_bytes().decode("utf-8"), host, where,
            directives=True, known_hosts=context.known_hosts,
        )
        if not text.startswith(FRONTMATTER_OPEN):
            raise BuildError(f"{where}: a command must start with frontmatter")
        # A command sits in commands/, one level above skills/; as a skill it sits inside
        # skills/, so a link that reached a skill through ../skills/ now reaches it through ../
        text = text.replace("../skills/", "../")
        skill = FRONTMATTER_OPEN + f"name: {path.stem}\n" + text[len(FRONTMATTER_OPEN):]
        skill = skill.rstrip("\n") + "\n\n" + SIBLING_SKILLS_NOTE
        _write(build, Path("skills") / path.stem / "SKILL.md", skill.encode("utf-8"), 0o644)


def _add_skill_locations(build: HostBuild) -> None:
    """Tell every skill where its own directory is, on a host that does not.

    A host that hands the assistant a ``SKILL.md`` without its path leaves "this skill directory"
    meaning nothing, and the assistant searches the disk for the files beside it (seen on Kiro
    IDE 1.4.26, 2026-11-15: ``find /`` reached a backup of another copy of the bootcamp). The
    host's ``skill_location_note`` option states the installed location; ``{skill}`` in it is
    the skill's name.
    """
    note = build.host.options.get("skill_location_note")
    if not note:
        return
    for relative in sorted(name for name in build.files if re.fullmatch(r"skills/[^/]+/SKILL\.md", name)):
        target = build.root / relative
        skill = relative.split("/")[1]
        text = target.read_bytes().decode("utf-8").rstrip("\n")
        target.write_bytes((text + "\n\n" + note.replace("{skill}", skill) + "\n").encode("utf-8"))


def _copy_host_files(build: HostBuild, context: BuildContext) -> None:
    """Files only this host's package carries, from ``hosts/<id>/files/`` (same layout as the package)."""
    host = build.host
    root = host.directory / "files"
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or IGNORED_NAMES & set(relative.parts):
            continue
        data = path.read_bytes()
        if _is_text(relative):
            data = render_text(
                data.decode("utf-8"), host, f"hosts/{host.id}/files/{relative.as_posix()}",
                directives=relative.suffix in MARKDOWN_SUFFIXES, known_hosts=context.known_hosts,
            ).encode("utf-8")
        executable = path.stat().st_mode & stat.S_IXUSR
        _write(build, relative, data, 0o755 if executable else 0o644)


def fallback_scripts(declaration: dict, host: Host) -> list[str]:
    """Hook scripts whose rule this host must be given as an instruction, in declared order.

    A script needs no instruction only when the host is guaranteed to run it: the host has an
    event for it, the event can do what the script asks (it is not ``advisory``), and the
    host's hooks run without the bootcamper having to install or approve them.
    """
    guaranteed = host.hooks.get("guaranteed", False)
    advisory = set(host.hooks.get("advisory", ()))
    enforced: set[str] = set()
    declared: list[str] = []
    for hook in declaration["hooks"]:
        if hook["script"] not in declared:
            declared.append(hook["script"])
        mapped = host.hooks["events"][hook["event"]] is not None
        if guaranteed and mapped and hook["event"] not in advisory:
            enforced.add(hook["script"])
    return [script for script in declared if script not in enforced]


def host_rules(declaration: dict, host: Host, context: BuildContext) -> str:
    """The text of ``host-rules.md``: the safeguards this assistant carries out by instruction."""
    scripts = fallback_scripts(declaration, host)
    product = host.vars["product"]
    lines = [
        f"# Bootcamp safeguards on {product}",
        "",
        "<!-- Generated by the build from source/hooks/fallbacks/. Do not edit this file. -->",
        "",
    ]
    if not scripts:
        lines += [
            f"Every safeguard the bootcamp relies on runs by itself on {product}, as a hook.",
            "There is nothing to add to the ground rules here.",
            "",
        ]
        return "\n".join(lines)
    lines += [
        "The bootcamp protects the bootcamper's work with a set of safeguards: it resumes where",
        "they left off, keeps their files in their project, keeps their recap from being lost and",
        "ends each turn on one question. On some assistants every one of them runs by itself.",
        "",
        f"{host.hooks.get('note', f'On {product} some of them are not guaranteed to run by themselves.')}",
        "So carry out each safeguard below yourself, as an instruction, on every turn. Where a",
        "safeguard also ran by itself, doing it again is harmless.",
        "",
        "They apply only in a bootcamp project: a directory where `config/bootcamp_progress.json`",
        "exists. Outside one, none of this applies, and you never create that file to make it apply.",
        "",
        f"The commands below name the bootcamp's scripts as `{host.vars['scripts_dir']}`. Where",
        f"`{host.vars['plugin_root_var']}` is not set in your shell, they are at",
        f"`{host.vars['scripts_fallback']}`, counted from the directory of any skill's `SKILL.md`:",
        "resolve that to an absolute path once per session and use it.",
        "",
    ]
    for script in scripts:
        path = context.source_dir / FALLBACK_DIR / (Path(script).stem + ".md")
        where = f"source/{FALLBACK_DIR}/{path.name}"
        try:
            text = path.read_bytes().decode("utf-8")
        except FileNotFoundError as error:
            raise BuildError(f"{where} is missing: every hook needs its rule written as an instruction") from error
        lines.append(render_text(text, host, where, directives=True, known_hosts=context.known_hosts).rstrip("\n"))
        lines.append("")
    return "\n".join(lines)


def _emit_host_rules(build: HostBuild, declaration: dict, context: BuildContext) -> None:
    skills = build.host.layout.get("skills")
    if skills is None:
        raise BuildError(f"{build.host.id}: the layout drops skills/, which every host needs")
    text = host_rules(declaration, build.host, context)
    _write(build, Path(skills) / HOST_RULES, text.encode("utf-8"), 0o644)


def _manifest(declaration: dict, host: Host, **extra: object) -> dict:
    manifest: dict = dict(extra)
    manifest.update({
        "name": declaration["name"],
        "version": declaration["version"],
        "description": _text(declaration, "description", host),
        "author": declaration["author"],
        "homepage": declaration["homepage"],
        "repository": declaration["repository"],
        "license": declaration["license"],
    })
    return manifest


def _servers(declaration: dict, shape) -> dict:
    return {name: shape(server) for name, server in declaration["mcp_servers"].items()}


def _emit_claude_plugin(build: HostBuild, declaration: dict, context: BuildContext) -> None:
    host = build.host
    _json(build, ".claude-plugin/plugin.json", _manifest(declaration, host))
    servers = _servers(declaration, lambda server: {"type": "http", "url": server["url"]})
    _json(build, ".mcp.json", {"mcpServers": servers})
    _json(build, "hooks/hooks.json", claude_style_hooks(declaration, host))


def _emit_agent_plugin(build: HostBuild, declaration: dict, context: BuildContext) -> None:
    """The open Agent Plugins format, with the host's own directory for what it adds."""
    host = build.host
    manifest = _manifest(declaration, host, **{"$schema": AGENT_PLUGIN_SCHEMA})
    manifest["keywords"] = declaration["keywords"]
    _json(build, "plugin.json", manifest)
    servers = _servers(declaration, lambda server: {"type": "streamable-http", "url": server["url"]})
    _json(build, "mcp.json", {"$schema": AGENT_PLUGIN_MCP_SCHEMA, "mcpServers": servers})
    _commands_as_skills(build, context)
    hooks_file = host.options.get("hooks_file")
    if hooks_file:
        _json(build, hooks_file, flat_hooks(declaration, host))


def _emit_codex_plugin(build: HostBuild, declaration: dict, context: BuildContext) -> None:
    host = build.host
    manifest = _manifest(declaration, host)
    manifest["keywords"] = declaration["keywords"]
    manifest["skills"] = "./skills/"
    manifest["mcpServers"] = "./.mcp.json"
    manifest.update(host.options.get("manifest", {}))
    _json(build, ".codex-plugin/plugin.json", manifest)
    servers = _servers(declaration, lambda server: {"type": "http", "url": server["url"]})
    _json(build, ".mcp.json", {"mcpServers": servers})
    _commands_as_skills(build, context)
    _json(build, "hooks/hooks.json", claude_style_hooks(declaration, host))


def _emit_antigravity_plugin(build: HostBuild, declaration: dict, context: BuildContext) -> None:
    host = build.host
    manifest = _manifest(declaration, host, **{"$schema": "https://antigravity.google/schemas/v1/plugin.json"})
    manifest["keywords"] = declaration["keywords"]
    manifest.update(host.options.get("manifest", {}))
    _json(build, "plugin.json", manifest)
    servers = _servers(declaration, lambda server: {"url": server["url"]})
    _json(build, "mcp_config.json", {"mcpServers": servers})
    _commands_as_skills(build, context)
    _json(build, "hooks.json", named_group_hooks(declaration, host, declaration["name"]))


EMITTERS = {
    "claude-plugin": _emit_claude_plugin,
    "agent-plugin": _emit_agent_plugin,
    "codex-plugin": _emit_codex_plugin,
    "antigravity-plugin": _emit_antigravity_plugin,
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
    context = BuildContext(source_dir=source_dir, known_hosts=known_hosts)
    _copy_layout(build, source_dir, known_hosts)
    _copy_host_files(build, context)
    emitter(build, declaration, context)
    _add_skill_locations(build)
    if (source_dir / FALLBACK_DIR).is_dir():
        _emit_host_rules(build, declaration, context)
    _emit_host_file(build, declaration)
    build.files.sort()
    return build


def write_catalogs(declaration: dict, hosts: list[Host], out_dir: Path) -> list[str]:
    """The catalog files at the root of the published repository, one per host that has one.

    Each assistant looks for its own catalog, so every package installs from the one
    repository and no assistant is offered another assistant's package.
    """
    written: list[str] = []
    for host in hosts:
        if not host.catalog:
            continue
        source = f"./plugins/{host.id}/{PACKAGE_DIR}"
        description = _text(declaration, "description", host)
        style = host.catalog["style"]
        if style == "claude":
            catalog = {
                "name": host.catalog["name"],
                "owner": {"name": declaration["author"]["name"]},
                "description": f"Senzing Bootcamp for {host.vars['product']}.",
                "plugins": [{
                    "name": declaration["name"],
                    "source": source,
                    "description": description,
                    "keywords": declaration["keywords"],
                }],
            }
        elif style == "agent-plugin":
            catalog = {
                "name": host.catalog["name"],
                "owner": {"name": declaration["author"]["name"]},
                "metadata": {"description": f"Senzing Bootcamp for {host.vars['product']}."},
                "plugins": [{"name": declaration["name"], "description": description, "source": source}],
            }
        elif style == "codex":
            catalog = {
                "name": host.catalog["name"],
                "interface": {"displayName": declaration["author"]["name"]},
                "plugins": [{
                    "name": declaration["name"],
                    "source": {"source": "local", "path": source},
                    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                    "category": "Productivity",
                }],
            }
        else:
            raise BuildError(f"{host.id}: unknown catalog style {style!r}")
        path = out_dir / host.catalog["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_dump_json(catalog), encoding="utf-8")
        written.append(host.catalog["path"])
    return written
