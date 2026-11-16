# Model and effort (maintainer notes)

This is a maintainer/developer reference — it does not ship as bootcamper-facing
content. It records how the bootcamp handles the model and the reasoning effort, why
it handles them that way, and why each stage has the working depth it has, so the
analysis is not re-investigated.

**The headline:** the bootcamp handles this itself. One model is fine for the whole
bootcamp, the bootcamper is never asked to change the model or the reasoning effort,
and how carefully the guide works at each stage is set by instruction alone.

## What the bootcamper sees

- **One statement, in the welcome.** The overview names one suitable model for the
  whole bootcamp, Opus 5.5 on Claude, and says the bootcamp never asks for a change of
  model or settings along the way (`../skills/bootcamp-onboarding/onboarding-flow.md`,
  step 3). It is a statement among the welcome points: no 👉, no pause, said once.
- **Nothing after that.** No module start and no graduation start says anything about
  a model or a reasoning effort. There is no question, no confirmation gate and no
  instruction naming a control. A bootcamper on a weaker model hears
  nothing further about it.
- **Nothing about automatic modes.** Whether the assistant is choosing the model or
  the effort by itself is neither detected nor mentioned.

There is no `model_guidance` preference. A stale `model_guidance` key in an old
preferences file is ignored, not honored (INV-137).

## What the guide does

`../skills/bootcamp-onboarding/ground-rules.md` → "Working depth by stage" gives every
stage one effort level, and gives each level one instruction to the guide. The guide
applies the instruction silently and changes no setting.

> **`ground-rules.md` is the authoritative copy of this table; the copy below is derived.**
> `ground-rules.md` is the file the guide actually loads, so the operational values
> must live there. Change `ground-rules.md` first, then mirror it here.
>
> The two are not kept in sync by hand: `tests/test_model_guidance_sync.py` asserts they
> are identical row for row, that every stage the bootcamp can run has exactly one row,
> that no superseded model name or ID appears in any shipped or user-facing doc, and that
> this file carries a dated verification note (INV-114). Editing one table
> without the other fails the suite.

| Stage | Effort |
|---|---|
| Onboarding | medium |
| Bootcamp preparation | medium |
| Entity Resolution Concepts | medium |
| Discover the Business Problem | medium |
| SDK setup | high |
| System verification | high |
| Truth Set visualization | high |
| Data collection | medium |
| Data Quality, Mapping, and Transformation | high |
| Data processing | high |
| Query, Visualize and Discover | high |
| Bootcamp graduation | high |

- **medium:** Move briskly: work from what the step and the Senzing MCP server give you, and do not re-derive what is already settled.
- **high:** Work carefully: before you write code or state a result, check it against the MCP server's answer and the bootcamper's own files, and re-read the step's rules before each action.

**One row per stage, in the order the bootcamp runs them,** and one level per row. Every
stage the bootcamp can run has exactly one row, the setup stages included (INV-140). A
conditional level ("high if bespoke load code") is not allowed: the guide reads the row
at the stage's start, before a condition can be resolved.

The levels are named after the reasoning-effort levels they stand in for, and they set
none: `medium` and `high` here are two ways of working, written as instructions.

## Why instructions, and not a setting

A setting only means anything for a component that invokes Claude. `type: command`
hooks and the scripts they run are deterministic programs and never "run under a
model."

| Component | Model? | Effort? | How / scope |
|---|:---:|:---:|---|
| Skills (`SKILL.md` frontmatter) | ✅ | ✅ | `model:` + `effort:` (`low`/`medium`/`high`/`xhigh`/`max`). **Turn-scoped.** |
| Slash commands (`.md` frontmatter) | ✅ | ❌ | `model:`; no effort field |
| Subagents (`agents/*.md`) | ✅ | ✅ | `model:` (`inherit` default) + `effort:`; persists for the subagent's whole run |
| Command hooks (`type: command`) | ❌ | ❌ | Deterministic program; only reads session effort via `$CLAUDE_EFFORT` |
| Prompt hooks (`type: prompt`) | ✅ | ❌ | `model:` in hook config |
| Agent hooks (`type: agent`) | ➖ | ➖ | Inherits the spawned subagent's `model:`/`effort:` |
| Scripts (run by hooks/commands) | ❌ | ❌ | Not model-executed |

None of these fits, so none is used:

- **Skill frontmatter is turn-scoped.** From the Claude Code skills docs:

  > The override applies for the rest of the current turn and is not saved to
  > settings; the session model resumes on your next prompt.

  A bootcamp module is loaded once and then runs for many turns: every step ends by
  yielding to the bootcamper after one 👉 question, so each following step arrives as
  a new prompt at the session's own model and effort. An `effort:` on a module skill
  would govern the turn that loads the module and none of the turns that do its work.
  The build also holds skill frontmatter to the keys every assistant reads, `name` and
  `description`.
- **A subagent does not see the conversation.** It holds its own `model:`/`effort:`
  for its whole run, but the bootcamp's stages depend on the conversation: the
  bootcamper's answers, their data and one question at a time.
- **The session's own setting belongs to the bootcamper.** Only they can change it,
  and the bootcamp does not ask them to. An earlier design asked at module starts;
  issue #4 retired that on every assistant.

An instruction is the one mechanism every assistant has. It touches no setting and
leaves an automatic mode free to decide for itself. The development repository's
`docs/effort-mechanisms.md` records the research behind this.

## Model tiers

Approximate positioning (verify current pricing/availability before relying on
the numbers — see the staleness note below):

| Model | Tier | ~Price (in/out per MTok) | Adaptive thinking | Notes |
|---|---|---|:---:|---|
| Fable 5.1 (`claude-fable-5-1`) | Top | ~$10 / ~$50 | Always on | Most capable; for demanding reasoning and long-horizon agentic work; slower; ~2.5× Opus cost |
| Opus 5.5 (`claude-opus-5-5`) | High | ~$4 / ~$20 | Always on | Long-running agentic coding and knowledge work; the general-purpose default |
| Sonnet 5.5 (`claude-sonnet-5-5`) | Mid | ~$2 / ~$10 | Yes | Speed/cost/capability sweet spot |
| Haiku 4.5 (`claude-haiku-4-5`) | Budget | ~$1 / ~$5 | **No** | Fastest; no adaptive thinking |

> **Point-in-time data — re-verify before relying on it.** Model names, IDs, and
> prices above are a snapshot, **last verified 2026-10-01** against
> `platform.claude.com/docs/en/about-claude/models/overview`. They go stale whenever
> a new model ships. That happened between the previous check (2026-07-25) and
> this one: Fable 5.1, Opus 5.5 and Sonnet 5.5 superseded Fable 5 (`claude-fable-5`),
> Opus 5 (`claude-opus-5`) and Sonnet 5 (`claude-sonnet-5`), which that page now
> lists as legacy, and the per-stage table lagged them. Prices moved with them,
> against the figures recorded at the 2026-07-25 check (not re-verified today):
> Opus 5.5 is cheaper than Opus 5 (~$5 / ~$25, the price Opus 5 had inherited from
> Opus 4.8), and Sonnet 5.5 cheaper than Sonnet 5 (~$3 / ~$15), while Fable 5.1
> lists the price recorded for Fable 5. Re-verify names, IDs, and pricing against current Claude
> documentation rather than trusting this table. The welcome names Opus 5.5 from the same
> snapshot, so it goes stale with it. This note is the only place in
> the shipped plugin that may name a superseded model, and only to explain the
> supersession; `tests/test_model_guidance_sync.py` exempts this block and nothing
> else in the file.

For a protocol-heavy (⛔ gates, INV-056 pinned wording, one-👉-per-turn),
MCP-first teaching plugin, Haiku's lack of adaptive thinking is a real risk of
gate/format slips, and Fable's premium buys little the workloads here need.

## Per-skill evaluation

Why each stage has its effort level. This table is the only record of the reasoning,
so every shipped skill has a row.

**Re-assessed 2026-07-26,** when the levels were still session settings the bootcamper
was asked to choose; the model half of that assessment was dropped with issue #4 and
the effort half is what the table keeps.

| Skill | Workload | Effort | Rationale |
|---|---|:---:|---|
| `bootcamp-onboarding` | Gated preface, exact-wording gates, preference capture | medium | Protocol adherence and instruction-following; no code |
| `bootcamp-preparation` | Setup preferences: verbosity, language, Core-vs-Customized path, module selection | medium | Same workload class as onboarding — pinned questions and recorded answers, no code. The choices steer every later module, so instruction-following matters more than depth |
| `module-00-entity-resolution-concepts` | Concepts teaching, Q&A, knowledge check | medium | Conversational teaching, no code |
| `module-01-business-problem` | Discovery conversation, document the problem | medium | Conversation-led, light technical |
| `module-02-sdk-setup` | Cross-platform install, license/engine/DB config, build-from-source recovery | high | Largest skill, most error-prone, platform-specific; install/config errors are high-cost |
| `module-03-system-verification` | Verify end-to-end, write and run the first real SDK code, report | high | Not "run / check / report": it writes the first working SDK code against the installed engine, and the 2026-07-26 export-flag defect was filed against this module |
| `module-03b-truthset-visualization` | **Build** a visualization server in the chosen language, load Truth Set, visualize | high | The module *generates* the server (INV-090): tab ids and deep-linking (INV-124), script-payload escaping (INV-106), offline vendoring (INV-091), brand tokens (INV-081). The largest code-generation artifact before graduation, and historically the most defect-prone |
| `module-04-data-collection` | Gather sources into `data/raw/` | medium | Data wrangling + light code; genuinely the lightest technical module |
| `module-05-data-quality-mapping` | Quality scoring + mapping to the Entity Spec via `mapping_workflow` | high | Mapping correctness drives resolution quality — the technical crux |
| `module-06-data-processing` | Load mapped data (SDK), validate, redo drain, export | high | Its failures are the silent kind: export flag families yielding rows with only `ENTITY_ID`, a redo drain that never terminates, the threading cutover |
| `module-07-query-visualize-discover` | Query SDK code, build the results app, discovery, deliverable | high | Where the silent-wrongness defects land: three of the 2026-07-26 self-observed entries plus INV-115's originating incident. Wrong field names render blank instead of raising — the failure mode least tolerant of working fast |
| `graduation` | Recap reconcile, PDF, production project (code/config/docs), report | high | Crown-jewel deliverable; production code/config correctness matters most |

## One model for the whole bootcamp

The welcome names the capable tier, **Opus 5.5**, because the back half of the
bootcamp, from Data Quality, Mapping, and Transformation through graduation, is where
correctness matters most. Running it throughout over-pays on the lighter conversational
modules; that cost is accepted so that the bootcamp never interrupts a module to ask
for a change. **Haiku 4.5** is not suited to any bootcamper-facing skill (protocol
risk), and **Fable 5.1** buys little the workloads here need. The bootcamp says none of
this to the bootcamper: it names one model once and leaves the choice with them.

## Sources

- Skills model/effort scope: `code.claude.com/docs/en/skills.md` (frontmatter reference).
- Subagents model/effort: `code.claude.com/docs/en/sub-agents.md`.
- Hooks: `code.claude.com/docs/en/hooks.md`.
- Model positioning/pricing: `platform.claude.com/docs/en/about-claude/models/overview`.
