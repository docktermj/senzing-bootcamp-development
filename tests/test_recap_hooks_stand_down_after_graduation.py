"""Once the bootcamp is complete, the recap hooks stand down, and session end still stops
the bootcamp's containers.

Issue #32. Graduation ends the bootcamp by writing `bootcamp_complete: true`, and the progress
file still records a module afterwards (`current_module: "graduation"`, or the last module on
a project graduated before graduation wrote the progress file). Three hooks tested only
`recap_checkpoint.bootcamp_active()`, which that recorded module satisfies, so on a finished
project:

- `checkpoint-tick.py` recreated `docs/progress/recap_checkpoint.md` on the next prompt and
  told the guide to keep it current;
- `precompact-recap.py` printed "A Senzing bootcamp is in progress.";
- `session-end.py` and `precompact-recap.py` went on folding a checkpoint graduation had
  already folded and cleared.

What changed, and what this file asserts:

- **The stand-down.** `checkpoint-tick.py` and `precompact-recap.py` stop once
  `module_start_apparatus.bootcamp_complete()` is true: they write no file, print nothing on
  stdout or stderr and exit 0. `checkpoint-tick.py` stands down whole (no scaffold, no
  announcement, no missing-record reminder) and still reads its stdin to the end first.
- **Only the fold, at session end.** `session-end.py` skips the fold and nothing else: it still
  stops each container the progress file records, under the gate it had, `bootcamp_active()`.
  Graduation records completion before its own session ends, so a stop gated on completion
  would leave that session's containers running (INV-101).
- **Either file.** Each case runs with the flag in the progress file, with the flag only in
  the preferences while the progress file still records a module, and with both.
- **In progress, unchanged.** Each silent case has a twin on a project that is in progress and
  not complete, where the same hook does what it did before: the scaffold and its
  announcement, the fold and its reminder, the fold and the stop.
- **One check, in each hook.** Each of the three calls `bootcamp_complete()` itself.
  `recap_checkpoint.bootcamp_active()` is not changed and does not read the flag (INV-227).
- **No list of callers.** `module_start_apparatus.py` and `bootcamp-onboarding/SKILL.md` step 2
  point at the one implementation and name no hook that calls it. Both lists had already gone
  stale once.
- **The README rows.** The three hooks' rows in `source/hooks/README.md` say what each does
  once the bootcamp is complete, and name `bootcamp_complete()` in the Gate column.

The hooks run as subprocesses with a real working directory and real stdin, the way an
assistant invokes them. The container cases run the real `session-end.py` in a child process
whose container-CLI lookup and `subprocess.run` are replaced first, so no real container
command can run on a machine that has `docker`; they show which commands the hook builds, not
what a real runtime does with them. The negative controls run the same checks against a
scratch copy of the scripts with one line put back, so each check is shown to fail on the
defect it guards.

Asserts the finished case of **INV-227**'s 2026-11-10 note (#905) for these three hooks, and
that **INV-101**'s stop at session end survives it.

A further dated note to INV-227 (#32), which would bind these three hooks in the register, is
queued as a `PROPOSED AMENDMENT` block in this issue's entry of `specs/IMPLEMENTED.md`,
awaiting the maintainer's sign-off.

**What this cannot establish.** That a live assistant fires these hooks after graduation, or
what a real container runtime does: only a live run observes those. It was run on Linux only.
The text under `source/hooks/fallbacks/` is not read here: #32 leaves it alone.

Line-scoped by design (#32): a row of the hooks README's table is one physical line, so the
rows are read with `splitlines()`. The prose checks collapse whitespace first (INV-346).

Standard library only; nothing under `source/` is imported into this process (INV-108).

Run:  python3 -m unittest discover -s tests
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "source"
SCRIPTS = PLUGIN / "scripts"
TICK = "checkpoint-tick.py"
PRECOMPACT = "precompact-recap.py"
SESSION_END = "session-end.py"
BUILDER = "module_start_apparatus.py"
RECAP_HELPER = "recap_checkpoint.py"
THREE_HOOKS = (TICK, PRECOMPACT, SESSION_END)
HOOKS_README = PLUGIN / "hooks" / "README.md"
ONBOARDING = PLUGIN / "skills" / "bootcamp-onboarding" / "SKILL.md"

CHECKPOINT = Path("docs") / "progress" / "recap_checkpoint.md"
RECAP = Path("docs") / "bootcamp_recap.md"
START = "<!-- RECAP-CHECKPOINT:START -->"
END = "<!-- RECAP-CHECKPOINT:END -->"
SCAFFOLD = "<!-- RECAP-CHECKPOINT:SCAFFOLD -->"

#: A checkpoint that holds a narrative, so a fold has something to move.
NARRATIVE = "Loaded the first data source and read its load statistics."
FILLED = "%s\n### Data processing (in progress)\n\n%s\n%s\n" % (START, NARRATIVE, END)
#: A recap with one completed section and no checkpoint block.
RECAP_TEXT = "# Bootcamp recap\n\n## Business problem\n\nMatch customers across two systems.\n"

#: The progress file as graduation's closing step leaves it.
GRADUATED = {"current_module": "graduation", "current_step": None, "bootcamp_complete": True,
             "completed_at": "2026-11-10T12:00:00Z",
             "modules_completed": ["business_problem", "data_quality_mapping",
                                   "query_visualize_discover", "graduation"]}
#: The progress file of a project graduated before graduation wrote it: a module, no flag.
LEFT_ON_LAST_MODULE = {"current_module": "query_visualize_discover", "current_step": None,
                       "modules_completed": ["business_problem", "data_quality_mapping",
                                             "query_visualize_discover"]}
#: A bootcamp that is in progress and not complete.
ACTIVE = {"current_module": "data_processing", "current_step": 3,
          "modules_completed": ["business_problem", "data_quality_mapping"]}

FLAG = "name: Ada\nbootcamp_complete: true\n"
NO_FLAG = "name: Ada\nbootcamp_complete: false\n"

#: (case, progress, preferences): every way a project reads as finished while its progress
#: file records a module. The second row is the one the issue names: the flag only in
#: preferences.
FINISHED = (
    ("the flag in the progress file", GRADUATED, NO_FLAG),
    ("the flag only in preferences", LEFT_ON_LAST_MODULE, FLAG),
    ("the flag in both files", GRADUATED, FLAG),
)
#: (case, progress, preferences): in progress and not complete.
IN_PROGRESS = (
    ("no flag", ACTIVE, NO_FLAG),
    ("no preferences file", ACTIVE, None),
)

#: Two recorded containers, one per runtime, so a stop is shown to use each one's own CLI.
CONTAINERS = [{"name": "senzing-bootcamp-a1b2c3", "runtime": "docker"},
              {"name": "senzing-bootcamp-db-a1b2c3", "runtime": "podman"}]
#: The commands the stubbed lookup makes the hook build for them.
STOPS = [["stub-docker", "stop", "senzing-bootcamp-a1b2c3"],
         ["stub-podman", "stop", "senzing-bootcamp-db-a1b2c3"]]

POINTER = "\U0001f449"
TRANSITION = "%s **Are you ready to move on to the next module: Data processing?**" % POINTER
REMINDER_LABEL = "Module-completion records still missing"
ANNOUNCEMENT = "in-progress recap checkpoint now exists"
PRECOMPACT_LEAD = "A Senzing bootcamp is in progress."

#: Runs a hook script in this child process with the container CLI replaced. The lookup finds
#: every CLI as ``stub-<name>``, and ``subprocess.run`` records the command instead of running
#: it. The commands are written to a log file the caller names, outside the project.
DRIVER = r'''
import json
import runpy
import sys

scripts, hook, log = sys.argv[1:4]
sys.path.insert(0, scripts)
import docker_lifecycle

calls = []


class Done:
    returncode = 0
    stdout = ""


def record(args, **kwargs):
    calls.append([str(arg) for arg in args])
    return Done()


docker_lifecycle.shutil.which = lambda name, *args, **kwargs: "stub-" + name
docker_lifecycle.subprocess.run = record
code = 0
try:
    runpy.run_path(hook, run_name="__main__")
except SystemExit as stop:
    code = stop.code or 0
finally:
    with open(log, "w", encoding="utf-8") as fh:
        json.dump(calls, fh)
sys.exit(code)
'''


def flat(text):
    return re.sub(r"\s+", " ", text)


def read(path):
    return path.read_text(encoding="utf-8")


def environment():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


class Scripts:
    """The plugin's top-level scripts, or a scratch copy of them with mutations applied."""

    def __init__(self, test, mutations=None):
        self.dir = SCRIPTS
        if mutations:
            tmp = tempfile.TemporaryDirectory()
            test.addCleanup(tmp.cleanup)
            self.dir = Path(tmp.name)
            for path in SCRIPTS.glob("*.py"):
                shutil.copy(path, self.dir / path.name)
            for name, (old, new) in mutations.items():
                source = read(self.dir / name)
                test.assertEqual(1, source.count(old),
                                 "the mutation of %s no longer applies" % name)
                (self.dir / name).write_text(source.replace(old, new), encoding="utf-8")

    def run(self, script, root, stdin=b"{}"):
        """Run a hook the way an assistant does. Returns the finished process."""
        return subprocess.run([sys.executable, str(self.dir / script)], input=stdin,
                              capture_output=True, cwd=str(root), env=environment(),
                              timeout=60)

    def run_with_stub_cli(self, test, script, root):
        """Run a hook with the container CLI replaced. Returns ``(process, commands)``."""
        tmp = tempfile.TemporaryDirectory()
        test.addCleanup(tmp.cleanup)
        log = Path(tmp.name) / "commands.json"
        proc = subprocess.run(
            [sys.executable, "-c", DRIVER, str(self.dir), str(self.dir / script), str(log)],
            input=b"{}", capture_output=True, cwd=str(root), env=environment(), timeout=60)
        test.assertTrue(log.is_file(), "the driver wrote no log: %r" % proc.stderr)
        return proc, json.loads(read(log))

    def drains_stdin(self, script, root):
        """Whether the hook reads a payload larger than any pipe buffer to its end.

        A hook that exits with its stdin unread closes the pipe under the writer, and the
        write fails. Returns ``(drained, process)``.
        """
        payload = json.dumps({"hook_event_name": "UserPromptSubmit",
                              "prompt": "x" * (1 << 20)}).encode("utf-8")
        proc = subprocess.Popen([sys.executable, str(self.dir / script)],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=str(root), env=environment())
        try:
            proc.stdin.write(payload)
            proc.stdin.close()
            drained = True
        except OSError:
            drained = False
        proc.stdout.read()
        proc.stderr.read()
        proc.wait(timeout=60)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            try:
                stream.close()
            except OSError:
                pass
        return drained, proc


def project(test, progress, preferences, checkpoint=None, recap=None, containers=None):
    """A scratch bootcamp project. ``checkpoint`` and ``recap`` are file text, or None for no
    file; ``containers`` is recorded under ``docker_containers`` when given."""
    tmp = tempfile.TemporaryDirectory()
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name)
    (root / "config").mkdir()
    data = dict(progress)
    if containers is not None:
        data["docker_containers"] = containers
    (root / "config" / "bootcamp_progress.json").write_text(json.dumps(data), encoding="utf-8")
    if preferences is not None:
        (root / "config" / "bootcamp_preferences.yaml").write_text(preferences,
                                                                   encoding="utf-8")
    if checkpoint is not None:
        (root / CHECKPOINT).parent.mkdir(parents=True)
        (root / CHECKPOINT).write_text(checkpoint, encoding="utf-8")
    if recap is not None:
        (root / RECAP).parent.mkdir(parents=True, exist_ok=True)
        (root / RECAP).write_text(recap, encoding="utf-8")
    return root


def snapshot(root):
    """Every path under ``root`` with its bytes (None for a directory)."""
    return {path.relative_to(root).as_posix(): (path.read_bytes() if path.is_file() else None)
            for path in sorted(root.rglob("*"))}


def stand_down_problems(proc, before, after):
    """Each way a hook run failed to stand down: a non-zero exit, a byte on stdout or
    stderr, or a path created, removed or rewritten."""
    problems = []
    if proc.returncode != 0:
        problems.append("exit code %d" % proc.returncode)
    if proc.stdout != b"":
        problems.append("stdout: %r" % proc.stdout[:120])
    if proc.stderr != b"":
        problems.append("stderr: %r" % proc.stderr[:120])
    for path in sorted(set(before) | set(after)):
        if path not in before:
            problems.append("created %s" % path)
        elif path not in after:
            problems.append("removed %s" % path)
        elif before[path] != after[path]:
            problems.append("rewrote %s" % path)
    return problems


def transcript(test, question=TRANSITION):
    """A settled previous turn that ends on ``question``, in a file outside any project."""
    tmp = tempfile.TemporaryDirectory()
    test.addCleanup(tmp.cleanup)
    path = Path(tmp.name) / "transcript.jsonl"
    records = [
        {"type": "user", "message": {"role": "user", "content": "Done."}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "**Module complete**\n\n" + question}]}},
    ]
    path.write_text("".join(json.dumps(rec) + "\n" for rec in records), encoding="utf-8")
    return json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "yes",
                       "transcript_path": str(path)}).encode("utf-8")


def missing_record(progress):
    """``progress`` with a directing step left unset for a completed module: the record
    `checkpoint-tick.py` names on a transition reply."""
    return dict(progress, directing_steps={})


def context(test, proc):
    """A UserPromptSubmit hook's additionalContext, or "" when it printed nothing."""
    test.assertEqual(0, proc.returncode, proc.stderr)
    if proc.stdout == b"":
        return ""
    output = json.loads(proc.stdout.decode("utf-8"))["hookSpecificOutput"]
    test.assertEqual("UserPromptSubmit", output["hookEventName"])
    return output["additionalContext"]


class TheFixturesAreSound(unittest.TestCase):

    def test_the_scripts_exist(self):
        for name in THREE_HOOKS + (BUILDER, RECAP_HELPER):
            with self.subTest(script=name):
                self.assertTrue((SCRIPTS / name).is_file(), "%s moved" % name)

    def test_every_finished_case_records_a_module(self):
        """Otherwise `bootcamp_active()` alone would silence the hooks, and nothing here
        would test the completion check."""
        for label, progress, _prefs in FINISHED:
            with self.subTest(case=label):
                self.assertTrue(progress["current_module"])

    def test_the_narrative_checkpoint_folds_on_a_project_in_progress(self):
        """If this fails, every "nothing was folded" assertion below could be vacuous."""
        root = project(self, ACTIVE, NO_FLAG, checkpoint=FILLED, recap=RECAP_TEXT)
        proc = Scripts(self).run(SESSION_END, root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn(NARRATIVE, read(root / RECAP))


class CheckpointTickStandsDown(unittest.TestCase):

    def test_a_finished_project_gets_no_scaffold_and_no_word(self):
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs)
                before = snapshot(root)
                proc = Scripts(self).run(TICK, root)
                self.assertEqual([], stand_down_problems(proc, before, snapshot(root)))
                self.assertFalse((root / CHECKPOINT).exists())

    def test_a_finished_project_gets_no_missing_record_reminder(self):
        """The twin speaks first: the same progress file and the same transition reply, with
        the bootcamp not complete, get the reminder."""
        payload = transcript(self)
        twin = project(self, missing_record(dict(LEFT_ON_LAST_MODULE)), NO_FLAG,
                       checkpoint=SCAFFOLD + "\n")
        self.assertIn(REMINDER_LABEL, context(self, Scripts(self).run(TICK, twin, payload)))
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, missing_record(progress), prefs,
                               checkpoint=SCAFFOLD + "\n")
                before = snapshot(root)
                proc = Scripts(self).run(TICK, root, payload)
                self.assertEqual([], stand_down_problems(proc, before, snapshot(root)))

    def test_a_scaffold_already_there_is_left_in_place(self):
        """Out of scope by decision: no hook removes a scaffold recreated before the fix."""
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=SCAFFOLD + "\n")
                before = snapshot(root)
                proc = Scripts(self).run(TICK, root)
                self.assertEqual([], stand_down_problems(proc, before, snapshot(root)))
                self.assertEqual(SCAFFOLD + "\n", read(root / CHECKPOINT))

    def test_stdin_is_still_read_to_the_end(self):
        for label, progress, prefs in FINISHED + IN_PROGRESS:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=SCAFFOLD + "\n")
                drained, proc = Scripts(self).drains_stdin(TICK, root)
                self.assertTrue(drained, "the hook exited with its stdin unread")
                self.assertEqual(0, proc.returncode)

    def test_a_project_in_progress_still_gets_its_scaffold_and_announcement(self):
        for label, progress, prefs in IN_PROGRESS:
            with self.subTest(case=label):
                root = project(self, progress, prefs)
                proc = Scripts(self).run(TICK, root)
                self.assertIn(ANNOUNCEMENT, context(self, proc))
                self.assertIn(SCAFFOLD, read(root / CHECKPOINT))
                self.assertIn(b"recap-checkpoint: created", proc.stderr)
                again = Scripts(self).run(TICK, root)
                self.assertEqual("", context(self, again),
                                 "the announcement is made once, on the turn the file is "
                                 "created")

    def test_a_project_in_progress_still_gets_its_missing_record_reminder(self):
        for label, progress, prefs in IN_PROGRESS:
            with self.subTest(case=label):
                root = project(self, missing_record(progress), prefs,
                               checkpoint=SCAFFOLD + "\n")
                proc = Scripts(self).run(TICK, root, transcript(self))
                self.assertIn(REMINDER_LABEL, context(self, proc))


class PrecompactRecapStandsDown(unittest.TestCase):

    def test_a_finished_project_gets_no_fold_and_no_reminder(self):
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=FILLED, recap=RECAP_TEXT)
                before = snapshot(root)
                proc = Scripts(self).run(PRECOMPACT, root)
                self.assertEqual([], stand_down_problems(proc, before, snapshot(root)))
                self.assertEqual(RECAP_TEXT, read(root / RECAP))
                self.assertEqual(FILLED, read(root / CHECKPOINT),
                                 "a narrative left after graduation is left as it is")

    def test_a_finished_project_with_no_checkpoint_is_silent_too(self):
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs)
                before = snapshot(root)
                proc = Scripts(self).run(PRECOMPACT, root)
                self.assertEqual([], stand_down_problems(proc, before, snapshot(root)))

    def test_a_project_in_progress_still_folds_and_reminds(self):
        for label, progress, prefs in IN_PROGRESS:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=FILLED, recap=RECAP_TEXT)
                proc = Scripts(self).run(PRECOMPACT, root)
                self.assertEqual(0, proc.returncode, proc.stderr)
                out = proc.stdout.decode("utf-8")
                self.assertTrue(out.startswith(PRECOMPACT_LEAD), out)
                self.assertIn("docs/progress/recap_checkpoint.md", out)
                recap = read(root / RECAP)
                self.assertTrue(recap.startswith(RECAP_TEXT.rstrip()), recap)
                self.assertIn(START, recap)
                self.assertIn(NARRATIVE, recap)
                self.assertIn(b"recap-checkpoint: folded", proc.stderr)


class SessionEndSkipsOnlyTheFold(unittest.TestCase):

    def test_a_finished_project_gets_no_fold_and_no_word(self):
        """Run as an assistant runs it. The project records no container, so no container
        command can be built."""
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=FILLED, recap=RECAP_TEXT)
                before = snapshot(root)
                proc = Scripts(self).run(SESSION_END, root)
                self.assertEqual([], stand_down_problems(proc, before, snapshot(root)))
                self.assertEqual(RECAP_TEXT, read(root / RECAP))

    def test_a_finished_project_still_has_its_containers_stopped(self):
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=FILLED, recap=RECAP_TEXT,
                               containers=CONTAINERS)
                before = snapshot(root)
                proc, commands = Scripts(self).run_with_stub_cli(self, SESSION_END, root)
                self.assertEqual(STOPS, commands,
                                 "each recorded container is stopped with its own CLI, and "
                                 "nothing else is run")
                self.assertEqual([], stand_down_problems(proc, before, snapshot(root)),
                                 "the stop changes no file and says nothing, and nothing "
                                 "is folded")

    def test_a_project_in_progress_still_folds_and_stops(self):
        for label, progress, prefs in IN_PROGRESS:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=FILLED, recap=RECAP_TEXT,
                               containers=CONTAINERS)
                proc, commands = Scripts(self).run_with_stub_cli(self, SESSION_END, root)
                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertEqual(STOPS, commands)
                self.assertEqual(b"", proc.stdout, "session end emits no output")
                recap = read(root / RECAP)
                self.assertIn(START, recap)
                self.assertIn(NARRATIVE, recap)
                self.assertIn(b"recap-checkpoint: folded", proc.stderr)

    def test_a_project_in_progress_with_no_container_still_folds(self):
        for label, progress, prefs in IN_PROGRESS:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=FILLED, recap=RECAP_TEXT)
                proc = Scripts(self).run(SESSION_END, root)
                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertEqual(b"", proc.stdout)
                self.assertIn(NARRATIVE, read(root / RECAP))


def completion_calls(source):
    """How many times a script's code calls ``module_start_apparatus.bootcamp_complete()``,
    read from the syntax tree so a docstring that names it does not count."""
    return sum(1 for node in ast.walk(ast.parse(source))
               if isinstance(node, ast.Call)
               and ast.unparse(node) == "module_start_apparatus.bootcamp_complete()")


def module_level_tests(source):
    """The test of each module-level ``if``, as source text."""
    return [ast.unparse(node.test) for node in ast.parse(source).body
            if isinstance(node, ast.If)]


class EachHookMakesItsOwnCheck(unittest.TestCase):

    def test_each_of_the_three_calls_the_one_implementation(self):
        for name in THREE_HOOKS:
            with self.subTest(script=name):
                source = read(SCRIPTS / name)
                self.assertEqual(1, completion_calls(source))
                self.assertNotIn("bootcamp_preferences", source,
                                 "%s reads the flag itself" % name)

    def test_each_of_the_three_keeps_its_bootcamp_active_gate(self):
        for name in THREE_HOOKS:
            with self.subTest(script=name):
                self.assertTrue(any("recap_checkpoint.bootcamp_active()" in test
                                    for test in module_level_tests(read(SCRIPTS / name))))

    def test_session_end_stops_containers_outside_the_completion_check(self):
        """The stop is a statement of the `bootcamp_active()` block itself, never of the
        completion check inside it."""
        tree = ast.parse(read(SCRIPTS / SESSION_END))
        gate = next(node for node in tree.body if isinstance(node, ast.If)
                    and ast.unparse(node.test) == "recap_checkpoint.bootcamp_active()")
        direct = [ast.unparse(node) for node in gate.body if isinstance(node, ast.Expr)]
        self.assertIn("docker_lifecycle.stop_started_containers()", direct)
        self.assertNotIn("recap_checkpoint.fold_checkpoint()", direct)

    def test_bootcamp_active_does_not_read_the_flag(self):
        """Out of scope by decision: `bootcamp_active()` keeps its meaning (INV-227)."""
        self.assertNotIn("bootcamp_complete", read(SCRIPTS / RECAP_HELPER))


SCRIPT_NAME = re.compile(r"[\w-]+\.py\b")


def builder_caller_list(source):
    """The script names in the two places `module_start_apparatus.py` states the
    finished-bootcamp rule: ``bootcamp_complete()``'s docstring, and the paragraph of the
    module docstring that names it."""
    tree = ast.parse(source)
    function = next((node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name == "bootcamp_complete"), None)
    if function is None:
        return None
    names = SCRIPT_NAME.findall(ast.get_docstring(function) or "")
    for paragraph in (ast.get_docstring(tree) or "").split("\n\n"):
        if "bootcamp_complete()" in paragraph:
            names += SCRIPT_NAME.findall(paragraph)
    return names


def finished_case(text):
    """The Finished case of `bootcamp-onboarding/SKILL.md` step 2, whitespace collapsed."""
    m = re.search(r"- \*\*Finished\*\* —(.*?)\n   - \*\*Missing\*\*", text, re.S)
    return flat(m.group(1)) if m else None


class NoListOfCallersIsKept(unittest.TestCase):

    def test_the_builder_names_no_caller(self):
        self.assertEqual([], builder_caller_list(read(SCRIPTS / BUILDER)))

    def test_the_onboarding_skill_names_no_caller(self):
        case = finished_case(read(ONBOARDING))
        self.assertIsNotNone(case, "step 2's Finished case moved")
        self.assertEqual([], SCRIPT_NAME.findall(case))
        self.assertIn("`module_start_apparatus.bootcamp_complete()`", case,
                      "the Finished case no longer points at the one implementation")


def readme_row(text, script):
    """``(purpose, gate)`` of a hook script's row in the hooks README, or None unless it has
    exactly one row."""
    rows = [line for line in text.splitlines()
            if line.startswith("| ") and "`scripts/%s`" % script in line.split("|")[2]]
    if len(rows) != 1:
        return None
    cells = [cell.strip() for cell in rows[0].strip().strip("|").split("|")]
    return cells[2], cells[3]


def readme_problems(text):
    """Each way the three hooks' README rows fail to say what the code does once the
    bootcamp is complete."""
    problems = []
    for script in THREE_HOOKS:
        row = readme_row(text, script)
        if row is None:
            problems.append("%s does not have exactly one row" % script)
            continue
        purpose, gate = row
        if not purpose.startswith("to "):
            problems.append("%s: the purpose does not begin with 'to'" % script)
        if "once the bootcamp is complete" not in purpose.lower():
            problems.append("%s: the purpose does not say what happens once the bootcamp is "
                            "complete" % script)
        if not gate.startswith("`bootcamp_active()`:"):
            problems.append("%s: the gate cell does not lead with bootcamp_active()" % script)
        if "`bootcamp_complete()`" not in gate:
            problems.append("%s: the gate cell does not name bootcamp_complete()" % script)
    row = readme_row(text, SESSION_END)
    if row is not None:
        if "still stops the containers" not in row[0]:
            problems.append("session-end.py: the purpose does not say the containers are "
                            "still stopped")
        if "only the fold is skipped" not in row[1]:
            problems.append("session-end.py: the gate cell does not say only the fold is "
                            "skipped")
    return problems


class TheReadmeRowsMatchTheCode(unittest.TestCase):

    def test_the_three_rows_say_what_a_finished_bootcamp_gets(self):
        self.assertEqual([], readme_problems(read(HOOKS_README)))

    def test_each_row_that_names_the_check_belongs_to_a_script_that_makes_it(self):
        text = read(HOOKS_README)
        for script in THREE_HOOKS:
            with self.subTest(script=script):
                _purpose, gate = readme_row(text, script)
                self.assertEqual("`bootcamp_complete()`" in gate,
                                 completion_calls(read(SCRIPTS / script)) > 0)


class NegativeControls(unittest.TestCase):
    """Each check above must turn red on the defect it guards against."""

    def test_a_checkpoint_tick_without_the_check_is_caught(self):
        scripts = Scripts(self, {TICK: ("if module_start_apparatus.bootcamp_complete():\n"
                                        "    sys.exit(0)\n",
                                        "if False:\n    sys.exit(0)\n")})
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs)
                before = snapshot(root)
                proc = scripts.run(TICK, root)
                problems = stand_down_problems(proc, before, snapshot(root))
                self.assertIn("created docs/progress/recap_checkpoint.md", problems)
                self.assertTrue(any(p.startswith("stdout:") for p in problems), problems)

    def test_a_checkpoint_tick_that_stands_down_before_reading_stdin_is_caught(self):
        scripts = Scripts(self, {TICK: (
            "try:\n    payload = json.loads(sys.stdin.buffer.read())\n",
            "if module_start_apparatus.bootcamp_complete():\n    sys.exit(0)\n"
            "try:\n    payload = json.loads(sys.stdin.buffer.read())\n")})
        root = project(self, GRADUATED, NO_FLAG)
        drained, _proc = scripts.drains_stdin(TICK, root)
        self.assertFalse(drained, "an unread stdin went unnoticed")

    def test_a_precompact_without_the_check_is_caught(self):
        scripts = Scripts(self, {PRECOMPACT: (
            " and not module_start_apparatus.bootcamp_complete()", "")})
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=FILLED, recap=RECAP_TEXT)
                before = snapshot(root)
                proc = scripts.run(PRECOMPACT, root)
                problems = stand_down_problems(proc, before, snapshot(root))
                self.assertIn("rewrote docs/bootcamp_recap.md", problems)
                self.assertTrue(any(p.startswith("stdout:") for p in problems), problems)

    def test_a_session_end_that_still_folds_is_caught(self):
        scripts = Scripts(self, {SESSION_END: (
            "    if not module_start_apparatus.bootcamp_complete():\n"
            "        recap_checkpoint.fold_checkpoint()\n",
            "    recap_checkpoint.fold_checkpoint()\n")})
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs, checkpoint=FILLED, recap=RECAP_TEXT)
                before = snapshot(root)
                proc = scripts.run(SESSION_END, root)
                self.assertIn("rewrote docs/bootcamp_recap.md",
                              stand_down_problems(proc, before, snapshot(root)))

    def test_a_session_end_that_gates_the_stop_too_is_caught(self):
        scripts = Scripts(self, {SESSION_END: (
            "    docker_lifecycle.stop_started_containers()\n",
            "    if not module_start_apparatus.bootcamp_complete():\n"
            "        docker_lifecycle.stop_started_containers()\n")})
        for label, progress, prefs in FINISHED:
            with self.subTest(case=label):
                root = project(self, progress, prefs, containers=CONTAINERS)
                _proc, commands = scripts.run_with_stub_cli(self, SESSION_END, root)
                self.assertEqual([], commands, "the stop was not gated by the mutation")
        root = project(self, ACTIVE, NO_FLAG, containers=CONTAINERS)
        _proc, commands = scripts.run_with_stub_cli(self, SESSION_END, root)
        self.assertEqual(STOPS, commands)

    def test_a_predicate_reading_one_file_only_is_caught(self):
        """Each of the two single-file rows fails under the rule that ignores its file, so
        the matrix tells the either-file rule from both one-file rules."""
        rule = "return _progress_flag() or _preferences_flag()"
        for kept, missed in (("return _progress_flag()", (LEFT_ON_LAST_MODULE, FLAG)),
                             ("return _preferences_flag()", (GRADUATED, NO_FLAG))):
            scripts = Scripts(self, {BUILDER: (rule, kept)})
            for hook in (TICK, PRECOMPACT, SESSION_END):
                with self.subTest(rule=kept, hook=hook):
                    root = project(self, *missed, checkpoint=None if hook == TICK else FILLED,
                                   recap=RECAP_TEXT)
                    before = snapshot(root)
                    proc = scripts.run(hook, root)
                    self.assertTrue(stand_down_problems(proc, before, snapshot(root)))

    def test_a_caller_list_put_back_in_the_builder_is_caught(self):
        source = read(SCRIPTS / BUILDER)
        old = "and every hook that asks whether the bootcamp is over\n    calls it (INV-300)."
        self.assertIn(old, source, "the mutation no longer applies")
        mutant = source.replace(old, "shared by ``session-start.py`` and\n"
                                     "    ``stop-nudge.py`` (INV-300).")
        self.assertEqual(["session-start.py", "stop-nudge.py"], builder_caller_list(mutant))

    def test_a_caller_list_put_back_in_the_skill_is_caught(self):
        text = read(ONBOARDING)
        old = "Every hook that asks whether the bootcamp is over reads the flag"
        self.assertIn(old, text, "the mutation no longer applies")
        mutant = text.replace(old, "`session-start.py` and `stop-nudge.py` read the flag")
        self.assertEqual(["session-start.py", "stop-nudge.py"],
                         SCRIPT_NAME.findall(finished_case(mutant)))

    def test_a_readme_row_that_says_nothing_of_completion_is_caught(self):
        text = read(HOOKS_README)
        for script in THREE_HOOKS:
            with self.subTest(script=script):
                row = next(line for line in text.splitlines()
                           if line.startswith("| ") and "`scripts/%s`" % script in line)
                purpose, gate = readme_row(text, script)
                bare = text.replace(row, row.replace(gate, "`bootcamp_active()`: no module "
                                                           "is recorded yet."))
                self.assertIn("%s: the gate cell does not name bootcamp_complete()" % script,
                              readme_problems(bare))
                mute = text.replace(row, row.replace(purpose, "to keep your recap."))
                self.assertIn("%s: the purpose does not say what happens once the bootcamp "
                              "is complete" % script, readme_problems(mute))


if __name__ == "__main__":
    unittest.main()
