
  ⛔ **This is the ONLY Claude-interface control the bootcamp asks the bootcamper to operate
  (INV-247).** It is an exception, not a precedent: no other session- or host-level setting — auto
  mode, auto-accept edits, permission mode, plan mode, fast mode, background tasks, `/compact`,
  `/loop` — is ever offered as a bootcamp question, and a new nudge in that shape must not be added
  here or anywhere else. Read the closed-question-set rule in the 👉 protocol before adding one. This
  limit is stated here because *this* section is what creates the expectation: a bootcamper who has
  just been asked to set `/model` and `/effort` for this module has no way to tell an unsanctioned
  interface question from bootcamp content.

  Like the step overview and the time estimate, this is module-start apparatus, so
  the apparatus-exempt setup modules (Bootcamp preparation, Module 0) do not present it (INV-063
  clarification). **Adapt the wording to the Claude interface in use** (INV-098): on the **Claude
  Code CLI** present the exact `/model` and `/effort` commands; in **Claude Desktop, the Claude web
  app, or a Claude IDE extension** — or when the interface is unknown — phrase it by intent, naming
  the recommended model and reasoning-effort level and directing the bootcamper to that interface's
  model/effort controls, without hardcoding a UI label that may drift.

  ⛔ **Name the interface. "The Claude app" is retired vocabulary (INV-158).** This plugin is a
  Claude Code plugin on every one of those interfaces — Claude Desktop runs Claude Code too — so
  that phrase left the bootcamper guessing which controls were meant, and "Claude Code" on its own
  does not distinguish the terminal from the desktop application. Say **Claude Code CLI** for the
  terminal and **Claude Desktop** for the desktop application.

  ⛔ **This behavior is unconditional — there is no preference to read and no mode to choose
  (INV-137).** The bootcamp is never asked how it wants model guidance handled, and there is no
  `model_guidance` key.

  ⛔ (INV-138) **For every dial whose current value can be determined, compare the recommendation
  against what the bootcamper is running right now — not against the previous stage's
  recommendation.** A dial that cannot be determined is the one exception, and the proxy at the end
  of this paragraph is its rule. You are told which model you are running, so read the
  model side from that; for effort, use the value in force when you can determine it. **Resolve
  "cannot be determined" PER DIAL, not for the setting as a whole** — model and effort are separate
  dials (INV-137), and in a live session they routinely sit in different epistemic states at the
  same moment: the model is knowable to the assistant, while the reasoning effort is **not exposed
  by default**. So compare each dial on its own evidence: a determinable
  model is compared **directly** even when effort is not, and vice versa. **Only for a dial whose
  current value cannot be determined**, and has never been determined in this conversation, use the
  **proxy**: compare this stage's recommended value for that dial against the recommended value for
  it in the stage just completed (that stage's row in the table below, INV-138's "previous stage's
  row"), and ask that dial's half only when the two differ; when they are the same, treat that dial
  as matching.
  ⛔ (INV-138) **The proxy is the only sanctioned recommendation-to-recommendation comparison.** It
  exists because such a dial has no current value to compare, and it is the previous-stage fallback
  the rest of this section refers to. On the Claude Code CLI before any `/effort` has been run, it is
  how the effort dial is decided: Discover the Business Problem (medium) to SDK setup (high) differs,
  so the effort half is asked.

  ⛔ **"Effort is not exposed by default" is not "effort can never be read" — and the switch flow
  below manufactures the evidence.** On the **Claude Code CLI** an `/effort` invocation reports the
  resulting level in the transcript, and the flow below asks the bootcamper to run exactly that
  command and then gates on "👉 Are you done modifying the model and effort?". So the moment an
  `/effort` result is in this conversation, the effort dial **is** determinable, and the
  previous-stage fallback MUST NOT be used for it — treating it as unreadable anyway is the same
  failure this clause already forbids for the model. Read the most recent such value, not the
  earliest — and compare it against the stage's recommendation, never against the previous stage's
  recommendation. Observed on a dry run, 2026-08-13: the bootcamper ran `/effort` at the SDK setup
  nudge and the transcript reported `xhigh`, which made the dial determinable from that point on;
  every later stage nevertheless fell back as though it were unreadable.
  On **Claude Desktop, the Claude web app or an IDE extension** there is no such
  command, so the dial may genuinely stay undeterminable there — both paths are live, and which one
  applies depends on the interface and on whether the bootcamper has used it.
  ⛔ Applying the previous-stage row to a dial that *was* determinable is the failure this clause
  exists to prevent: a bootcamper demonstrably on Opus 5.5 would be compared against the previous
  stage's recommended Sonnet 5.5, found "unchanged", and never offered the switch — silently defeating
  the purpose of the invariant this superseded. Comparing recommendation-to-recommendation asks a
  bootcamper already on Opus 5.5 at high effort "would you like to switch to Opus 5.5 at high effort?" —
  a question whose answer changes nothing, which is exactly what INV-006 and INV-012 forbid. Running
  one model for the whole bootcamp is a supported choice, so this is the common case, not an edge
  case.

  ⛔ **One dial is exempt from the comparison before it starts: an effort setting ABOVE everything
  the table ever recommends.** The table's highest effort is `high`; the CLI dial also offers `xhigh`
  and `max`. A bootcamper who has chosen one of those sits above **every remaining row**, so the
  step-down clause below would fire at every module for the rest of the bootcamp — twelve questions
  proposing a change they already made deliberately, none of which they can make stop except by
  downgrading. Treat the recommendation as **satisfied**: give the one-line statement (the "matches"
  case below), name the stage's recommended effort, and say plainly that running higher is fine. Ask
  **nothing**. A deliberate over-provision is not a mismatch to correct, and re-offering it every
  module is the "pointless switch? every module" outcome INV-006 and INV-012 forbid.

  ⚠️ **This is narrower than it may look, and deliberately so.** It applies only *above the whole
  table*, never to a step down **within** it — a bootcamper on Opus 5.5 / high entering a Sonnet 5.5 /
  medium stage is still asked, both dials, exactly as today. Step-down questions inside the table
  remain symmetric with step-ups by maintainer decision (2026-07-26, recorded in
  `../../docs/model-selection.md`); what this carve-out removes is only the case that **cannot be
  resolved by answering it**.

  The **model** dial has the same case today: **Fable 5.1 sits above the table's top row, Opus 5.5**,
  so a bootcamper running Fable 5.1 is above every row on the model dial, and the exemption applies
  there in the same terms. The model half is **satisfied**, not mismatched: at every stage they get
  the one-line statement, naming the stage's recommended model and saying that running higher is
  fine, and **never** a model question. Their effort is still compared on its own evidence. If a
  stronger model ships and this table lags it, the same terms apply to it. Opus 5.5 is not above the
  table, because it *is* the top row: a bootcamper on Opus 5.5 entering a Sonnet 5.5 stage is asked,
  as a step down within the table (INV-139).

  Two cases, decided only by that comparison:

  - **The recommendation differs from the current setting** — in **either** direction. A step down
    asks just as a step up does: the choice is the bootcamper's both ways. End the turn with a
    **single** 👉 yes/no question offering the switch, and do NOT also show Step 1 this turn
    (exactly one 👉 per turn — INV-251; INV-008/INV-009 govern each question's clarity, not the count).

    **Name only the dial that differs.** Model and effort are **separate dials**: a bootcamper on
    Opus 5.5 at medium effort entering a stage recommending Opus 5.5 at high effort is asked to change
    the effort only, never told to re-set the model they are already on.

    ⛔ **That rule covers the whole sentence, including the answer hint** — `{dial}` below resolves
    to "model", "effort", or "model and effort", matching whatever the stem names. An effort-only
    question that ends "reply no to keep your current **model**" tells the bootcamper what declining
    does to a dial it is not touching, and the pinning rule (INV-056) means the guide cannot quietly
    correct it at runtime. This is the common case, not an edge one: a bootcamper who stays on Opus 5.5
    through the conversational stages meets an **effort-only** step-up at SDK setup, the first time
    the nudge has anything to say to them at all.

    On the **Claude Code CLI**, pin the switch question verbatim, substituting only the bracketed
    values — the stage's commands, just the one dial when only one differs, and `{dial}` to match:

    > 👉 **Would you like to switch to `/model {model}` + `/effort {effort}` for {this module | graduation}?** (Recommended for best value; reply no to keep your current {dial}.)

    In **Claude Desktop, the Claude web app, or a Claude IDE extension** (or an unknown interface),
    pin the intent-based equivalent — name the stage's recommended model and effort, and do NOT
    present CLI commands as the only instruction:

    > 👉 **Would you like to switch to {Model} at {effort} reasoning effort for {this module | graduation}?** (Recommended for best value; set it with the model and effort controls in {Claude Desktop | the Claude web app | your Claude IDE extension}; reply no to keep your current {dial}.)

    Substitute the one interface the bootcamper is actually on. When the interface cannot be
    determined, say "in your Claude interface" — vague only where the plugin genuinely does not
    know, never as a shorthand for an interface it does know (INV-158).

    ⛔ **When the recommendation sits *below* the current setting, say so in the question itself.**
    Add one clause naming it as a step down, stating that the recommendation is about cost rather
    than capability and that staying put costs them nothing — e.g. "this is a step down from your
    current {current}; it is a cost saving, not a capability the module needs, so staying put is
    fine." Without it the bootcamper is being asked to accept a worse experience for no stated
    reason. It never reads as advice to downgrade. (An effort above the whole table never reaches
    this clause, and neither does a model above it such as Fable 5.1 — see the exemption above; it is
    a statement, not a question.)

    This switch turn ends at the 👉. **On yes, read what the dial is actually set to before you
    compose the reply** (INV-236). The question just handed the bootcamper a command, so many will
    run it in the same turn as their yes — that is the natural response to being shown a command,
    not an edge case. Three shapes, decided by the live setting rather than by the yes alone:

    1. **The dial is not yet set** — the ordinary case, unchanged. Open the reply turn with a
       one-line statement telling the bootcamper how to make the change (run the `/model`/`/effort`
       commands in the Claude Code CLI, or use the model and reasoning-effort controls in Claude
       Desktop / the Claude web app / their Claude IDE extension — naming only the dial that is
       moving), then end the turn on this pinned confirmation gate (its question verbatim,
       INV-056/INV-069 — only the answer hint adapts to the interface) — do NOT show Step 1 yet:

       > 👉 **Are you done modifying the model and effort?** (Reply yes once you've set your model and effort; reply no if you need more time.)

       Step 1 comes on the turn **after** the bootcamper confirms. If they reply no / "not yet",
       acknowledge and wait for their go-ahead, then present Step 1 — do not re-ask this gate
       (ask-once, INV-006).

    2. **The dial is already at the recommended value** — they ran it themselves.
       **Acknowledge it instead of instructing it** — "You're on `/effort medium` already: that's
       this module's recommendation." — and present Step 1 **in the same turn**, with **no**
       confirmation gate. Nothing is left to confirm, so asking is the pointless question INV-006
       and INV-012 forbid, and this is the case where INV-064's single-turn continuation is
       genuinely correct.

    3. **The dial is already at a different value** — state what is in force and leave it there:
       "You're on `/effort xhigh`; this module recommends `medium`, and running higher is fine — it
       simply costs more, nothing else." Then present Step 1 in the same turn, no gate. ⛔ **Never
       re-instruct the recommended command once the bootcamper has set a different value.** They
       answered the question with an action, and the table is a recommended floor for value, not a
       ceiling — repeating it names a value they just deliberately rejected. This reuses the
       above-the-table wording on purpose ("running higher is fine", "simply costs more"), so the
       two statements of the same idea cannot drift apart.

    ⛔ **Shapes 2 and 3 skip the confirmation gate; shape 1 keeps it.** The gate exists to give the
    bootcamper a window in which to run the commands — a bootcamper who has already run them does
    not need one, and gating anyway asks a question the transcript has answered.

    ⚠️ **Interface-aware, like the question itself.** In Claude Desktop, the Claude web app or a
    Claude IDE extension, shapes 2 and 3 name the **setting** rather than a command — "you're
    already on {Model} at {effort} reasoning effort" — since those bootcampers can change it before
    replying just as readily (INV-158).

    On **no** to the switch, acknowledge and present Step 1 the same reply
    turn, ending on **the next single 👉 question**. That is Step 1's own 👉 when it has one — and
    when Step 1 is **non-yielding**, it is the 👉 of the next step that asks, with the intervening
    steps executed in the same turn (see the 👉 protocol). Module 1's Step 1 is exactly this case:
    a privacy reminder that asks nothing, so the turn ends on Step 2's question.
  - **The recommendation matches what they are already running** → a brief one-line statement; no
    question, so the bootcamp never asks a pointless "switch?" every module (INV-012). The statement
    names the recommended model and effort as **separate dials**, notes either can be
    changed at any time and applies from the next message, and — when the recommendation sits
    *below* the current setting — says so explicitly with why the carve-out may not apply, so it
    never reads as advice to downgrade.

  ⛔ **You never change the session yourself — only the bootcamper can.** That is why the switch is
  offered as a question rather than performed. The "Are you done modifying the model and effort?"
  gate follows a **yes that still needs one** — shape 1 above — and nothing else: never after a
  decline, never when the recommendation already matched, and never in shapes 2 and 3, where the dial
  is already set and the gate would ask what the transcript has answered.

  Switching is always optional — running one model for everything (Opus 5.5) stays valid. Per-stage
  recommendation — **this table is the authoritative copy** (the one in
  `../../docs/model-selection.md` is derived from it; change this one first). Model names, IDs, and
  the values below are point-in-time and go stale when a new model ships; `docs/model-selection.md`
  carries the dated verification note, and `tests/test_model_guidance_sync.py` fails if the two
  tables drift or if any superseded model name survives (INV-114):

  **One row per stage, in the order the bootcamp runs them** — so the next stage's recommendation
  can be read off directly, and so no stage is ever missing a value to compare against. Each row
  names exactly **one** model and **one** effort: a conditional recommendation cannot be pinned into
  a verbatim question (INV-056) and gives the comparison above two answers.

  | Stage | Recommended | CLI commands |
  |---|---|---|
  | Onboarding | Sonnet 5.5, medium effort | `/model sonnet` · `/effort medium` |
  | Bootcamp preparation | Sonnet 5.5, medium effort | `/model sonnet` · `/effort medium` |
  | Entity Resolution Concepts | Sonnet 5.5, medium effort | `/model sonnet` · `/effort medium` |
  | Discover the Business Problem | Sonnet 5.5, medium effort | `/model sonnet` · `/effort medium` |
  | SDK setup | Opus 5.5, high effort | `/model opus` · `/effort high` |
  | System verification | Sonnet 5.5, high effort | `/model sonnet` · `/effort high` |
  | Truth Set visualization | Opus 5.5, high effort | `/model opus` · `/effort high` |
  | Data collection | Sonnet 5.5, medium effort | `/model sonnet` · `/effort medium` |
  | Data Quality, Mapping, and Transformation | Opus 5.5, high effort | `/model opus` · `/effort high` |
  | Data processing | Opus 5.5, high effort | `/model opus` · `/effort high` |
  | Query, Visualize and Discover | Opus 5.5, high effort | `/model opus` · `/effort high` |
  | Bootcamp graduation | Opus 5.5, high effort | `/model opus` · `/effort high` |

  The **Recommended** column is interface-neutral. In Claude Desktop, the Claude web app, or a Claude
  IDE extension, set the same model and reasoning effort using that interface's model/effort controls;
  the **CLI commands** column is the Claude Code CLI equivalent (INV-098).

  ⚠️ **These effort values are a recommended floor for value, not a ceiling.** The table never goes
  above `high`, and the dial goes further (`xhigh`, `max`). Running above the table is **in policy**
  and simply costs more — it is not an over-setting to be corrected, which is why an effort above
  every row is exempt from the comparison above. `high` was chosen as the top row because there is no
  evidence the modules need more, not because more is disallowed (see
  `../../docs/model-selection.md` → considered and rejected).

  From Data Quality, Mapping, and Transformation onward the recommendation is **flat** — a
  bootcamper who switches there is asked nothing further for the rest of the bootcamp.

  Onboarding, Bootcamp preparation and Entity Resolution Concepts appear in this table only so the
  nudge always has a value on both sides of the comparison; being apparatus-exempt
  (INV-075/INV-078), those setup stages present no model/effort nudge themselves (see the carve-out
  above).
