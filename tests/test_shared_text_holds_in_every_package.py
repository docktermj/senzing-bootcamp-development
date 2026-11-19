"""Six passages that named one assistant's files, IDs and mechanisms hold in every package (#30).

Text outside a host marker reaches all five packages. `production-readiness-audit-2026-11-17`
(findings 7, 8, 12, 16, 19 and 24) found six small passages that were true in one package and
were shipped in all of them. This file builds every assistant's package from `source/` and reads
what each one ships. The assistants come from the build's own list, so a sixth is covered the day
it is added (INV-246).

1. **The MCP file.** The MCP failure message in `onboarding-flow.md` named `.mcp.json`. Two
   packages ship `mcp.json` and one ships `mcp_config.json`. The message now takes the name from
   `vars.mcp_file` in the assistant's profile. Here the name it states must be the one file at
   the package's root that registers an MCP server, found by reading the package and not from a
   list, and the address it states must be the one that file registers.
2. **The package noun.** The same message said "this plugin's". It takes the noun from
   `vars.package_noun`: "this Power's" in the Kiro package and "this plugin's" in the other four.
   The Kiro package's `host-rules.md`, which the guide reads at the start of every session, says
   once that "plugin" in the bootcamp's files means the Power. No other package carries that
   sentence, and no other file of the Kiro package does. The message was the one piece of text
   shown to the bootcamper word for word that said "plugin"; a sweep of every `text` display
   block and every pinned 👉 question, in each package whose noun is not "plugin", keeps it so.

   ⛔ **Text a package shows the bootcamper word for word names the package by its assistant's own noun.**

   That line is queued as a `DEFERRED INVARIANT` block in this issue's entry of
   `specs/IMPLEMENTED.md`, awaiting the maintainer's sign-off. Until then only this file holds
   it. It binds displayed text only: guide-facing prose, the identifiers `PLUGIN_ROOT` and
   `plugin.json`, the `plugin` routing value and the `**Plugin version:**` label keep the word,
   as the issue decides.
3. **The skill's directory.** `onboarding-flow.md` said "The harness supplies that directory at
   invocation", and the Kiro package also says that Kiro gives no path. The passage no longer
   says who supplies the directory. It is the same text in all five packages and keeps the rest:
   the skill's own directory, two levels up, the plugin whose files are running, and INV-185.
   The path it gives must name a manifest the package carries (INV-252).
4. **The model example.** The `Model / effort` line of the feedback entry gave one assistant's
   model ID as its example. The example is now a placeholder: it holds no model ID, and the line
   is the same in all five packages.
5. **Where the recap generator is.** `graduation/SKILL.md` said the generator is "two levels up
   under `scripts/`", which is false in the Kiro package. The passage states the path from
   `vars.scripts_relative`. Here that path, counted from `skills/graduation/` in each built
   package, must be the directory that holds `generate_recap_pdf.py`, and the command under the
   passage must name the same file.
6. **The handle that is not a pid.** A warning in `visualization-api-reference.md` named a
   "background-task" mechanism, a feature of one assistant, in every package. It is reworded to
   name no feature. It must still say that the id is not a pid, that no pid is recorded from it,
   and that the pid comes from the launch confirmation's port lookup.
   `tests/test_viz_server_process_handle.py` pins its place in the launch confirmation and
   mutates it.
   This holds **INV-223**'s 2026-11-17 note (#30, applied 2026-11-18) in every built package;
   it cannot establish that a live turn records no pid from such an id.

The build's check for another assistant's name ignores letter case since #30, which is how the
model ID in passage 4 went unreported. `tests/test_bootcamp_build_emit.py` plants a lowercase
name in a package and in the source and sees each reported. `TheCheckIgnoresCaseOnTheRealTree`
here holds the real tree to the recorded ceilings: nothing in `source/`, and in each non-Claude
package the one project-directory variable the hook adapter reads.

Each check is a function over text, and a negative control feeds it the wording #30 replaced, or
another package's value, and sees it reported.

**What this cannot establish.** That a guide on a real assistant shows the failure message, reads
`host-rules.md`, or acts on the warning. Nothing here runs an assistant; only a run recorded in
`hosts/<assistant>/checks.json` observes that. Whether any assistant other than Claude has a
feature the warning would apply to was not looked into, as the issue decides. It was run on
Linux only.

Prose is read wrap-aware: every text check collapses whitespace first (INV-346).

Stdlib only; nothing under `source/` is imported into this process (INV-108).

Run:  python3 -m unittest discover -s tests
"""
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from _built import SOURCE_DIR, built, host_ids, load_declaration, load_host  # a package per assistant

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.emit import HostBuild  # noqa: E402
from tools.bootcamp_build.validate import lint_source, residue  # noqa: E402

HOSTS = tuple(host_ids())
ONBOARDING = "bootcamp-onboarding"


def read(path):
    return Path(path).read_bytes().decode("utf-8")


def flat(text):
    """Text with every run of whitespace made one space, so a line wrap changes nothing."""
    return " ".join(text.split())


def skill_file(host, relative):
    """One skill file of ``host``'s built package, by its path under the skills directory."""
    return built(host) / load_host(host).layout["skills"] / relative


def markdown(host):
    return sorted(built(host).rglob("*.md"))


def one(found, what):
    """The only item of ``found``; more or fewer is a failure that says what was looked for."""
    if len(found) != 1:
        raise AssertionError("expected one %s, found %d: %r" % (what, len(found), found))
    return found[0]


def agreed(values, what):
    """The one value all hosts share. ``values`` is ``{host: value}``."""
    if len(set(values.values())) != 1:
        raise AssertionError("%s differs between packages: %r" % (what, values))
    return next(iter(values.values()))


# --- 1 and 2: the MCP failure message --------------------------------------------------------

#: The message's line that says where the server's registration ships: the noun, the file, the
#: address. Read from collapsed text.
SHIPS_WITH = re.compile(r"\(it ships with this (\S+)'s (\S+), pointing at (\S+)\)\.")


def failure_message(text):
    """The fenced block the guide shows when the MCP server does not answer, collapsed."""
    blocks = [block for block in re.findall(r"(?ms)^ *```text\n(.*?)^ *```", text)
              if "The Senzing MCP server is unreachable." in block]
    return flat(one(blocks, "MCP failure message"))


def ships_with(text):
    """``(noun, file, address)`` as the failure message states them."""
    return one(SHIPS_WITH.findall(failure_message(text)), "'it ships with' line")


def mcp_registrations(root):
    """``{file name: [server address, …]}`` for each JSON file at a package's root that registers
    an MCP server. Found by reading the files, so no list of names is kept here."""
    found = {}
    for path in sorted(Path(root).glob("*.json")) + sorted(Path(root).glob(".*.json")):
        try:
            data = json.loads(read(path))
        except ValueError:
            continue
        servers = data.get("mcpServers") if isinstance(data, dict) else None
        if isinstance(servers, dict) and servers:
            found[path.name] = sorted(str(server.get("url")) for server in servers.values())
    return found


def onboarding_flow(host):
    return read(skill_file(host, ONBOARDING + "/onboarding-flow.md"))


class TheMcpFailureMessageNamesThePackagesOwnFile(unittest.TestCase):
    def test_the_build_lists_five_assistants_or_more(self):
        self.assertGreaterEqual(len(HOSTS), 5, HOSTS)

    def test_every_package_registers_the_server_in_one_file_at_its_root(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual(1, len(mcp_registrations(built(host))), mcp_registrations(built(host)))

    def test_the_message_names_the_file_the_package_ships(self):
        for host in HOSTS:
            with self.subTest(host=host):
                shipped = one(sorted(mcp_registrations(built(host))), "MCP registration file")
                _, named, _ = ships_with(onboarding_flow(host))
                self.assertEqual(shipped, named,
                                 "the %s package ships %s and its failure message names %s"
                                 % (host, shipped, named))
                self.assertEqual(shipped, load_host(host).vars["mcp_file"])

    def test_the_message_states_the_address_that_file_registers(self):
        for host in HOSTS:
            with self.subTest(host=host):
                registrations = mcp_registrations(built(host))
                _, named, address = ships_with(onboarding_flow(host))
                self.assertEqual([address], registrations[named])

    def test_the_packages_do_not_all_ship_one_file_name(self):
        """Or the check above could not tell a host value from the literal it replaced."""
        names = {one(sorted(mcp_registrations(built(host))), "MCP registration file")
                 for host in HOSTS}
        self.assertGreaterEqual(len(names), 3, names)

    def test_the_source_takes_both_values_from_the_host_profile(self):
        message = failure_message(read(SOURCE_DIR / "skills" / ONBOARDING / "onboarding-flow.md"))
        self.assertIn("(it ships with this {{host.package_noun}}'s {{host.mcp_file}}, pointing at",
                      message)

    def test_the_message_is_otherwise_the_same_in_every_package(self):
        rest = {}
        for host in HOSTS:
            message = failure_message(onboarding_flow(host))
            noun, named, _ = ships_with(onboarding_flow(host))
            values = load_host(host).vars
            self.assertIn(values["product"], message)
            rest[host] = (message.replace("this %s's %s," % (noun, named), "this <noun>'s <file>,")
                          .replace(values["product"], "<product>"))
        agreed(rest, "the MCP failure message, apart from its three host values")

    def test_another_packages_file_name_is_reported(self):
        """Negative control: the wording #30 replaced fails in a package that ships another file."""
        fixed = {host: one(sorted(mcp_registrations(built(host))), "MCP registration file")
                 for host in HOSTS}
        differing = [host for host in HOSTS if fixed[host] != ".mcp.json"]
        self.assertTrue(differing, "no package ships a file other than .mcp.json")
        for host in differing:
            with self.subTest(host=host):
                noun, named, _ = ships_with(onboarding_flow(host))
                old = onboarding_flow(host).replace("this %s's %s," % (noun, named),
                                                    "this plugin's .mcp.json,")
                self.assertNotEqual(fixed[host], ships_with(old)[1])


#: A block the guide shows as written, and a pinned question: the bold span a 👉 opens, which
#: can wrap over lines.
DISPLAY_BLOCK = re.compile(r"(?ms)^( *)```text\n(.*?)^\1```")
PINNED_QUESTION = re.compile(r"👉\s*\*\*(.+?)\*\*", re.S)
#: The word, not an identifier that holds it: `PLUGIN_ROOT` and `plugin.json` are names.
PLUGIN_WORD = re.compile(r"(?i)(?<![\w.-])plugins?(?![\w]|\.json)")


def displayed(text):
    """Every piece of ``text`` shown to the bootcamper word for word, each collapsed."""
    return ([flat(match.group(2)) for match in DISPLAY_BLOCK.finditer(text)]
            + [flat(match.group(1)) for match in PINNED_QUESTION.finditer(text)])


def says_plugin(text):
    return PLUGIN_WORD.search(text) is not None


class ThePackageNounIsTheAssistantsOwn(unittest.TestCase):
    #: The sentence the build adds to `host-rules.md` where the assistant's noun is not "plugin".
    MEANS = re.compile(r"In the bootcamp's files, \"plugin\" means this (\S+)\.")

    def carrying(self, host):
        """``[(file, noun), …]`` for every statement of the sentence in ``host``'s Markdown."""
        return [(path.relative_to(built(host)).as_posix(), noun)
                for path in markdown(host) for noun in self.MEANS.findall(flat(read(path)))]

    def test_the_message_says_power_on_kiro_and_plugin_elsewhere(self):
        for host in HOSTS:
            with self.subTest(host=host):
                noun, _, _ = ships_with(onboarding_flow(host))
                self.assertEqual("Power" if host == "kiro" else "plugin", noun)
                self.assertEqual(load_host(host).vars["package_noun"], noun)

    def test_the_kiro_host_rules_say_once_that_plugin_means_the_power(self):
        skills = load_host("kiro").layout["skills"]
        self.assertEqual([("%s/%s/host-rules.md" % (skills, ONBOARDING), "Power")],
                         self.carrying("kiro"))

    def test_no_other_package_carries_the_sentence(self):
        for host in HOSTS:
            if host == "kiro":
                continue
            with self.subTest(host=host):
                self.assertEqual([], self.carrying(host))
                for path in markdown(host):
                    self.assertNotIn('"plugin" means', flat(read(path)), path.name)

    def test_the_guide_is_told_to_read_that_file_every_session(self):
        """The sentence is worth one line only because the guide reads the file that holds it."""
        rules = flat(read(skill_file("kiro", ONBOARDING + "/ground-rules.md")))
        self.assertIn("Read `host-rules.md`, beside this file, at the start of every session", rules)
        self.assertTrue(skill_file("kiro", ONBOARDING + "/host-rules.md").is_file())

    def test_no_displayed_text_says_plugin_where_the_noun_is_another(self):
        swept = 0
        for host in HOSTS:
            if load_host(host).vars["package_noun"] == "plugin":
                continue
            with self.subTest(host=host):
                shown = [(path.name, text) for path in markdown(host)
                         for text in displayed(read(path))]
                # Vacuity floor: 44 display blocks and 132 pinned questions in the Kiro
                # package on 2026-11-17.
                self.assertGreater(len(shown), 100, "the sweep found too little displayed text")
                self.assertEqual([], [(name, text[:80]) for name, text in shown
                                      if says_plugin(text)])
                swept += 1
        self.assertGreater(swept, 0, "no package has a noun other than plugin")

    def test_the_sweep_reports_the_wording_the_message_had(self):
        """Negative control: a display block and a pinned question that say "plugin"."""
        block = "```text\n(it ships with this plugin's mcp.json)\n```\n"
        question = "👉 **Would you like to reinstall the\nplugin now?**\n"
        for text in (block, question):
            with self.subTest(text=text[:20]):
                self.assertEqual(1, len([shown for shown in displayed(text) if says_plugin(shown)]))
        prose = "Read the plugin manifest, then ask the 👉 question below.\n"
        self.assertEqual([], [shown for shown in displayed(prose) if says_plugin(shown)])
        self.assertFalse(says_plugin("set PLUGIN_ROOT, then read plugin.json"))

    def test_the_sentence_follows_the_noun_and_not_the_assistant(self):
        """Every profile whose noun is not "plugin" gets the sentence; no host id is tested."""
        for host in HOSTS:
            with self.subTest(host=host):
                noun = load_host(host).vars["package_noun"]
                expected = [] if noun == "plugin" else [noun]
                self.assertEqual(expected, [found for _, found in self.carrying(host)])


# --- 3: the skill's directory ----------------------------------------------------------------

WHO_SUPPLIES = re.compile(r"(?i)\b(?:harness|assistant|host|interface)\s+(?:supplies|provides|gives"
                          r"|hands)\s+(?:you\s+)?(?:that|this|the\s+skill's)\s+directory")


def skill_directory_passage(text, manifest):
    """The second branch of the manifest resolution, collapsed, after the path it opens with."""
    collapsed = flat(text)
    opening = "2. `<this-skill-dir>/../../%s` — " % manifest
    begin = collapsed.index(opening) + len(opening)
    return collapsed[begin:collapsed.index(' 3. "Unknown"', begin)]


def passage(host):
    return skill_directory_passage(onboarding_flow(host), load_host(host).vars["manifest_path"])


class TheSkillDirectoryPassageSaysNotWhoSuppliesIt(unittest.TestCase):
    def test_it_is_the_same_in_every_package(self):
        agreed({host: passage(host) for host in HOSTS}, "the skill-directory passage")

    def test_it_keeps_the_rest(self):
        text = agreed({host: passage(host) for host in HOSTS}, "the skill-directory passage")
        for kept in ("this skill's own directory, two levels up.",
                     "it belongs to the plugin whose files are running.",
                     "the same skill-relative fallback INV-185 documents for bundled scripts."):
            self.assertIn(kept, text)

    def test_no_package_says_who_supplies_the_directory(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIsNone(WHO_SUPPLIES.search(passage(host)), passage(host))
                for path in markdown(host):
                    self.assertNotRegex(flat(read(path)), r"(?i)harness\s+supplies", path.name)

    def test_the_path_it_gives_names_a_manifest_the_package_carries(self):
        """INV-252: two levels up from a skill's directory is the manifest, in every layout."""
        for host in HOSTS:
            with self.subTest(host=host):
                manifest = skill_file(host, ONBOARDING) / ".." / ".." / load_host(host).vars["manifest_path"]
                self.assertTrue(manifest.is_file(), manifest)
                self.assertEqual(load_declaration(SOURCE_DIR)["version"],
                                 json.loads(read(manifest))["version"])

    def test_the_replaced_wording_is_reported(self):
        """Negative control."""
        old = "The harness supplies that directory at invocation, so by construction it belongs"
        self.assertIsNotNone(WHO_SUPPLIES.search(old))
        self.assertIsNone(WHO_SUPPLIES.search("That directory is the one this skill's files are read from"))


# --- 4: the model example --------------------------------------------------------------------

MODEL_LINE = re.compile(r"- \*\*Model / effort:\*\* \[[^\]]*?e\.g\. \"([^\"]*)\"[^\]]*\]")
#: The example as a placeholder and an effort level: no ID at all, so none of any assistant.
PLACEHOLDER_EXAMPLE = re.compile(r"<[^<>]+> / \w+")


def model_line(text):
    """``(the whole line, its example)`` for the feedback entry's Model / effort line."""
    match = one(list(MODEL_LINE.finditer(flat(text))), "Model / effort line")
    return match.group(0), match.group(1)


def assistant_words():
    """Every word that names an assistant or one of its models, from the profiles, lowercased.

    The assistants' names are the terms each profile lists as foreign to it. A model's name is a
    capitalized word of a profile's ``model_capable`` value; "a high-capability model" has none.
    """
    words = set()
    for host in HOSTS:
        profile = load_host(host)
        words.update(term.strip("_").lower() for term in profile.foreign_terms)
        words.update(part.lower() for part in re.findall(r"\b[A-Z][A-Za-z]{2,}",
                                                         profile.vars["model_capable"]))
    return words


def model_ids_in(example):
    """What makes ``example`` hold a model ID: an assistant's or model's name, or an ID's shape."""
    lowered = example.lower()
    found = sorted(word for word in assistant_words() if word in lowered)
    found += re.findall(r"\b[a-z]+(?:-[a-z0-9.]+)*-\d[\w.\[\]-]*", lowered)
    if not PLACEHOLDER_EXAMPLE.fullmatch(example):
        found.append("not a placeholder: %r" % example)
    return found


class TheModelExampleHoldsNoModelId(unittest.TestCase):
    def feedback(self, host):
        return read(skill_file(host, ONBOARDING + "/feedback.md"))

    def test_the_line_is_the_same_in_every_package(self):
        agreed({host: model_line(self.feedback(host))[0] for host in HOSTS}, "the Model / effort line")

    def test_the_example_holds_no_model_id(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual([], model_ids_in(model_line(self.feedback(host))[1]))

    def test_the_line_still_asks_for_the_model_id_and_the_effort_level(self):
        line = model_line(self.feedback(HOSTS[0]))[0]
        self.assertIn("[model ID and reasoning-effort level;", line)
        self.assertIn('or "Unknown"]', line)

    def test_the_profiles_name_every_assistant(self):
        """A liveness check on the word list the scan is built from."""
        words = assistant_words()
        for word in ("claude", "copilot", "kiro", "gemini", "chatgpt", "opus"):
            self.assertIn(word, words)

    def test_a_model_id_is_reported(self):
        """Negative control: the example #30 replaced, and one of another shape."""
        for example in ("claude-opus-5-5[1m] / high", "gpt-5 / high", "Opus 5.5 / high",
                        "gemini-3-pro / medium", "some-model-7 / high", "x / high"):
            with self.subTest(example=example):
                self.assertTrue(model_ids_in(example), example)


# --- 5: where the recap generator is ---------------------------------------------------------

GENERATOR = "generate_recap_pdf.py"
LIVES_AT = re.compile(r"\(this skill lives at `([^`]+)`, so the generator is in `([^`]+)`, "
                      r"counted from there\):")
FALLBACK_COMMAND = re.compile(r"python3 <this-skill-dir>/(\S+)/" + re.escape(GENERATOR))


def graduation(host):
    return read(skill_file(host, "graduation/SKILL.md"))


def generator_problems(root, text):
    """Where the graduation passage and the package at ``root`` disagree about the generator."""
    stated = LIVES_AT.findall(flat(text))
    if len(stated) != 1:
        return ["the passage states the generator's place %d times" % len(stated)]
    skill, relative = stated[0]
    problems = []
    home = Path(root) / skill
    if not (home / "SKILL.md").is_file():
        problems.append("%s holds no SKILL.md" % skill)
    target = (home / relative).resolve()
    if not (target / GENERATOR).is_file():
        problems.append("%s, counted from %s, holds no %s" % (relative, skill, GENERATOR))
    commands = FALLBACK_COMMAND.findall(flat(text))
    if len(commands) != 1:
        problems.append("the fallback command is given %d times" % len(commands))
    elif (home / commands[0]).resolve() != target:
        problems.append("the command names %s and the passage %s" % (commands[0], relative))
    return problems


class TheGraduationPassageNamesWhereTheGeneratorIs(unittest.TestCase):
    def test_the_stated_path_holds_the_generator_in_every_package(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual([], generator_problems(built(host), graduation(host)))

    def test_it_is_the_one_generator_the_package_carries(self):
        for host in HOSTS:
            with self.subTest(host=host):
                skill, relative = one(LIVES_AT.findall(flat(graduation(host))), "passage")
                carried = one(sorted(built(host).rglob(GENERATOR)), GENERATOR)
                self.assertEqual(carried.resolve(),
                                 (built(host) / skill / relative / GENERATOR).resolve())
                self.assertEqual(load_host(host).vars["scripts_relative"] + "/", relative)

    def test_the_packages_do_not_all_keep_their_scripts_in_one_place(self):
        """Or one literal path would pass in every package."""
        places = {one(LIVES_AT.findall(flat(graduation(host))), "passage")[1] for host in HOSTS}
        self.assertGreater(len(places), 1, places)

    def test_no_package_says_two_levels_up_under_scripts(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertNotIn("two levels up under `scripts/`", flat(graduation(host)))

    def test_another_packages_layout_is_reported(self):
        """Negative control: each package's passage, read against a package laid out differently."""
        stated = {host: one(LIVES_AT.findall(flat(graduation(host))), "passage")[1] for host in HOSTS}
        pairs = [(host, other) for host in HOSTS for other in HOSTS if stated[host] != stated[other]]
        self.assertTrue(pairs)
        for host, other in pairs:
            with self.subTest(text=host, package=other):
                self.assertTrue(generator_problems(built(other), graduation(host)))


# --- 6: the handle that is not a pid ---------------------------------------------------------

REFERENCE = "module-03b-truthset-visualization/visualization-api-reference.md"
BACKGROUND_TASK = re.compile(r"(?i)background[\s-]*tasks?")
WARNING_SAYS = (
    ("the id is not a pid", r"\*\*A handle that names a task rather than a process is not a pid\.\*\*"),
    ("the id names a task, not a process", r"the id it returns names a task, not a process"),
    ("no pid is recorded from it", r"record no pid from it"),
    ("the pid comes from the port lookup",
     r"take the pid from the launch confirmation's port lookup"),
    ("what holds when the lookup names no single listener",
     r"the checkpoint keeps no pid and teardown's missing-pid fallback applies"),
)


def handle_warning(text):
    """The one paragraph that warns about a handle that is not a pid, collapsed."""
    paragraphs = [flat(block) for block in re.split(r"\n\s*\n", text)
                  if "record no pid from it" in flat(block)]
    return one(paragraphs, "handle warning")


def warning_problems(paragraph):
    problems = [name for name, pattern in WARNING_SAYS if not re.search(pattern, paragraph)]
    if BACKGROUND_TASK.search(paragraph):
        problems.append("names a background-task feature")
    return problems


class TheHandleWarningNamesNoAssistantFeature(unittest.TestCase):
    def warning(self, host):
        return handle_warning(read(skill_file(host, REFERENCE)))

    def test_it_is_in_every_package_and_says_what_it_must(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual([], warning_problems(self.warning(host)))

    def test_it_is_the_same_in_every_package(self):
        agreed({host: self.warning(host) for host in HOSTS}, "the handle warning")

    def test_the_reference_names_no_background_task_anywhere(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIsNone(BACKGROUND_TASK.search(flat(read(skill_file(host, REFERENCE)))))

    def test_it_names_no_assistant(self):
        lowered = self.warning(HOSTS[0]).lower()
        self.assertEqual([], sorted(word for word in assistant_words() if word in lowered))

    def test_it_sits_in_the_launch_confirmation(self):
        text = read(skill_file(HOSTS[0], REFERENCE))
        begin = text.index('<a id="launch-confirmation"></a>')
        end = text.index("Never identify the server by matching its command line", begin)
        self.assertIn(self.warning(HOSTS[0]), flat(text[begin:end]))

    def test_the_replaced_wording_and_an_inverted_one_are_reported(self):
        """Negative controls."""
        old = ("⚠️ **A handle from the host's own background-task mechanism is not a pid.** When "
               "the server is started through the guide's own background-task feature rather than "
               "with `&` in a shell, the id that feature returns names a task, not a process: "
               "record no pid from it, and take the pid from the launch confirmation's port "
               "lookup. Where that lookup names no single listener, the checkpoint keeps no pid "
               "and teardown's missing-pid fallback applies.")
        self.assertIn("names a background-task feature", warning_problems(old))
        current = self.warning(HOSTS[0])
        self.assertIn("the id is not a pid",
                      warning_problems(current.replace("is not a pid", "is a pid")))
        self.assertIn("no pid is recorded from it",
                      warning_problems(current.replace("record no pid", "record the pid")))
        self.assertIn("the pid comes from the port lookup",
                      warning_problems(current.replace("port lookup", "ready line")))
        self.assertIn("names a background-task feature",
                      warning_problems(current + " (a background task)"))


# --- the check, on the real tree -------------------------------------------------------------

NEUTRALITY = REPO_ROOT / "tools" / "bootcamp_build" / "neutrality.json"


def as_build(host, root):
    """``root`` as the build's own record of a package, which is what `residue` reads."""
    files = sorted(path.relative_to(root).as_posix() for path in Path(root).rglob("*")
                   if path.is_file())
    return HostBuild(host=host, root=Path(root), files=files)


class TheCheckIgnoresCaseOnTheRealTree(unittest.TestCase):
    """`tools.bootcamp_build check` with the ceilings #30 found and left as they were."""

    @classmethod
    def setUpClass(cls):
        cls.hosts = [load_host(host) for host in HOSTS]
        cls.findings = {host.id: residue(as_build(host, built(host.id))) for host in cls.hosts}

    def test_the_ceilings_are_the_ones_recorded_before_the_check_ignored_case(self):
        recorded = json.loads(read(NEUTRALITY))
        self.assertEqual(0, recorded["source"])
        self.assertEqual({host: (0 if host == "claude" else 1) for host in HOSTS}, recorded["hosts"])

    def test_the_source_names_no_assistant_in_any_letter_case(self):
        self.assertEqual([], [str(finding) for finding in lint_source(SOURCE_DIR, self.hosts)])

    def test_each_package_is_at_its_ceiling(self):
        recorded = json.loads(read(NEUTRALITY))["hosts"]
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual(recorded[host], len(self.findings[host]),
                                 [str(finding) for finding in self.findings[host]])

    def test_the_one_allowed_reference_is_the_adapters_project_directory_variable(self):
        allowed = [finding for host in HOSTS for finding in self.findings[host]]
        self.assertTrue(allowed, "no package holds the reference the ceilings allow")
        for finding in allowed:
            with self.subTest(path=finding.path):
                self.assertEqual("hook_adapter.py", Path(finding.path).name)
                self.assertIn("CLAUDE_PROJECT_DIR", finding.text)

    def test_a_lowercase_name_added_to_a_real_package_file_is_reported(self):
        """Negative control, on the file the model ID sat in: a copy of it, with one line added."""
        planted = 0
        for host in self.hosts:
            if not host.foreign_terms:
                continue
            term = host.foreign_terms[0].strip("_").lower()
            with self.subTest(host=host.id, term=term), tempfile.TemporaryDirectory() as scratch:
                copy = Path(scratch) / "feedback.md"
                shutil.copyfile(skill_file(host.id, ONBOARDING + "/feedback.md"), copy)
                self.assertEqual([], residue(as_build(host, scratch)))
                copy.write_bytes(copy.read_bytes()
                                 + ('\ne.g. "%s-model-1 / high"\n' % term).encode("utf-8"))
                self.assertEqual([term], [finding.term for finding in residue(as_build(host, scratch))])
                planted += 1
        self.assertGreaterEqual(planted, len(HOSTS))


if __name__ == "__main__":
    unittest.main()
