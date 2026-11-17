"""The model notes and every assistant's site tips name no mid-bootcamp switch (#4).

Two places outside the skills told a reader that the bootcamp would ask for a model or
effort change along the way: the maintainer notes in `docs/model-selection.md` (a page in this
repository that no package carries, #12), and
the "Model and effort" tip on each assistant's install page
(`hosts/<assistant>/fragments/site-tips.html`). Issue #4 removed the request, so both now
say what the welcome says: one model is fine for the whole bootcamp, and the bootcamp never
asks for a change. A page that still promised a switch would describe a bootcamp that no
longer exists.

What must hold:

1. Each assistant's tip states the one-model rule, names that assistant's capable-tier model
   and says the bootcamp never asks for a switch.
2. No tip and no install fragment says the bootcamp suggests, recommends or announces a
   model or effort change at a module start, or tells the reader how to make one mid-way.
3. `model-selection.md` states the same rule, names no switch and no command that sets the
   model or the effort, and keeps one derived copy of the working-depth table.
4. The Claude install walkthrough starts the reader on the model the welcome names.

Issue #13 added what an install page (`hosts/<assistant>/fragments/site-install.html`) may say
about the model and the effort. On ChatGPT the page named one model and the welcome another,
and two of the five pages set an effort that the bootcamp never mentions again.

- ⛔ **(INV-428) An install page that names a model takes the name from `{{host.model_capable}}`, the value the welcome is built from.**
  It spells that value nowhere as literal text. A page that names no model passes.
- ⛔ **(INV-428) The model ID in the Claude CLI start command is the one derived from Claude's `model_capable`.**
  Lowercase, each space and dot a hyphen, `claude-` in front: "Opus 5.5" gives
  `claude-opus-5-5`. The ID stays literal in the fragment, and the command carries no flag
  but `--model` and `--permission-mode auto`.
- ⛔ **(INV-429) No install page mentions an effort.**
  The bootcamper runs at their assistant's default effort, and the pages say nothing about it.

⚠️ **Choosing a model once, before the bootcamp starts, is not a switch.** The install
fragments that name a model to start on are not reported for that.

HTML is read as visible text: tags removed and whitespace collapsed, so a re-wrapped
paragraph still matches. An install fragment is read twice: as written, to see where the
model's name comes from, and as the build renders it, to see what a reader gets. The render is
`substitute_tokens`, the function the build calls on a fragment.

Enforces **INV-428** (registered 2026-11-16): the two model rules above. The effort rule
below them is a separate subject and is not part of INV-428.

Enforces **INV-429** (registered 2026-11-16): the effort rule. It searches each fragment's
visible text for the word "effort"; it does not recognize a level named without that word,
and it does not read the shared page template `site/_install.html`.

⚠️ **What the #13 checks cannot establish:** that a `model_capable` value names a model the
assistant offers, or that a model ID exists. They do not report a page that names a second
model beside the token, or a model named without the word "model" and without the token.

Run:  python3 -m unittest discover -s tests
"""
import dataclasses
import html
import re
import unittest

from _built import REPO_ROOT, load_host
from _model_effort import (HOSTS, ONBOARDING_FLOW, capable_model, depth_block, depth_instructions,
                           depth_rows, flat, skill_text)
from tools.bootcamp_build.render import substitute_tokens  # noqa: E402

HOSTS_DIR = REPO_ROOT / "hosts"
MODEL_SELECTION = REPO_ROOT / "docs" / "model-selection.md"

RULE = "One model is fine for the whole bootcamp."
NEVER = "The bootcamp never asks you to switch models or change settings along the way."

#: Wording that describes a model or effort change made during the bootcamp.
MID_BOOTCAMP_SWITCH = re.compile(
    r"(?i)at the start of each module"
    r"|\b(?:tells you when|may suggest|suggests|recommends)\b"
    r"|\bswitch(?:es|ing)? (?:to|up|down|back|mid|the session)\b"
    r"|\bmid-(?:session|bootcamp|module)\b"
    r"|\bonly you can change\b"
    r"|\badapts its model\b"
    r"|(?<![\w./-])/(?:model|effort)(?![\w-])")


#: The token an install fragment takes its model from: the value the welcome is built from.
MODEL_TOKEN = "{{host.model_capable}}"
#: The word that makes an install page one that names a model.
MODEL_WORD = re.compile(r"(?i)\bmodels?\b")
#: Any mention of an effort, a flag included (`--effort`).
EFFORT_WORD = re.compile(r"(?i)\befforts?\b")
#: The Claude CLI start command, as the fragment's command block holds it.
CLI_START = re.compile(r"<code>(claude --model [^<]*)</code>")
#: The fewest characters of visible text an install page is taken to have.
INSTALL_TEXT_FLOOR = 200


def visible_text(markup):
    """HTML as a reader sees it: tags removed, entities decoded, whitespace collapsed."""
    return flat(html.unescape(re.sub(r"<[^>]+>", " ", markup)))


def visible(path):
    """An HTML fragment's text as a reader sees it."""
    return visible_text(path.read_text(encoding="utf-8"))


def install_source(host):
    """``host``'s install fragment as written, tokens and all."""
    return (HOSTS_DIR / host / "fragments" / "site-install.html").read_text(encoding="utf-8")


def with_model(host, model):
    """``host``'s profile with ``model`` as its ``model_capable`` value."""
    profile = load_host(host)
    return dataclasses.replace(profile, vars=dict(profile.vars, model_capable=model))


def rendered(source, profile):
    """An install fragment's visible text once the build has put ``profile``'s values in."""
    return visible_text(substitute_tokens(source, profile, "site-install.html"))


def names_a_model(source):
    """True when an install fragment names a model: it says "model", or it uses the token."""
    return bool(MODEL_WORD.search(visible_text(source))) or MODEL_TOKEN in source


def model_problems(source, profile):
    """What is wrong with how an install fragment names its model; empty when nothing is.

    ``profile`` is the assistant's host profile, whose ``model_capable`` the welcome states.
    A fragment that names no model has nothing to get wrong.
    """
    if not names_a_model(source):
        return []
    model = profile.vars["model_capable"]
    problems = []
    if MODEL_TOKEN not in source:
        problems.append("mentions a model and does not take its name from %s" % MODEL_TOKEN)
    if model in source or model in visible_text(source):
        problems.append("spells %r as literal text" % model)
    if model not in rendered(source, profile):
        problems.append("its rendered text does not name %r, the welcome's model" % model)
    return problems


def model_id(name):
    """The Claude model ID for a display name: "Opus 5.5" gives ``claude-opus-5-5``."""
    return "claude-" + re.sub(r"[ .]", "-", name.lower())


def cli_command(model):
    """The Claude CLI start command for the model the welcome names."""
    return "claude --model %s --permission-mode auto" % model_id(model)


def cli_problems(source, model):
    """What is wrong with the Claude CLI start command in ``source``; empty when nothing is."""
    found = CLI_START.findall(source)
    if not found:
        return ["no `claude --model` command was found"]
    return ["%r should be %r" % (command, cli_command(model))
            for command in found if command != cli_command(model)]


def effort_mentions(text):
    """Each mention of an effort in ``text``, with the words around it."""
    return [text[max(0, m.start() - 30):m.end() + 30] for m in EFFORT_WORD.finditer(text)]


def tip(host):
    """The text of ``host``'s model tip: the block with ``id="model"``."""
    text = (HOSTS_DIR / host / "fragments" / "site-tips.html").read_text(encoding="utf-8")
    match = re.search(r'<div class="tip" id="model">(.*?)</div>', text, re.S)
    return flat(html.unescape(re.sub(r"<[^>]+>", " ", match.group(1)))) if match else None


class EveryAssistantsTipStatesTheOneModelRule(unittest.TestCase):
    def test_every_assistant_has_the_tip(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIsNotNone(tip(host), "site-tips.html has no tip with id=\"model\"")

    def test_it_states_the_rule_and_that_nothing_is_asked(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIn(RULE, tip(host))
                self.assertIn(NEVER, tip(host))

    def test_it_names_that_assistants_capable_model(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertIn(capable_model(host).lower() + " suits it well", tip(host).lower())

    def test_it_is_headed_for_the_model_alone(self):
        """Sentence case, and no effort setting to look for."""
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertTrue(tip(host).startswith("Model " + RULE), tip(host)[:60])


class NoSitePageNamesAMidBootcampSwitch(unittest.TestCase):
    def fragments(self):
        return sorted(HOSTS_DIR.glob("*/fragments/site-*.html"))

    def test_the_fragments_are_found(self):
        self.assertGreaterEqual(len(self.fragments()), 3 * len(HOSTS))

    def test_no_fragment_names_one(self):
        for path in self.fragments():
            with self.subTest(path=path.relative_to(REPO_ROOT).as_posix()):
                found = [m.group(0) for m in MID_BOOTCAMP_SWITCH.finditer(visible(path))]
                self.assertEqual([], found)

    def test_the_wording_each_tip_used_to_carry_is_reported(self):
        """Negative controls (INV-265): the five sentences issue #4 removed."""
        for retired in (
                "At the start of each module the bootcamp tells you when to switch to Opus 5.5.",
                "The bootcamp suggests a model and effort at the start of each module, and only "
                "you can change the setting.",
                "At the start of each module the bootcamp may suggest a more capable model.",
                "it adapts its model and effort guidance to the interface you are in",
                "Switch mid-session with /model claude-opus-5-5",
        ):
            with self.subTest(retired=retired[:40]):
                self.assertTrue(MID_BOOTCAMP_SWITCH.search(retired))

    def test_the_new_wording_and_an_install_time_choice_are_not(self):
        for kept in (RULE + " Opus 5.5 suits it well. " + NEVER,
                     "Choose the Model Opus 5.5.",
                     "claude --model claude-opus-5-5 --permission-mode auto",
                     "On the bottom, set the mode and model:",
                     "In the lower right of Codex, select the model:"):
            with self.subTest(kept=kept[:40]):
                self.assertIsNone(MID_BOOTCAMP_SWITCH.search(kept))

    def test_the_claude_walkthrough_starts_on_the_model_the_welcome_names(self):
        """Read as rendered (#13): the fragment as written holds the token, not the name."""
        text = rendered(install_source("claude"), load_host("claude"))
        self.assertIn("Choose the Model %s ." % capable_model("claude"), text)
        self.assertIn("claude --model claude-opus-5-5 ", text)
        self.assertNotIn("Sonnet", text)


class EveryInstallPageNamesTheWelcomesModel(unittest.TestCase):
    """#13: one value, ``model_capable``, names the model in the welcome and on the install page."""

    def naming(self):
        return [host for host in HOSTS if names_a_model(install_source(host))]

    def test_every_assistant_has_an_install_page_with_text(self):
        self.assertGreaterEqual(len(HOSTS), 5)
        for host in HOSTS:
            with self.subTest(host=host):
                text = visible_text(install_source(host))
                self.assertGreaterEqual(len(text), INSTALL_TEXT_FLOOR)

    def test_a_page_that_names_a_model_takes_it_from_the_welcomes_value(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual([], model_problems(install_source(host), load_host(host)))

    def test_the_claude_and_chatgpt_pages_do_name_one(self):
        """INV-265: five pages that name no model would agree with any welcome."""
        for host in ("chatgpt", "claude"):
            with self.subTest(host=host):
                self.assertIn(host, self.naming())

    def test_the_page_and_the_built_welcome_name_the_same_model(self):
        """Both sides are read: the page as rendered, the welcome from the built package."""
        for host in self.naming():
            model = capable_model(host)
            with self.subTest(host=host):
                self.assertIn(model, rendered(install_source(host), load_host(host)))
                self.assertIn("%s suits it well" % model, flat(skill_text(host, ONBOARDING_FLOW)))

    def test_each_step_that_names_the_model_renders_it(self):
        """The Claude Desktop step, the Claude CLI sentence and the ChatGPT step."""
        claude = rendered(install_source("claude"), load_host("claude"))
        self.assertIn("Choose the Model %s ." % capable_model("claude"), claude)
        self.assertIn("Start the Claude Code CLI on %s , with" % capable_model("claude"), claude)
        chatgpt = rendered(install_source("chatgpt"), load_host("chatgpt"))
        self.assertIn("Choose the model %s ." % capable_model("chatgpt"), chatgpt)

    def test_the_chatgpt_welcome_and_tip_name_the_model_the_page_named(self):
        """#13 moved the name the install page already carried into ``model_capable``."""
        self.assertEqual("GPT-5.6 Terra", capable_model("chatgpt"))
        self.assertIn("GPT-5.6 Terra suits it well", flat(skill_text("chatgpt", ONBOARDING_FLOW)))
        self.assertIn("GPT-5.6 Terra suits it well.", tip("chatgpt"))

    def test_the_retired_chatgpt_pairing_is_reported(self):
        """Negative control: the page said "GPT-5.6 Terra", the welcome a "Codex model"."""
        page = install_source("chatgpt").replace(MODEL_TOKEN, "GPT-5.6 Terra")
        self.assertNotEqual(install_source("chatgpt"), page, "the control changed nothing")
        self.assertEqual(
            ["mentions a model and does not take its name from {{host.model_capable}}",
             "its rendered text does not name 'a high-capability Codex model', "
             "the welcome's model"],
            model_problems(page, with_model("chatgpt", "a high-capability Codex model")))

    def test_a_model_spelled_out_on_the_page_is_reported(self):
        """Negative controls: the welcome's own value as literal text, in every place or in one."""
        for host in ("chatgpt", "claude"):
            model, source = capable_model(host), install_source(host)
            with self.subTest(host=host, replaced="every token"):
                self.assertEqual(
                    ["mentions a model and does not take its name from {{host.model_capable}}",
                     "spells %r as literal text" % model],
                    model_problems(source.replace(MODEL_TOKEN, model), load_host(host)))
            with self.subTest(host=host, replaced="one token"):
                self.assertEqual(
                    ["spells %r as literal text" % model],
                    model_problems(source.replace(MODEL_TOKEN, model, 1) + MODEL_TOKEN + "\n",
                                   load_host(host)))

    def test_a_page_that_names_no_model_passes(self):
        """Its welcome names one all the same; the page is not asked to."""
        page = ("<ol><li>Install the extension.</li>"
                "<li>Enter <code>Start the bootcamp</code>.</li></ol>\n")
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual([], model_problems(page, load_host(host)))


class TheClaudeCliCommandNamesTheWelcomesModel(unittest.TestCase):
    """#13: the model ID is a second spelling of ``model_capable``, held to it here."""

    def test_the_id_is_derived_from_the_display_name(self):
        self.assertEqual("claude-opus-5-5", model_id("Opus 5.5"))
        self.assertEqual("claude --model claude-opus-5-5 --permission-mode auto",
                         cli_command("Opus 5.5"))

    def test_the_command_names_the_id_of_the_welcomes_model(self):
        source = install_source("claude")
        self.assertEqual([cli_command(capable_model("claude"))], CLI_START.findall(source))
        self.assertEqual([], cli_problems(source, capable_model("claude")))

    def test_a_command_on_another_model_or_with_another_flag_is_reported(self):
        """Negative controls: a stale ID, the removed `--effort medium`, a moved `model_capable`."""
        model, source = capable_model("claude"), install_source("claude")
        current = cli_command(model)
        for retired in ("claude --model claude-opus-5 --permission-mode auto",
                        current.replace(" --permission", " --effort medium --permission")):
            with self.subTest(retired=retired):
                changed = source.replace(current, retired)
                self.assertNotEqual(source, changed, "the control changed nothing")
                self.assertEqual(["%r should be %r" % (retired, current)],
                                 cli_problems(changed, model))
        self.assertEqual(["%r should be %r" % (current, cli_command("Opus 6"))],
                         cli_problems(source, "Opus 6"))

    def test_a_page_with_no_command_is_reported(self):
        """INV-265: no command found is a failure, not a command that agrees."""
        self.assertEqual(["no `claude --model` command was found"],
                         cli_problems(install_source("chatgpt"), capable_model("claude")))


class NoInstallPageMentionsAnEffort(unittest.TestCase):
    """#13: effort is left to the assistant, and no install page sets or names one."""

    #: The six places issue #13 removed an effort from, as they were written.
    REMOVED = (
        "On the bottom, set the mode, model and effort:",
        "<li>Choose the Effort <strong>medium</strong>.</li>",
        "Start the Claude Code CLI on <strong>Opus 5.5</strong> at medium effort, with",
        "<code>claude --model claude-opus-5-5 --effort medium --permission-mode auto</code>",
        "In the lower right of Codex, select the model and effort:",
        "<li>Choose the effort <strong>Medium</strong>.</li>",
    )
    #: What stands in their place.
    KEPT = (
        "On the bottom, set the mode and model:",
        "Start the Claude Code CLI on <strong>Opus 5.5</strong>, with",
        "<code>claude --model claude-opus-5-5 --permission-mode auto</code>",
        "In the lower right of Codex, select the model:",
        "Install it effortlessly.",
    )

    def test_no_page_mentions_one(self):
        self.assertGreaterEqual(len(HOSTS), 5)
        for host in HOSTS:
            with self.subTest(host=host):
                text = rendered(install_source(host), load_host(host))
                self.assertGreaterEqual(len(text), INSTALL_TEXT_FLOOR)
                self.assertEqual([], effort_mentions(text))

    def test_each_removed_line_is_reported(self):
        """Negative controls: one for each removed mention."""
        for removed in self.REMOVED:
            with self.subTest(removed=removed[:45]):
                self.assertEqual(1, len(effort_mentions(visible_text(removed))))

    def test_the_lines_that_replaced_them_are_not(self):
        for kept in self.KEPT:
            with self.subTest(kept=kept[:45]):
                self.assertEqual([], effort_mentions(visible_text(kept)))

    def test_an_effort_put_back_on_a_page_is_reported(self):
        """Negative control on the real pages: the ChatGPT step and the Claude flag."""
        for host, old, new in (
                ("chatgpt", "select the model:", "select the model and effort:"),
                ("claude", " --permission-mode auto</code>",
                 " --effort medium --permission-mode auto</code>")):
            with self.subTest(host=host):
                source = install_source(host)
                changed = source.replace(old, new)
                self.assertNotEqual(source, changed, "the control changed nothing")
                self.assertEqual(1, len(effort_mentions(rendered(changed, load_host(host)))))


class TheMaintainerNotesDescribeTheSameBehavior(unittest.TestCase):
    def setUp(self):
        self.raw = MODEL_SELECTION.read_text(encoding="utf-8")
        self.text = flat(self.raw)

    def test_they_state_the_rule(self):
        self.assertIn("the bootcamp handles this itself", self.text)
        self.assertIn("One model is fine for the whole bootcamp, the bootcamper is never asked to "
                      "change the model or the reasoning effort", self.text)
        self.assertIn("how carefully the guide works at each stage is set by instruction alone",
                      self.text)

    def test_they_name_no_mid_bootcamp_switch(self):
        found = [m.group(0) for m in MID_BOOTCAMP_SWITCH.finditer(self.text)]
        self.assertEqual([], found)
        self.assertNotRegex(self.text, r"(?i)switch question|done modifying|the nudge\b")

    def test_they_say_why_a_skill_setting_does_not_fit(self):
        self.assertIn("**Skill frontmatter is turn-scoped.**", self.text)
        self.assertIn("A bootcamp module is loaded once and then runs for many turns", self.text)

    def test_their_table_and_instructions_are_the_ground_rules_copy(self):
        rules = depth_block(skill_text("claude", "bootcamp-onboarding/ground-rules.md"))
        start = self.raw.index("| Stage | Effort |")
        notes = self.raw[start:self.raw.index("**One row per stage", start)]
        self.assertEqual(depth_rows(rules), depth_rows(notes))
        self.assertEqual(depth_instructions(rules), depth_instructions(notes))


if __name__ == "__main__":
    unittest.main()
