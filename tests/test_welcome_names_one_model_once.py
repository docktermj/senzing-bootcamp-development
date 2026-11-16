"""The welcome names one suitable model, once, as a statement (#4).

Issue #4 replaced the per-module model recommendation with one opening statement: the
welcome's overview names the assistant's capable-tier model as suitable for the whole
bootcamp and says the bootcamp never asks for a change along the way. This file replaces
`test_model_nudge_trigger_direction.py`, which pinned when the retired question fired.

What must hold in every assistant's built package:

1. **It is there, and it names that assistant's model.** The overview holds one bullet that
   states the assistant's `model_capable` value (`hosts/<assistant>/host.json`).
2. **It is said once.** The model is named once in the welcome and nowhere else in the
   skills the guide reads, so no module can restate it.
3. **It is a statement.** The bullet holds no 👉, the welcome's only 👉 is the "any
   questions" question that follows the overview, and the flow says not to pause on it.
4. **Nothing follows it up.** The flow says to say nothing further to a bootcamper on a
   different model.

⚠️ **What this cannot establish:** that a live welcome shows the bullet once. Under the
`minimal` verbosity preset the overview is cut to two bullets (INV-214), which a resumed or
pre-seeded run can reach; a fresh bootcamp has no preset and shows every bullet.

Reads collapsed text (`flat`), so a re-wrapped bullet still matches.

Run:  python3 -m unittest discover -s tests

Enforces **INV-426** (registered 2026-11-16). It establishes what each package's text says; it
does not establish that a live turn obeys it, which only `dry-run` phase 3 can observe.
"""
import re
import unittest

from _built import REPO_ROOT
from _model_effort import HOSTS, ONBOARDING_FLOW, capable_model, flat, skill_text, skills_dir

#: The overview: from the "give the overview" line to the commentary that closes its list.
OVERVIEW_START = "Then give the overview (cover naturally, do not ask a question yet)."
OVERVIEW_END = "**The note bullet is verbosity-aware"
#: Step 3, the welcome, up to the step that asks the first question.
WELCOME_START = "## 3. Welcome and overview"
WELCOME_END = "## 4. Any questions"


def between(text, start, end):
    begin = text.index(start)
    return text[begin:text.index(end, begin)]


def bullets(overview):
    """The overview's top-level bullets, each collapsed to one line."""
    return [flat(item) for item in re.split(r"(?m)^(?=- )", overview) if item.startswith("- ")]


def statement(host):
    """The bullet ``host``'s welcome is expected to hold."""
    return ("- One model is fine for the whole bootcamp: %s suits it well, and the bootcamp "
            "never asks you to switch models or change settings along the way."
            % capable_model(host))


class TheWelcomeNamesTheCapableModel(unittest.TestCase):
    def test_every_assistant_has_a_capable_model_to_name(self):
        names = {host: capable_model(host) for host in HOSTS}
        for host, name in names.items():
            with self.subTest(host=host):
                self.assertTrue(name.strip(), "host.json gives no model_capable")

    def test_the_overview_holds_the_statement(self):
        for host in HOSTS:
            with self.subTest(host=host):
                overview = between(skill_text(host, ONBOARDING_FLOW), OVERVIEW_START, OVERVIEW_END)
                self.assertEqual(1, bullets(overview).count(statement(host)),
                                 "the welcome's overview does not hold the one-model "
                                 "statement naming %r exactly once" % capable_model(host))

    def test_the_source_uses_the_token_once(self):
        source = (REPO_ROOT / "source" / "skills" / ONBOARDING_FLOW).read_text(encoding="utf-8")
        self.assertEqual(1, source.count("{{host.model_capable}}"))
        self.assertNotRegex(source, r"\{\{host\.model_(?!capable\}\})")


class ItIsSaidOnce(unittest.TestCase):
    def test_the_welcome_names_the_model_once(self):
        for host in HOSTS:
            with self.subTest(host=host):
                welcome = flat(between(skill_text(host, ONBOARDING_FLOW), WELCOME_START, WELCOME_END))
                self.assertEqual(1, welcome.count(capable_model(host)))

    def test_no_other_skill_file_names_it(self):
        """Not a module start, not graduation: nowhere else the guide reads."""
        for host in HOSTS:
            name = capable_model(host)
            found = {}
            for path in sorted(skills_dir(host).rglob("*.md")):
                count = flat(path.read_text(encoding="utf-8")).count(name)
                if count:
                    found[path.relative_to(skills_dir(host)).as_posix()] = count
            with self.subTest(host=host):
                self.assertEqual({ONBOARDING_FLOW: 1}, found)

    def test_no_source_file_uses_the_token_but_the_welcome(self):
        using = sorted(path.relative_to(REPO_ROOT).as_posix()
                       for path in (REPO_ROOT / "source").rglob("*")
                       if path.is_file() and path.suffix in (".md", ".py", ".json")
                       and "{{host.model_" in path.read_text(encoding="utf-8"))
        self.assertEqual(["source/skills/" + ONBOARDING_FLOW], using)


class ItIsAStatement(unittest.TestCase):
    def test_the_bullet_holds_no_pointer(self):
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertNotIn("👉", statement(host))
                overview = between(skill_text(host, ONBOARDING_FLOW), OVERVIEW_START, OVERVIEW_END)
                self.assertNotIn("👉", overview, "the overview asks a question")

    def test_the_first_question_comes_after_the_welcome(self):
        for host in HOSTS:
            with self.subTest(host=host):
                text = skill_text(host, ONBOARDING_FLOW)
                asked = re.search(r"(?m)^👉 \*\*", text)
                self.assertIsNotNone(asked)
                self.assertGreater(asked.start(), text.index(WELCOME_END))
                self.assertIn("👉 **Do you have any questions before we get started?**",
                              text[asked.start():asked.start() + 80])

    def test_the_flow_says_it_is_a_statement_said_once(self):
        for host in HOSTS:
            with self.subTest(host=host):
                welcome = flat(between(skill_text(host, ONBOARDING_FLOW), WELCOME_START, WELCOME_END))
                self.assertIn("⛔ **(INV-426) The model bullet is a statement, said once.** Never pose it as "
                              "a 👉 question, never pause on it, and never follow it up", welcome)


class NothingFollowsItUp(unittest.TestCase):
    def test_a_bootcamper_on_a_different_model_hears_nothing_further(self):
        for host in HOSTS:
            with self.subTest(host=host):
                welcome = flat(between(skill_text(host, ONBOARDING_FLOW), WELCOME_START, WELCOME_END))
                self.assertIn("when the bootcamper is on a different model, say nothing further, "
                              "here or later", welcome)

    def test_the_ground_rules_say_the_same(self):
        for host in HOSTS:
            with self.subTest(host=host):
                rules = flat(skill_text(host, "bootcamp-onboarding/ground-rules.md"))
                self.assertIn("The welcome names one suitable model, once (`onboarding-flow.md` "
                              "step 3), and nothing is said about it afterwards, whatever the "
                              "bootcamper is running.", rules)


class TheChecksAreNotVacuous(unittest.TestCase):
    """Negative controls (INV-265), on the shipped welcome with one change made."""

    def setUp(self):
        self.text = skill_text("claude", ONBOARDING_FLOW)
        self.name = capable_model("claude")

    def test_a_second_statement_is_counted(self):
        overview = between(self.text, OVERVIEW_START, OVERVIEW_END)
        bullet = [item for item in re.split(r"(?m)^(?=- )", overview) if self.name in item][0]
        self.assertEqual(2, bullets(overview.replace(bullet, bullet + bullet)).count(statement("claude")))

    def test_a_missing_statement_is_counted(self):
        overview = between(self.text, OVERVIEW_START, OVERVIEW_END).replace(self.name, "a model")
        self.assertEqual(0, bullets(overview).count(statement("claude")))

    def test_a_re_wrapped_statement_still_matches(self):
        overview = between(self.text, OVERVIEW_START, OVERVIEW_END).replace(
            "suits it well, and", "suits it\n  well, and")
        self.assertEqual(1, bullets(overview).count(statement("claude")))


if __name__ == "__main__":
    unittest.main()
