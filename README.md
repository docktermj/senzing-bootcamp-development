# Senzing Agentic AI Bootcamp: development

This repository is where the Senzing Agentic AI Bootcamp is developed for every AI assistant
it runs in: Claude, GitHub Copilot, Kiro, ChatGPT and Gemini.
Bootcampers install from the public repository, [Senzing/bootcamp].

## One source, every assistant

The bootcamp is written once, in `source/`.
A build writes each assistant's package from it, so a change to the bootcamp reaches every
assistant and no assistant gets its own copy to drift.

| Path | What it holds |
| --- | --- |
| `source/` | The bootcamp: skills, commands, scripts and example documents, with no assistant written into it |
| `hosts/<assistant>/` | What differs for one assistant: its names for things, its package format, its hook events and its install steps |
| `hosts/_shared/` | The hook adapter, which lets the same hook scripts run on assistants whose hook payloads differ |
| `tools/bootcamp_build/` | The build, its checks and the promotion to the public repository |
| `site/` | The pages published at [hub.senzing.com/bootcamp]; they become `docs/` in the public repository |
| `public/` | Files copied to the root of the public repository as they are, such as its README |
| `tests/` | The test suite |
| `specs/` | The invariant register and its ledgers |
| `.claude/skills/` | The maintainer operations |

The source marks every place where assistants differ, in one of three ways:

- `{{host.name}}`: a value from the assistant's profile, such as its product name.
- `<!-- host:only claude, kiro -->` … `<!-- host:end -->`: lines kept only for the named assistants.
- `<!-- host:include name -->`: a passage each assistant supplies, from `hosts/<assistant>/fragments/`.

Text outside a marker is copied unchanged into every package.
That is what keeps the bootcamp the same everywhere, and it is why a test that passes on
`source/` holds for every assistant.

## Everyday commands

Run these from the repository root. They need only Python 3.

```console
python3 -m tools.bootcamp_build build                 # write every package, catalog and page under dist/
python3 -m tools.bootcamp_build check                 # build twice and run every cross-assistant check
python3 -m unittest discover -s tests                 # the test suite
python3 -m tools.bootcamp_build promote --to ~/github.com/senzing/bootcamp
```

`check` stops a change that would reach only some assistants. It fails when:

- the source names an assistant outside a marker for that assistant
- a built package names a different assistant
- an assistant does not define a value the source uses, or does not supply a passage it includes
- a source file is not placed, or dropped on purpose, by every assistant
- two builds of the same source differ

`promote` prints what would change in a clone of the public repository and writes nothing.
With `--apply` it writes that clone's working tree and stops there: it never commits or pushes.

## Adding or changing an assistant

An assistant is one directory, `hosts/<assistant>/`:

- `host.json`: its names, where each part of the source lands in its package, its hook events
  and tool names, its catalog file and the facts its install page shows.
- `fragments/`: the passages it supplies, for the bootcamp and for its install page.
- `files/`: files only its package carries.

The build refuses a profile that leaves a hook event undecided.
Where an assistant has no event for a hook, the rule that hook enforces is given to the
assistant as an instruction instead, so the bootcamp behaves the same with or without the hook.

## More

- [docs/development.md](docs/development.md): how a change moves from an issue to a release.
- [specs/README.md](specs/README.md): the invariant register, and where the earlier history is archived.

[hub.senzing.com/bootcamp]: https://hub.senzing.com/bootcamp/
[Senzing/bootcamp]: https://github.com/Senzing/bootcamp
