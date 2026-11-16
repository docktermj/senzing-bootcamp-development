# How each assistant can adjust reasoning effort

Research for [issue #5](https://github.com/docktermj/senzing-bootcamp-development/issues/5),
done on 2026-11-16. It answers one question for
[issue #4](https://github.com/docktermj/senzing-bootcamp-development/issues/4): can the bootcamp
match reasoning effort to each stage without the bootcamper doing anything, and without making
the assistant re-process the conversation?

Terms used here:

- **Reasoning effort** is the assistant's setting that trades depth of thinking for speed and cost.
- **Main session** is the conversation the bootcamper is having.
- **Helper agent** is a second agent the assistant starts for one task. It runs in its own
  context, does not see the conversation and returns only its result.
- **Conversation cache** is the provider's cache of the conversation so far. Losing it means the
  next request re-processes the whole history.

## Findings

| Assistant | Main session: can a package change effort? | Helper agent at a chosen effort? | Effect on the conversation cache | Verified |
|---|---|---|---|---|
| Claude (Claude Code) | **Yes, for one turn.** A skill's `effort:` frontmatter applies for the rest of the turn that invokes it, then the session's level returns. | **Yes.** A plugin agent's `effort:` frontmatter. | Kept in both cases in the live check. The documentation says an effort change keeps the cache only on current models with an API key or a Claude subscription. | Live, Claude Code 2.1.325, 2026-11-16 |
| GitHub Copilot | None found. Skill frontmatter has no effort key, and no hook output carries one. | **Documented, not confirmed.** An agent file's `reasoningEffort` is documented; in the live check the helper agent ran at the session's effort instead. | Not measured. Automatic modes are documented to route "along natural cache boundaries". | Live, Copilot CLI 1.0.112, 2026-11-16 |
| Kiro | None found. Skills, Powers and custom agents have no effort field. | None a package can use. Only a workflow step can set effort, a workflow needs the bootcamper's approval before it runs, and a Power is not documented to ship one. | Not documented for an effort change. A model handoff compacts the conversation. | Documentation only |
| ChatGPT (Codex) | None found. Skills have no effort field, and hook output cannot change a request. | **Documented.** A custom agent file sets `model_reasoning_effort` for that agent. Whether a plugin can ship one is not documented. | Not documented by Codex. An open community report says a new effort level loses the cache. | Documentation only |
| Gemini (Antigravity) | None found. Effort is a model variant chosen by the bootcamper. | **Model tier only.** A plugin agent's `model` takes a tier; there is no effort key. | Not documented. | Documentation only |

## What the live checks showed

### Claude Code 2.1.325

One resumed session on Opus 5.5 under a Claude subscription, with a scratch plugin holding one
skill (`effort: low`), one agent (`effort: low`) and a `PreToolUse` hook that logged the
`effort.level` field of its input. The session's own level was `high`.

| Turn | Effort the hook saw | Cache read (tokens) | Cache written (tokens) |
|---|---|---|---|
| Plain request | high | 59,142 | 0 |
| Plain request | high | 59,320 | 180 |
| Skill typed as a command | **low** | 59,828 | 331 |
| Plain request | high | 60,283 | 120 |
| Helper agent | **low**, inside the agent | 60,660 | 550 |
| Plain request | high | 61,709 | 206 |

- The skill's level applied for its turn and the session's level came back on the next turn.
- The same held when the assistant invoked the skill itself: a tool call before the skill in that
  turn ran at `high` and the skill's own tool call ran at `low`.
- No turn re-processed the conversation. Each read the history from cache and wrote a few hundred
  new tokens.

### Copilot CLI 1.0.112

A scratch plugin with one agent file declaring `reasoningEffort: low`, run twice: once with the
session at `high` and once at the default, `medium`. Copilot's own event stream reported the
helper agent as configured at `high` and then at `medium`, with the model selection source
`session_inheritance`. The declared level was not applied either time.

The documentation says a declared effort "that can't be honored falls back to the session's
value". The check does not show why it fell back here, so this row stays unconfirmed, not
disproved.

### Kiro

No live check was run. The acceptance criterion asks for one for each mechanism reported as
found, and none was found. Kiro's session record from the 2026-11-15 bootcamp runs shows the
session's model (`auto`) and no effort value.

## Automatic modes

No assistant documents a way for a package to detect that the bootcamper selected an automatic
mode.

- **GitHub Copilot.** Auto picks the model. Copilot Fusion is documented to pick "the right level
  of reasoning effort" as well. Hook input carries no model or effort field.
- **Kiro.** Auto routes between models. Whether it picks effort is not documented.
- **Gemini (Antigravity).** Orchestrator pairs two models and has a fixed thinking level.
- **Claude and ChatGPT (Codex).** No automatic effort mode is documented.

## What was not verified

- Claude on other models, and through Amazon Bedrock, Google Cloud or Microsoft Foundry, where the
  documentation says an effort change loses the cache.
- Why Copilot did not apply the agent's declared effort, and what a manual model or effort switch
  does to Copilot's cache.
- Everything about Kiro, ChatGPT (Codex) and Gemini (Antigravity): those rows come from
  documentation read through a summarizing fetch, so their quoted wording may be inexact.
- Whether a Codex plugin can ship a custom agent, and whether Antigravity's helper agents inherit
  the session's effort.

## Recommendation for issue #4

**Use instructions only, on every assistant.**

1. **Instructions everywhere.** Each stage tells the assistant how carefully to work: verify more
   on the hard stages, move briskly on the simple ones. This is the only mechanism available on
   all five assistants. It touches no setting, so it cannot lose the conversation cache, and it
   leaves an automatic mode free to decide for itself.
2. **No skill `effort:` setting on Claude.** It is the one main-session mechanism found, it is
   verified live and it kept the cache, and it still does not fit. It lasts only for the turn that
   loads a skill. A bootcamp module is loaded once and then runs for many turns, each one a new
   request from the bootcamper, so the setting would cover the turn that opens a module and none
   of the turns that do its work. The build also requires skill frontmatter every assistant reads.
3. **No helper agents for the bootcamp's stages.** A helper agent does not see the conversation,
   and the bootcamp's stages depend on it: the bootcamper's answers, their data and the one
   question at a time. Only Claude's was confirmed live, and Copilot's did not take effect.

The consequence for issue #4 is that "effort follows the task" is guidance to the assistant on all
five assistants, the same text in every package, and no package changes a setting. An earlier
version of this section recommended adding the skill `effort:` setting on Claude; it was corrected
on 2026-11-16 for the reason in item 2.

## Sources

- Claude: <https://code.claude.com/docs/en/model-config.md>,
  <https://code.claude.com/docs/en/skills.md>, <https://code.claude.com/docs/en/sub-agents.md>,
  <https://code.claude.com/docs/en/hooks.md>, <https://code.claude.com/docs/en/prompt-caching.md>
- GitHub Copilot:
  <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference>,
  <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference>,
  <https://docs.github.com/en/copilot/reference/hooks-configuration>,
  <https://docs.github.com/en/copilot/concepts/models/auto-model-selection>,
  <https://docs.github.com/en/copilot/concepts/models/copilot-fusion>
- Kiro: <https://kiro.dev/docs/models/effort/>, <https://kiro.dev/docs/skills/>,
  <https://kiro.dev/docs/powers/create/>, <https://kiro.dev/docs/custom-agents/configuration-reference/>,
  <https://kiro.dev/docs/workflows/authoring/>, <https://kiro.dev/docs/hooks/types/>
- ChatGPT (Codex): <https://learn.chatgpt.com/docs/config-file/config-reference.md>,
  <https://learn.chatgpt.com/docs/agent-configuration/subagents.md>,
  <https://learn.chatgpt.com/docs/build-skills.md>, <https://learn.chatgpt.com/docs/hooks.md>,
  <https://github.com/openai/codex/issues/42996>
- Gemini (Antigravity): <https://antigravity.google/docs/models.md>,
  <https://antigravity.google/docs/cli/commands/effort.md>,
  <https://antigravity.google/docs/build-plugins.md>, <https://antigravity.google/docs/subagents.md>,
  <https://antigravity.google/docs/hooks.md>
