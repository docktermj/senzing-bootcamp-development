"""Shared reads for the tests of how the bootcamp handles the model and the effort (#4).

Issue #4 settled it: the bootcamp never asks the bootcamper to change the model or the
reasoning effort, the welcome names one suitable model once, and how carefully the guide
works at each stage is one instruction per effort level, identical on every assistant.
Several test modules check a part of that against every assistant's built package. What
they share is here, so a pattern is written once.

Stdlib only; packages are built by ``_built.built`` (INV-108).
"""
import re

from _built import built, host_ids, load_host

#: Every assistant the bootcamp is built for, from ``hosts/``.
HOSTS = tuple(host_ids())

GROUND_RULES = "bootcamp-onboarding/ground-rules.md"
ONBOARDING_FLOW = "bootcamp-onboarding/onboarding-flow.md"

#: Files read as text when a whole package is scanned.
TEXT_SUFFIXES = (".md", ".py", ".json", ".html", ".txt", ".toml", ".yaml", ".yml", ".sh", ".ps1")


def flat(text):
    """``text`` with every run of whitespace collapsed, so a wrapped phrase still matches."""
    return " ".join(text.split())


def skills_dir(host_id):
    """The directory holding ``host_id``'s skills in its built package."""
    return built(host_id) / "skills"


def skill_text(host_id, relative):
    return (skills_dir(host_id) / relative).read_text(encoding="utf-8")


def capable_model(host_id):
    """What ``host_id`` calls its capable-tier model: the ``model_capable`` value."""
    return load_host(host_id).vars["model_capable"]


def package_texts(host_id):
    """``(relative path, text)`` for every text file in ``host_id``'s built package."""
    root = built(host_id)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES or "vendor" in path.parts:
            continue
        try:
            yield path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


#: Every shape a request to change the model or the effort has taken, or would take. Each is
#: searched in collapsed text, so a line wrap cannot hide one. None matches a diagnostic
#: mention ("Model and effort:" in the feedback context) or a prohibition ("never asks you
#: to switch models").
REQUESTS = (
    ("the switch question",
     re.compile(r"Would you like to switch to[^?]{0,200}(?i:model|effort|\{Model\})")),
    ("the confirmation gate", re.compile(r"(?i)done modifying the model")),
    ("a slash command that sets the model or the effort",
     re.compile(r"(?<![\w./-])/(?:model|effort)(?![\w-])")),
    ("a control for the model or the effort",
     re.compile(r"(?i)\b(?:model|reasoning[- ]effort|effort)"
                r"(?: (?:and|or|/) (?:reasoning[- ])?effort)? (?:controls?|pickers?|selectors?)\b")),
    ("the module-start nudge, by a name it had",
     re.compile(r"(?i)model/effort (?:nudge|prompt|switch)|best-value model|model-switch question")),
)

#: A pinned 👉 question: the pointer, then the question in bold.
PINNED_QUESTION = re.compile(r"👉 \*\*((?:[^*]|\*(?!\*))+)\*\*")
#: A word that makes a pinned question one about the model or the effort.
ABOUT_MODEL_OR_EFFORT = re.compile(r"(?i)\b(?:models?|effort)\b")


def requests_in(text):
    """What in ``text`` asks the bootcamper to change the model or the effort, as messages."""
    collapsed = flat(text)
    found = ["%s: %r" % (what, collapsed[max(0, m.start() - 30):m.end() + 30])
             for what, pattern in REQUESTS for m in pattern.finditer(collapsed)]
    found += ["a 👉 question about the model or the effort: %r" % m.group(1)[:90]
              for m in PINNED_QUESTION.finditer(collapsed)
              if ABOUT_MODEL_OR_EFFORT.search(m.group(1))]
    return found


#: The working-depth block in ``ground-rules.md``: from its bullet to the next one.
DEPTH_START = "- **Working depth by stage.**"
DEPTH_END = "- Module start banner:"
#: One table row: a stage and its effort level.
DEPTH_ROW = re.compile(r"^\s*\| ([A-Z][^|]*?) \| ([^|]+?) \|\s*$", re.M)
#: One instruction: a level in bold, then what the guide does at it.
DEPTH_INSTRUCTION = re.compile(r"^\s*- \*\*([a-z]+):\*\* (.+)$", re.M)


def depth_block(text):
    """The working-depth block of a ``ground-rules.md`` text, bullet to next bullet."""
    start = text.index(DEPTH_START)
    return text[start:text.index(DEPTH_END, start)]


def depth_rows(block):
    """``[(stage, level)]`` for the block's table, header left out, in order.

    Line-scoped by design (#4): a Markdown table row is one line.
    """
    return [(stage, level) for stage, level in DEPTH_ROW.findall(block) if stage != "Stage"]


def depth_instructions(block):
    """``[(level, instruction)]`` for the block's instruction lines, in order.

    Line-scoped by design (#4): each instruction is written on one line, so that it is the
    same bytes in every package and in ``docs/model-selection.md``.
    """
    return DEPTH_INSTRUCTION.findall(block)
