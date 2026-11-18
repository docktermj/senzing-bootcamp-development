"""Load the host-neutral bootcamp declaration and the host profiles.

The bootcamp has one source tree (``source/``) and one profile per AI assistant
(``hosts/<id>/host.json``). Everything a host needs that is not the same for every
assistant is data in its profile, so adding an assistant never means editing the source.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "source"
HOSTS_DIR = REPO_ROOT / "hosts"
DECLARATION = "bootcamp.json"
CHECKS_FILE = "checks.json"
#: How far a recorded on-assistant check went, weakest first.
CHECK_SCOPES = ("first-turn", "install", "full")

HOST_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
VAR_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

#: Canonical hook events. A host maps each to its own event name, or to ``null`` when it
#: has no such event; a missing key is an error, so a new event forces a decision per host.
HOOK_EVENTS = (
    "session_start",
    "prompt_submit",
    "pre_tool_use",
    "post_tool_use",
    "post_tool_use_failure",
    "stop",
    "pre_compact",
    "session_end",
)

#: Canonical tool categories a hook can be limited to.
HOOK_TOOLS = ("write", "edit", "shell")


class BuildError(Exception):
    """A problem in the source, a host profile, or the build itself."""


@dataclass(frozen=True)
class Host:
    """One AI assistant the bootcamp is built for."""

    id: str
    name: str
    package_format: str
    vars: dict[str, str]
    layout: dict[str, str | None]
    hooks: dict
    catalog: dict | None
    foreign_terms: tuple[str, ...]
    directory: Path
    options: dict = field(default_factory=dict)
    site: dict = field(default_factory=dict)
    checks: tuple = ()

    def check_for(self, version: str, scope: str | None = None) -> dict | None:
        """The latest recorded on-assistant check of ``version`` (of ``scope``, when given)."""
        found = [
            check for check in self.checks
            if check["release"] == version and (scope is None or check["scope"] == scope)
        ]
        return max(found, key=lambda check: check["date"]) if found else None

    def fragment_path(self, name: str) -> Path:
        """Where this host's copy of a fragment is, or the shared copy when it has none of its own.

        The shared directory ``hosts/_shared/fragments/`` is optional and does not exist today, so
        every host supplies its own copy of each fragment. Were it added, a host with no copy of
        its own would get the shared one.
        """
        file_name = name if "." in name else f"{name}.md"
        own = self.directory / "fragments" / file_name
        shared = self.directory.parent / "_shared" / "fragments" / file_name
        return own if own.is_file() or not shared.is_file() else shared


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise BuildError(f"missing file: {path}") from error
    except json.JSONDecodeError as error:
        raise BuildError(f"{path}: invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise BuildError(f"{path}: expected a JSON object")
    return value


def load_declaration(source_dir: Path = SOURCE_DIR) -> dict:
    """Read ``source/bootcamp.json`` and check the parts every host relies on."""
    path = source_dir / DECLARATION
    declaration = _read_json(path)
    for key in ("name", "version", "description", "license", "mcp_servers", "hooks"):
        if key not in declaration:
            raise BuildError(f"{path}: missing required key {key!r}")
    for index, hook in enumerate(declaration["hooks"]):
        where = f"{path}: hooks[{index}]"
        if hook.get("event") not in HOOK_EVENTS:
            raise BuildError(f"{where}: unknown event {hook.get('event')!r}")
        script = hook.get("script")
        if not isinstance(script, str) or not (source_dir / "scripts" / script).is_file():
            raise BuildError(f"{where}: script {script!r} is not a file under source/scripts/")
        for tool in hook.get("tools", []):
            if tool not in HOOK_TOOLS:
                raise BuildError(f"{where}: unknown tool category {tool!r}")
    return declaration


def _load_checks(path: Path) -> tuple:
    """Recorded runs of the bootcamp on the real assistant, from ``hosts/<id>/checks.json``.

    A record is evidence, written by whoever ran the check: which version of the bootcamp, in
    which client, on what date, how far it went (``scope``) and what happened. ``scope`` is
    ``first-turn`` (the bootcamp started), ``install`` (installed from the public repository
    and started) or ``full`` (walked through to graduation).
    """
    if not path.is_file():
        return ()
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise BuildError(f"{path}: invalid JSON: {error}") from error
    if not isinstance(records, list):
        raise BuildError(f"{path}: expected a list of check records")
    for index, record in enumerate(records):
        for key in ("release", "client", "date", "scope", "result"):
            if not isinstance(record.get(key), str) or not record[key]:
                raise BuildError(f"{path}: record {index} needs a text value for {key!r}")
        if record["scope"] not in CHECK_SCOPES:
            raise BuildError(f"{path}: record {index} has scope {record['scope']!r}; use one of {CHECK_SCOPES}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", record["date"]):
            raise BuildError(f"{path}: record {index} date must be YYYY-MM-DD")
    return tuple(records)


def host_ids(hosts_dir: Path = HOSTS_DIR) -> list[str]:
    """Every host that has a profile, in a stable order."""
    if not hosts_dir.is_dir():
        return []
    return sorted(
        entry.name for entry in hosts_dir.iterdir() if (entry / "host.json").is_file()
    )


def load_host(host_id: str, hosts_dir: Path = HOSTS_DIR) -> Host:
    if not HOST_ID_RE.match(host_id):
        raise BuildError(f"invalid host id {host_id!r}")
    directory = hosts_dir / host_id
    path = directory / "host.json"
    data = _read_json(path)
    if data.get("id") != host_id:
        raise BuildError(f"{path}: id {data.get('id')!r} does not match its directory")
    for key in ("name", "package_format", "vars", "layout", "hooks"):
        if key not in data:
            raise BuildError(f"{path}: missing required key {key!r}")
    variables = data["vars"]
    for name, value in variables.items():
        if not VAR_NAME_RE.match(name):
            raise BuildError(f"{path}: invalid variable name {name!r}")
        if not isinstance(value, str):
            raise BuildError(f"{path}: variable {name!r} must be text")
    hooks = data["hooks"]
    for event in HOOK_EVENTS:
        if event not in hooks.get("events", {}):
            raise BuildError(
                f"{path}: hooks.events has no entry for {event!r}; "
                "name the host's event, or null where the host has none"
            )
    for tool in HOOK_TOOLS:
        if tool not in hooks.get("tools", {}):
            raise BuildError(f"{path}: hooks.tools has no entry for {tool!r}")
    return Host(
        id=host_id,
        name=data["name"],
        package_format=data["package_format"],
        vars=dict(variables),
        layout=dict(data["layout"]),
        hooks=hooks,
        catalog=data.get("catalog"),
        foreign_terms=tuple(data.get("foreign_terms", ())),
        directory=directory,
        options=dict(data.get("options", {})),
        site=dict(data.get("site", {})),
        checks=_load_checks(directory / CHECKS_FILE),
    )


def load_hosts(selected: list[str] | None = None, hosts_dir: Path = HOSTS_DIR) -> list[Host]:
    ids = selected or host_ids(hosts_dir)
    if not ids:
        raise BuildError(f"no host profiles found under {hosts_dir}")
    return [load_host(host_id, hosts_dir) for host_id in ids]
