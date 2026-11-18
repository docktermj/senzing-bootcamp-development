#!/usr/bin/env python3
"""Install, show or remove the bootcamp's hooks in a Kiro workspace.

    <python> install_hooks.py plan    --workspace <project>
    <python> install_hooks.py install --workspace <project> --yes
    <python> install_hooks.py remove  --workspace <project>

Kiro does not load hooks from a Power, so the bootcamp's hooks are installed into the
bootcamper's own workspace, under ``.kiro/hooks/``, and only with their consent. ``plan``
writes nothing and prints every file ``install`` would write and the exact command each hook
would run. ``install`` refuses to run without ``--yes``. ``remove`` deletes only files this
script wrote.

Every hook command names the Python interpreter that ran this script and the hook adapter by
absolute path, quoted, so a hook never depends on ``PATH`` or on a shell variable.

Standard library only.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = "senzing-bootcamp-"
HOOKS_DIRECTORY = Path(".kiro") / "hooks"
TIMEOUT_SECONDS = 30
#: The hook adapter turns a patch into write and edit calls, so a tool the adapter's map calls
#: a patch is matched by every hook that covers either.
PATCH_CATEGORY = "patch"
PATCH_COVERS = {"write", "edit"}


def quoted(value):
    return '"' + str(value).replace('"', '\\"') + '"'


def matcher(config, hooks):
    """The tools one event's hook must match: every name the adapter maps to a category the
    event's scripts cover, in the map's order. Empty when the scripts are limited to no tool.

    The names come from ``tool_categories``, the map the hook adapter itself reads, so the hook
    runs for exactly the tools the adapter would act on.
    """
    covered = {tool for entry in hooks for tool in entry.get("tools", [])}
    if covered & PATCH_COVERS:
        covered.add(PATCH_CATEGORY)
    return "|".join(name for name, category in config["tool_categories"].items() if category in covered)


def definitions(config):
    """``{file name: hook definition}`` for every event the bootcamp declares on this host."""
    found = {}
    for event, trigger in config["host_events"].items():
        hooks = config.get("hooks", {}).get(event)
        if not trigger or not hooks:
            continue
        name = PREFIX + event.replace("_", "-")
        hook = {
            "name": name,
            "trigger": trigger,
            "action": {
                "type": "command",
                "command": f"{quoted(sys.executable)} {quoted(HERE / 'hook_adapter.py')} {event}",
            },
            "timeout": TIMEOUT_SECONDS,
        }
        tools = matcher(config, hooks)
        if tools:
            hook["matcher"] = tools
        found[name + ".json"] = {"version": "v1", "hooks": [hook]}
    return found


def installed(directory):
    return sorted(path for path in directory.glob(PREFIX + "*.json")) if directory.is_dir() else []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("action", choices=("plan", "install", "remove"))
    parser.add_argument("--workspace", required=True, help="the bootcamper's project directory")
    parser.add_argument("--yes", action="store_true", help="the bootcamper has agreed (install only)")
    arguments = parser.parse_args(argv)

    workspace = Path(arguments.workspace).expanduser().resolve()
    if not workspace.is_dir():
        print(f"error: {workspace} is not a directory", file=sys.stderr)
        return 2
    directory = workspace / HOOKS_DIRECTORY
    with open(HERE / "bootcamp_host.json", encoding="utf-8") as handle:
        wanted = definitions(json.load(handle))

    if arguments.action == "remove":
        removed = installed(directory)
        for path in removed:
            path.unlink()
        print(f"Removed {len(removed)} bootcamp hook file(s) from {directory}.")
        return 0

    others = [path.name for path in sorted(directory.glob("*.json"))
              if not path.name.startswith(PREFIX)] if directory.is_dir() else []
    print(f"Python interpreter: {sys.executable}")
    print(f"Hook adapter:       {HERE / 'hook_adapter.py'}")
    print(f"Hook files ({len(wanted)}), each in {directory}:")
    for name, definition in wanted.items():
        hook = definition["hooks"][0]
        matcher = f", tools {hook['matcher']}" if "matcher" in hook else ""
        print(f"  {name}: on {hook['trigger']}{matcher}")
        print(f"    runs {hook['action']['command']}")
    stale = [path.name for path in installed(directory) if path.name not in wanted]
    if stale:
        print(f"Bootcamp hook files no longer used, which install removes: {', '.join(stale)}")
    print(f"Other hook files there, left untouched: {', '.join(others) if others else 'none'}")

    if arguments.action == "plan":
        print("Nothing was written.")
        return 0
    if not arguments.yes:
        print("error: install needs --yes, given only after the bootcamper has agreed", file=sys.stderr)
        return 2
    directory.mkdir(parents=True, exist_ok=True)
    for path in installed(directory):
        if path.name not in wanted:
            path.unlink()
    for name, definition in wanted.items():
        (directory / name).write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")
    print(f"Installed {len(wanted)} bootcamp hook file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
