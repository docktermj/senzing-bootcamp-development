
  ⛔ **This is the ONLY {{host.assistant}}-interface control the bootcamp asks the bootcamper to
  operate (INV-247).** It is an exception, not a precedent: no other session- or host-level setting
  — an automatic or auto-approve mode, a permission mode, a planning mode, background tasks, or
  compacting the conversation — is ever offered as a bootcamp question, and a new nudge in that
  shape must not be added here or anywhere else. Read the closed-question-set rule in the 👉
  protocol before adding one. This limit is stated here because *this* section is what creates the
  expectation: a bootcamper who has just been asked to set the model and effort for this module has
  no way to tell an unsanctioned interface question from bootcamp content.

  Like the step overview and the time estimate, this is module-start apparatus, so
  the apparatus-exempt setup modules (Bootcamp preparation, Module 0) do not present it (INV-063
  clarification). **Phrase it by intent** (INV-098): name the recommended model and
  reasoning-effort level, and direct the bootcamper to {{host.model_controls}}, without hardcoding
  a UI label that may drift. Where {{host.product}} offers no reasoning-effort setting, or offers
  different levels, name the nearest level it offers and say that it is the nearest.

  ⛔ **Name the interface (INV-158).** Say which {{host.assistant}} interface a control is in,
  as "Naming the {{host.assistant}} interface" above lists them, and say "in your
  {{host.assistant}} interface" only when the interface genuinely cannot be determined.

  ⛔ **This behavior is unconditional — there is no preference to read and no mode to choose
  (INV-137).** The bootcamp is never asked how it wants model guidance handled, and there is no
  `model_guidance` key.

  ⛔ (INV-138) **For every dial whose current value can be determined, compare the recommendation
  against what the bootcamper is running right now — not against the previous stage's
  recommendation.** A dial that cannot be determined is the one exception, and the proxy at the end
  of this paragraph is its rule. When you are told which model you are running, read the
  model side from that; for effort, use the value in force when you can determine it. **Resolve
  "cannot be determined" PER DIAL, not for the setting as a whole** — model and effort are separate
  dials (INV-137), and in a live session they routinely sit in different epistemic states at the
  same moment: the model is often knowable to the assistant, while the reasoning effort often is
  not. So compare each dial on its own evidence: a determinable
  model is compared **directly** even when effort is not, and vice versa. **Only for a dial whose
  current value cannot be determined**, and has never been determined in this conversation, use the
  **proxy**: compare this stage's recommended value for that dial against the recommended value for
  it in the stage just completed (that stage's row in the table below, INV-138's "previous stage's
  row"), and ask that dial's half only when the two differ; when the two are the same, treat that
  dial as matching.
  ⛔ (INV-138) **The proxy is the only sanctioned recommendation-to-recommendation comparison.** It
  exists because such a dial has no current value to compare, and it is the previous-stage fallback
  the rest of this section refers to.

  ⛔ **A dial is determinable from the moment this conversation shows its value.** The switch flow
  below asks the bootcamper to change a setting and then gates on "👉 Are you done modifying the
  model and effort?". So once the bootcamper has said what they set, or the conversation otherwise
  shows it, that dial **is** determinable, and the previous-stage fallback MUST NOT be used for it.
  Read the most recent such value, not the earliest — and compare it against the stage's
  recommendation, never against the previous stage's recommendation.
  ⛔ Applying the previous-stage row to a dial that *was* determinable is the failure this clause
  exists to prevent: a bootcamper demonstrably on {{host.model_capable}} would be compared against
  the previous stage's recommended {{host.model_balanced}}, found "unchanged", and never offered the
  switch. Comparing recommendation-to-recommendation asks a bootcamper already on
  {{host.model_capable}} at high effort "would you like to switch to {{host.model_capable}} at high
  effort?" — a question whose answer changes nothing, which is exactly what INV-006 and INV-012
  forbid. Running one model for the whole bootcamp is a supported choice, so this is the common
  case, not an edge case.

  ⛔ **One dial is exempt from the comparison before it starts: a setting ABOVE everything
  the table ever recommends.** The table's highest effort is `high`. A bootcamper who has chosen a
  higher effort, or a model more capable than the table's top row, sits above **every remaining
  row**, so a step-down question would fire at every module for the rest of the bootcamp. Treat the
  recommendation as **satisfied**: give the one-line statement (the "matches" case below), name the
  stage's recommended value, and say plainly that running higher is fine. Ask **nothing** about
  that dial. A deliberate over-provision is not a mismatch to correct, and re-offering it every
  module is the "pointless switch? every module" outcome INV-006 and INV-012 forbid.

  ⚠️ **This is narrower than it may look, and deliberately so.** It applies only *above the whole
  table*, never to a step down **within** it — a bootcamper on {{host.model_capable}} / high
  entering a {{host.model_balanced}} / medium stage is still asked, both dials (INV-139).

  Two cases, decided only by that comparison:

  - **The recommendation differs from the current setting** — in **either** direction. A step down
    asks just as a step up does: the choice is the bootcamper's both ways. End the turn with a
    **single** 👉 yes/no question offering the switch, and do NOT also show Step 1 this turn
    (exactly one 👉 per turn — INV-251; INV-008/INV-009 govern each question's clarity, not the count).

    **Name only the dial that differs.** Model and effort are **separate dials**: a bootcamper on
    {{host.model_capable}} at medium effort entering a stage recommending {{host.model_capable}} at
    high effort is asked to change the effort only, never told to re-set the model they are already on.

    ⛔ **That rule covers the whole sentence, including the answer hint** — `{dial}` below resolves
    to "model", "effort", or "model and effort", matching whatever the stem names (INV-056).

    Pin the switch question verbatim, substituting only the bracketed values — the stage's
    recommendation, just the one dial when only one differs, and `{dial}` to match:

    > 👉 **Would you like to switch to {Model} at {effort} reasoning effort for {this module | graduation}?** (Recommended for best value; set it with {{host.model_controls}}; reply no to keep your current {dial}.)

    ⛔ **When the recommendation sits *below* the current setting, say so in the question itself.**
    Add one clause naming it as a step down, stating that the recommendation is about cost rather
    than capability and that staying put costs them nothing — e.g. "this is a step down from your
    current {current}; it is a cost saving, not a capability the module needs, so staying put is
    fine." Without it the bootcamper is being asked to accept a worse experience for no stated
    reason. It never reads as advice to downgrade.

    This switch turn ends at the 👉. **On yes, read what the dial is actually set to before you
    compose the reply** (INV-236). Many bootcampers change the setting in the same turn as their
    yes. Three shapes, decided by the live setting rather than by the yes alone:

    1. **The dial is not yet set** — the ordinary case. Open the reply turn with a one-line
       statement telling the bootcamper how to make the change (with {{host.model_controls}} —
       naming only the dial that is moving), then end the turn on this pinned confirmation gate
       (its question verbatim, INV-056/INV-069) — do NOT show Step 1 yet:

       > 👉 **Are you done modifying the model and effort?** (Reply yes once you've set your model and effort; reply no if you need more time.)

       Step 1 comes on the turn **after** the bootcamper confirms. If they reply no / "not yet",
       acknowledge and wait for their go-ahead, then present Step 1 — do not re-ask this gate
       (ask-once, INV-006).

    2. **The dial is already at the recommended value** — they set it themselves.
       **Acknowledge it instead of instructing it** — "You're already on {Model} at {effort}
       reasoning effort: that's this module's recommendation." — and present Step 1 **in the same
       turn**, with **no** confirmation gate (INV-006, INV-012, INV-064).

    3. **The dial is already at a different value** — state what is in force and leave it there,
       saying that running higher is fine and simply costs more. Then present Step 1 in the same
       turn, no gate. ⛔ **Never re-instruct the recommendation once the bootcamper has set a
       different value.** The table is a recommended floor for value, not a ceiling.

    ⛔ **Shapes 2 and 3 skip the confirmation gate; shape 1 keeps it.**

    On **no** to the switch, acknowledge and present Step 1 the same reply
    turn, ending on **the next single 👉 question**. That is Step 1's own 👉 when it has one — and
    when Step 1 is **non-yielding**, it is the 👉 of the next step that asks, with the intervening
    steps executed in the same turn (see the 👉 protocol).
  - **The recommendation matches what they are already running** → a brief one-line statement; no
    question, so the bootcamp never asks a pointless "switch?" every module (INV-012). The statement
    names the recommended model and effort as **separate dials**, notes either can be
    changed at any time, and — when the recommendation sits *below* the current setting — says so
    explicitly, so it never reads as advice to downgrade.

  ⛔ **You never change the session yourself — only the bootcamper can.** That is why the switch is
  offered as a question rather than performed. The "Are you done modifying the model and effort?"
  gate follows a **yes that still needs one** — shape 1 above — and nothing else.

  Switching is always optional — running one model for everything stays valid. Per-stage
  recommendation, by how capable a model the stage is worth (INV-114):

  **One row per stage, in the order the bootcamp runs them** — so the next stage's recommendation
  can be read off directly, and so no stage is ever missing a value to compare against. Each row
  names exactly **one** model and **one** effort (INV-056).

  | Stage | Recommended |
  |---|---|
  | Onboarding | {{host.model_balanced}}, medium effort |
  | Bootcamp preparation | {{host.model_balanced}}, medium effort |
  | Entity Resolution Concepts | {{host.model_balanced}}, medium effort |
  | Discover the Business Problem | {{host.model_balanced}}, medium effort |
  | SDK setup | {{host.model_capable}}, high effort |
  | System verification | {{host.model_balanced}}, high effort |
  | Truth Set visualization | {{host.model_capable}}, high effort |
  | Data collection | {{host.model_balanced}}, medium effort |
  | Data Quality, Mapping, and Transformation | {{host.model_capable}}, high effort |
  | Data processing | {{host.model_capable}}, high effort |
  | Query, Visualize and Discover | {{host.model_capable}}, high effort |
  | Bootcamp graduation | {{host.model_capable}}, high effort |

  ⚠️ **These effort values are a recommended floor for value, not a ceiling.** The table never goes
  above `high`. Running above the table is **in policy** and simply costs more — it is not an
  over-setting to be corrected, which is why a setting above every row is exempt from the
  comparison above.

  From Data Quality, Mapping, and Transformation onward the recommendation is **flat** — a
  bootcamper who switches there is asked nothing further for the rest of the bootcamp.

  Onboarding, Bootcamp preparation and Entity Resolution Concepts appear in this table only so the
  nudge always has a value on both sides of the comparison; being apparatus-exempt
  (INV-075/INV-078), those setup stages present no model/effort nudge themselves (see the carve-out
  above).
