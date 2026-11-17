"""How each assistant's package names the bootcamp's operations (issue #28).

The bootcamp has one operation per file in ``source/commands/``. The Claude package ships each
as a slash command and names it that way. Every other package ships the same operations as
skills and names each by the plain-language request its install page gives. Which form an
assistant uses is a host value, ``invoke_<command>`` in ``hosts/<assistant>/host.json``.

A test that pinned a slash form by reading ``source/`` reads each built package through this
module instead, and holds the form that package's assistant uses: the slash form where the
package ships commands, the request form everywhere else.

Stdlib only; packages are built by ``_built.built`` (INV-108).
"""
from pathlib import PurePosixPath

from _built import SOURCE_DIR, built, host_ids, load_host

#: Every assistant the bootcamp is built for, from ``hosts/``.
HOSTS = tuple(host_ids())
COMMANDS_DIR = SOURCE_DIR / "commands"

#: The host value that holds the packaging operation in the form a script can print from a
#: double-quoted string: the request in straight single quotes.
PACKAGE_IN_STRING = "invoke_package_bootcamp_in_string"

#: The closing line of graduation in its two pinned forms (INV-057, issue #28): the slash
#: command where the package ships commands, the request everywhere else.
PACKAGE_LINE_COMMAND = (
    "Run `/package-bootcamp` anytime to bundle your bootcamp results into one zip you can "
    "archive, move to another machine, or share with others."
)
PACKAGE_LINE_REQUEST = (
    "Say \"Back up the bootcamp\" anytime to bundle your bootcamp results into one zip you can "
    "archive, move to another machine, or share with others."
)


def command_names():
    """The operations, by the names of the files in ``source/commands/``."""
    return tuple(sorted(path.stem for path in COMMANDS_DIR.glob("*.md")))


def ships_commands(host_id):
    """True when ``host_id``'s package carries the commands as commands, not as skills."""
    return load_host(host_id).layout.get("commands") is not None


#: The assistants whose package names a slash command, and the ones whose package names a request.
COMMAND_HOSTS = tuple(host for host in HOSTS if ships_commands(host))
REQUEST_HOSTS = tuple(host for host in HOSTS if not ships_commands(host))


def value_name(command):
    """The host value that says how ``command`` is invoked: ``invoke_`` and the command's name."""
    return "invoke_" + command.replace("-", "_")


def invocation(host_id, command):
    """How ``host_id`` invokes ``command``, as its host value writes it."""
    return load_host(host_id).vars[value_name(command)]


def mention(host_id, command):
    """``command`` as an inline mention reads in ``host_id``'s Markdown: the value in backticks."""
    return "`%s`" % invocation(host_id, command)


def package_line(host_id):
    """The closing line of graduation as ``host_id``'s package pins it."""
    return PACKAGE_LINE_COMMAND if ships_commands(host_id) else PACKAGE_LINE_REQUEST


def package_path(host_id, relative):
    """Where ``source/<relative>`` is in ``host_id``'s built package.

    The assistant's layout places it, the more specific entry first, as the build does. A
    command lands as ``skills/<name>/SKILL.md`` in a package that ships no commands.
    """
    host = load_host(host_id)
    source = PurePosixPath(relative)
    if source.parts[0] == "commands" and not ships_commands(host_id):
        return built(host_id) / "skills" / source.stem / "SKILL.md"
    entries = [entry for entry in host.layout
               if source.as_posix() == entry or source.as_posix().startswith(entry + "/")]
    assert entries, "hosts/%s/host.json places no source/%s" % (host_id, relative)
    entry = max(entries, key=len)
    assert host.layout[entry] is not None, "%s's package drops source/%s" % (host_id, relative)
    return built(host_id) / host.layout[entry] / source.relative_to(entry)


def package_text(host_id, relative):
    """The text of ``source/<relative>`` as ``host_id``'s built package carries it."""
    return package_path(host_id, relative).read_text(encoding="utf-8")


def scripts_dir(host_id):
    """The directory holding ``host_id``'s scripts in its built package."""
    return package_path(host_id, "scripts/session-start.py").parent
