"""The guide is told to read every long file to the last line, on every assistant (PR #3, #39).

Kiro IDE 1.4.26 cuts a tool result at about 30,000 characters, and `ground-rules.md` is about
134 KB. On 2026-11-15 a first turn there read under a tenth of the file before the welcome, so
most of the bootcamp's rules were never seen. The onboarding skill now says a read that was cut
short has not read the file, and to continue to the last line before the first reply.

The ground rules are not the only file over that size (#39). Each package holds 17 more files of
instructions over the cut, four of them `SKILL.md` files. A skill is loaded with no hand-over
sentence, and a phase file is handed over by name, so the step that names the ground rules
reaches none of them. The build therefore puts one instruction at the top of every Markdown file
over the cut, in every package: after the frontmatter where the file has one, otherwise first in
the file. It says "before acting on anything this file says", which also fits a file read after
the first turn.

- **The cut is the build's.** `READ_CUT_CHARACTERS` in `tools/bootcamp_build/emit.py` is the one
  definition, and this file reads it from there. A file of that many characters or fewer gets
  no instruction.
- **Each package is judged on its own files.** The size is the file's size in characters as
  built for that package, before the instruction is added. One file can be over the cut in one
  package and under it in another.
- **The docs directory is left alone.** What is there is for the bootcamper to read, and the
  example recap in it ships as a pair with a PDF. The directory is read from each assistant's
  profile, because one assistant keeps it inside a skill.
- **No file in `source/` carries the instruction.** A file that grows past the cut gets it at
  the next build, and one that shrinks under the cut loses it.

The instruction is compared with the build's own text, line wraps included, because the build
writes it and the claim is that every file carries the same text. What it says is checked with
whitespace collapsed (INV-346).

Enforces **INV-427** (registered 2026-11-16). It establishes that every package carries the
instruction at the step that names the ground rules and at the top of every long file; it does
not establish that a live turn obeys it, which only a run on the assistant can show
(`hosts/kiro/checks.json` records one that did, for the ground rules). No run on a real
assistant was made for #39.

Run:  python3 -m unittest discover -s tests
"""
import re
import tempfile
import unittest
from pathlib import Path

from _built import built
from test_bootcamp_build_emit import Workspace

from tools.bootcamp_build.emit import READ_CUT_CHARACTERS, READ_TO_THE_END_NOTE, TEXT_SUFFIXES
from tools.bootcamp_build.model import HOSTS_DIR, SOURCE_DIR, host_ids, load_host

HOSTS = ("claude", "copilot", "kiro", "chatgpt", "gemini")
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
#: What the instruction must say, with whitespace collapsed.
PARTS = (
    "(INV-427) Read this file to its last line.",
    "a read that reports it was cut short or truncated has not read it",
    "continue from where it stopped, in as many reads as it takes",
    "before acting on anything this file says",
)


def flat(text):
    """Whitespace collapsed, so a re-wrapped sentence still matches."""
    return re.sub(r"\s+", " ", text)


def step_one(host):
    text = flat((built(host) / "skills" / "bootcamp-onboarding" / "SKILL.md").read_text(encoding="utf-8"))
    start = text.index("1. **Read and follow `ground-rules.md`**")
    return text[start:text.index("2. **Fresh start vs. resume", start)]


def says_read_to_the_end(step):
    return all(phrase in step for phrase in (
        "(INV-427) Read the file to its last line.",
        "cut short or truncated has not read it",
        "continue from where it stopped",
        "before the first reply",
    ))


def says_everything(instruction):
    """True when the instruction at the top of a file says every part the rule has."""
    return all(part in flat(instruction) for part in PARTS)


def read(path):
    """A file's text as the build wrote it, with no newline translation."""
    return Path(path).read_bytes().decode("utf-8")


def body(text):
    """The text from its first body line: past the frontmatter, where it has one, and blank lines."""
    match = FRONTMATTER.match(text)
    return (text[match.end():] if match else text).lstrip("\n")


def carries_the_instruction(text):
    """True when the instruction, then a blank line, is the file's first body text."""
    return body(text).startswith(READ_TO_THE_END_NOTE + "\n")


def before_the_instruction(text):
    """The file as the build measured it: without the instruction, where it carries one."""
    if not carries_the_instruction(text):
        return text
    rest = body(text)
    return text[:len(text) - len(rest)] + rest[len(READ_TO_THE_END_NOTE) + 1:]


def is_over_the_cut(text):
    return len(before_the_instruction(text)) > READ_CUT_CHARACTERS


def docs_directory(host):
    """Where the assistant's package keeps its docs, from the assistant's own profile."""
    return load_host(host).layout["docs"]


def markdown_files(root, docs):
    """``(package path, text)`` of every Markdown file in a package, outside its docs directory."""
    found = []
    for path in sorted(Path(root).rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        if not relative.startswith(docs + "/"):
            found.append((relative, read(path)))
    return found


def over_the_cut(root, docs):
    return [(relative, text) for relative, text in markdown_files(root, docs) if is_over_the_cut(text)]


def lacking_the_instruction(root, docs):
    """The check: every file over the cut that does not carry the instruction as its first body text."""
    return [relative for relative, text in over_the_cut(root, docs) if not carries_the_instruction(text)]


def carrying_it_without_cause(root, docs):
    """Every file at or under the cut that carries the instruction all the same."""
    return [relative for relative, text in markdown_files(root, docs)
            if carries_the_instruction(text) and not is_over_the_cut(text)]


class TheGroundRulesAreReadToTheEnd(unittest.TestCase):
    def test_every_package_says_so_at_the_step_that_names_the_file(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertTrue(says_read_to_the_end(step_one(host)), step_one(host))

    def test_the_instruction_is_the_same_in_every_package(self):
        steps = {host: step_one(host).split("⛔", 1)[1] for host in HOSTS}
        self.assertEqual(len(set(steps.values())), 1, steps)


class TheCheckSeesAStepWithoutIt(unittest.TestCase):
    def test_a_step_missing_any_part_fails(self):
        whole = step_one("claude")
        self.assertTrue(says_read_to_the_end(whole))
        for part in ("Read the file to its last line.", "continue from where it stopped",
                     "before the first reply"):
            with self.subTest(part=part):
                self.assertFalse(says_read_to_the_end(whole.replace(part, "")))


class EveryLongFileSaysSoAtItsTop(unittest.TestCase):
    """What each built package carries (#39). The assistants are the build's own list."""

    def test_the_five_assistants_are_all_built(self):
        self.assertLessEqual(set(HOSTS), set(host_ids()))

    def test_every_file_over_the_cut_carries_the_instruction(self):
        for host in host_ids():
            with self.subTest(host=host):
                found = over_the_cut(built(host), docs_directory(host))
                self.assertTrue(found, "no Markdown file over the cut was found, so nothing was checked")
                self.assertEqual(lacking_the_instruction(built(host), docs_directory(host)), [])

    def test_the_files_found_include_the_ground_rules_and_a_skill(self):
        for host in host_ids():
            with self.subTest(host=host):
                names = [relative for relative, _ in over_the_cut(built(host), docs_directory(host))]
                self.assertIn("skills/bootcamp-onboarding/ground-rules.md", names)
                self.assertTrue([name for name in names if name.endswith("/SKILL.md")], names)

    def test_it_is_after_the_frontmatter_or_first_in_the_file(self):
        for host in host_ids():
            for relative, text in over_the_cut(built(host), docs_directory(host)):
                with self.subTest(host=host, file=relative):
                    match = FRONTMATTER.match(text)
                    if match:
                        self.assertTrue(text[match.end():].startswith("\n" + READ_TO_THE_END_NOTE + "\n"),
                                        text[:match.end() + 400])
                    else:
                        self.assertTrue(text.startswith(READ_TO_THE_END_NOTE + "\n"), text[:400])

    def test_a_skill_over_the_cut_still_starts_with_its_frontmatter(self):
        for host in host_ids():
            for relative, text in over_the_cut(built(host), docs_directory(host)):
                if relative.endswith("/SKILL.md"):
                    with self.subTest(host=host, file=relative):
                        self.assertIsNotNone(FRONTMATTER.match(text), text[:200])

    def test_it_is_the_same_text_in_every_package_and_every_file(self):
        seen = set()
        for host in host_ids():
            for _, text in over_the_cut(built(host), docs_directory(host)):
                seen.add(body(text).split("\n\n", 1)[0] + "\n")
        self.assertEqual(seen, {READ_TO_THE_END_NOTE})

    def test_each_file_carries_it_once(self):
        for host in host_ids():
            for relative, text in over_the_cut(built(host), docs_directory(host)):
                with self.subTest(host=host, file=relative):
                    self.assertEqual(flat(text).count(PARTS[0]), 1)

    def test_a_file_at_or_under_the_cut_carries_none(self):
        for host in host_ids():
            with self.subTest(host=host):
                root, docs = built(host), docs_directory(host)
                self.assertGreater(len(markdown_files(root, docs)), len(over_the_cut(root, docs)))
                self.assertEqual(carrying_it_without_cause(root, docs), [])

    def test_the_docs_directory_is_left_alone(self):
        for host in host_ids():
            with self.subTest(host=host):
                files = sorted((built(host) / docs_directory(host)).rglob("*.md"))
                self.assertTrue(files, "the package's docs directory holds no Markdown file")
                for path in files:
                    self.assertNotIn(PARTS[0], flat(read(path)), path.name)


class TheInstructionItself(unittest.TestCase):
    def test_it_says_every_part_and_cites_the_invariant(self):
        self.assertTrue(says_everything(READ_TO_THE_END_NOTE), READ_TO_THE_END_NOTE)
        self.assertIn("INV-427", READ_TO_THE_END_NOTE)

    def test_one_with_a_part_missing_does_not_pass(self):
        for part in PARTS:
            with self.subTest(part=part):
                self.assertFalse(says_everything(flat(READ_TO_THE_END_NOTE).replace(part, "")))

    def test_it_names_no_assistant(self):
        for host_id in host_ids():
            host = load_host(host_id)
            for term in (host.id, host.name, host.vars["product"], *host.foreign_terms):
                with self.subTest(host=host_id, term=term):
                    self.assertIsNone(re.search(term, READ_TO_THE_END_NOTE, re.IGNORECASE))

    def test_no_file_the_build_reads_carries_it_by_hand(self):
        carried = []
        for root in (SOURCE_DIR, HOSTS_DIR):
            for path in sorted(root.rglob("*")):
                if path.is_file() and path.suffix in TEXT_SUFFIXES and PARTS[0] in flat(read(path)):
                    carried.append(path.relative_to(root.parent).as_posix())
        self.assertEqual(carried, [])


def of_size(size, start="# A long file\n\n"):
    """Markdown of exactly ``size`` characters that begins with ``start``."""
    filler = "One more line of the file.\n"
    text = start + filler * (size // len(filler) + 1)
    return text[:size - 1] + "\n"


class TheBuildAddsItByTheBuiltSize(Workspace):
    """The build's own rule, on a miniature repository: the cut, the size it measures, the docs."""

    def package(self, host_id):
        return self.build(host_id)[1].root

    def test_one_character_over_the_cut_gets_it_and_the_cut_itself_does_not(self):
        over, at = of_size(READ_CUT_CHARACTERS + 1), of_size(READ_CUT_CHARACTERS)
        self.write("source/skills/start/over.md", over)
        self.write("source/skills/start/at.md", at)
        root = self.package("alpha")
        self.assertEqual(read(root / "skills/start/over.md"), READ_TO_THE_END_NOTE + "\n" + over)
        self.assertEqual(read(root / "skills/start/at.md"), at)
        self.assertEqual(lacking_the_instruction(root, "docs"), [])
        self.assertEqual(carrying_it_without_cause(root, "docs"), [])

    def test_a_file_with_frontmatter_gets_it_after_the_frontmatter(self):
        frontmatter = "---\nname: long\ndescription: A long skill.\n---\n"
        text = of_size(READ_CUT_CHARACTERS + 500, frontmatter + "\n# A long skill\n\n")
        self.write("source/skills/long/SKILL.md", text)
        built_text = read(self.package("alpha") / "skills/long/SKILL.md")
        self.assertEqual(built_text,
                         frontmatter + "\n" + READ_TO_THE_END_NOTE + "\n" + text[len(frontmatter) + 1:])
        self.assertEqual(before_the_instruction(built_text), text)

    def test_the_size_is_measured_on_the_file_as_built_for_that_package(self):
        # "Alpha Code" is one character longer than "Beta Chat", so the same source file is one
        # character over the cut in one package and exactly at it in the other.
        start = "# For {{host.product}}\n\n"
        source = of_size(READ_CUT_CHARACTERS + len("{{host.product}}") - len("Beta Chat"), start)
        self.write("source/skills/start/sized.md", source)
        alpha = read(self.package("alpha") / "skills/start/sized.md")
        beta = read(self.package("beta") / "skills/start/sized.md")
        self.assertEqual(len(beta), READ_CUT_CHARACTERS)
        self.assertFalse(carries_the_instruction(beta))
        self.assertTrue(carries_the_instruction(alpha))
        self.assertEqual(len(before_the_instruction(alpha)), READ_CUT_CHARACTERS + 1)

    def test_a_file_that_grows_past_the_cut_gets_it_and_one_that_shrinks_loses_it(self):
        self.write("source/skills/start/phase.md", of_size(READ_CUT_CHARACTERS))
        self.assertFalse(carries_the_instruction(read(self.package("alpha") / "skills/start/phase.md")))
        self.write("source/skills/start/phase.md", of_size(READ_CUT_CHARACTERS + 1))
        self.assertTrue(carries_the_instruction(read(self.package("alpha") / "skills/start/phase.md")))
        self.write("source/skills/start/phase.md", of_size(READ_CUT_CHARACTERS))
        self.assertFalse(carries_the_instruction(read(self.package("alpha") / "skills/start/phase.md")))

    def test_the_docs_directory_is_left_alone_wherever_the_layout_puts_it(self):
        long = of_size(READ_CUT_CHARACTERS * 2)
        self.write("source/docs/examples/recap.md", long)
        self.write("source/skills/start/phase.md", long)
        for host_id, product, docs in (("alpha", "Alpha Code", "docs"), ("beta", "Beta Chat", "skills/start/docs")):
            with self.subTest(docs=docs):
                self.profile(host_id, product, layout={"skills": "skills", "scripts": "scripts", "docs": docs})
                root = self.package(host_id)
                self.assertEqual(read(root / docs / "examples/recap.md"), long)
                self.assertTrue(carries_the_instruction(read(root / "skills/start/phase.md")))
                self.assertEqual(lacking_the_instruction(root, docs), [])

    def test_a_file_that_is_not_markdown_is_left_alone(self):
        script = "# " + of_size(READ_CUT_CHARACTERS * 2, "a long script\n")
        self.write("source/scripts/long.py", script)
        self.assertEqual(read(self.package("alpha") / "scripts/long.py"), script)


class TheCheckSeesAFileWithoutIt(unittest.TestCase):
    """Negative controls: the check on packages that are wrong in one way each."""

    def package(self, files):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        for relative, text in files.items():
            path = Path(scratch.name) / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode("utf-8"))
        return Path(scratch.name)

    def test_a_file_over_the_cut_without_it_fails(self):
        root = self.package({"skills/a/long.md": of_size(READ_CUT_CHARACTERS + 1)})
        self.assertEqual(lacking_the_instruction(root, "docs"), ["skills/a/long.md"])

    def test_the_same_file_with_it_passes(self):
        root = self.package({"skills/a/long.md": READ_TO_THE_END_NOTE + "\n" + of_size(READ_CUT_CHARACTERS + 1)})
        self.assertEqual(lacking_the_instruction(root, "docs"), [])

    def test_a_real_file_with_the_instruction_taken_out_fails(self):
        relative = "skills/bootcamp-onboarding/ground-rules.md"
        for host in host_ids():
            with self.subTest(host=host):
                shipped = read(built(host) / relative)
                self.assertTrue(carries_the_instruction(shipped))
                root = self.package({relative: before_the_instruction(shipped)})
                self.assertEqual(lacking_the_instruction(root, docs_directory(host)), [relative])

    def test_a_skill_with_frontmatter_and_no_instruction_fails(self):
        skill = of_size(READ_CUT_CHARACTERS + 200, "---\nname: a\ndescription: A skill.\n---\n\n# A skill\n\n")
        root = self.package({"skills/a/SKILL.md": skill})
        self.assertEqual(lacking_the_instruction(root, "docs"), ["skills/a/SKILL.md"])

    def test_an_instruction_that_is_not_the_first_body_text_fails(self):
        text = of_size(READ_CUT_CHARACTERS + 1)
        moved = text[:len("# A long file\n\n")] + READ_TO_THE_END_NOTE + "\n" + text[len("# A long file\n\n"):]
        root = self.package({"skills/a/long.md": moved})
        self.assertEqual(lacking_the_instruction(root, "docs"), ["skills/a/long.md"])

    def test_an_instruction_with_a_part_missing_fails(self):
        for part in ("Read this file to its last line.", "continue from where it stopped",
                     "before acting on anything this file says"):
            with self.subTest(part=part):
                changed = READ_TO_THE_END_NOTE.replace(part, "")
                self.assertNotEqual(changed, READ_TO_THE_END_NOTE)
                root = self.package({"skills/a/long.md": changed + "\n" + of_size(READ_CUT_CHARACTERS + 1)})
                self.assertEqual(lacking_the_instruction(root, "docs"), ["skills/a/long.md"])

    def test_a_file_at_the_cut_or_in_the_docs_directory_is_not_reported(self):
        root = self.package({
            "skills/a/at.md": of_size(READ_CUT_CHARACTERS),
            "docs/examples/recap.md": of_size(READ_CUT_CHARACTERS * 2),
            "skills/a/docs/examples/recap.md": of_size(READ_CUT_CHARACTERS * 2),
        })
        self.assertEqual(lacking_the_instruction(root, "docs"), ["skills/a/docs/examples/recap.md"])
        self.assertEqual(lacking_the_instruction(root, "skills/a/docs"), ["docs/examples/recap.md"])

    def test_an_instruction_on_a_file_under_the_cut_is_reported(self):
        root = self.package({"skills/a/short.md": READ_TO_THE_END_NOTE + "\n" + of_size(READ_CUT_CHARACTERS)})
        self.assertEqual(carrying_it_without_cause(root, "docs"), ["skills/a/short.md"])


if __name__ == "__main__":
    unittest.main()
