---
name: model-routing
description: Split Claude Code work between a top-tier main session (Mythos / Fable) and Opus subagents, and pace it against the plan's weekly usage bars. Use before spawning subagents or a workflow on any multi-step task, and when the user asks about model split, quota pacing, 模型分工 or 额度配速.
---

# Model routing: top-tier main session, Opus workers

_Last updated: 2026-11-18_

## Why two tiers

On a Claude subscription the top-tier models (Mythos 5.2, Fable 5.2) drain the plan far faster than Opus 5.5:

- List price is 2× Opus for input, output and cache writes ($8 / $40 against $4 / $20 per million tokens). Cache reads cost the same ($0.20).
- Each list-price dollar of top-tier usage takes about 2.5× as much of the plan's bars as a dollar of Opus.
- Together that is about 4× per token for a typical cache-heavy Claude Code session, and 5× at most.
- Top-tier models can use at most half of the weekly allowance. A week spent only on the top tier leaves the other half unused.

The 2.5× and 4× figures were measured on one account in November 2026. Treat them as estimates.

So the top-tier model does the part only it does well, and Opus does the rest. There is no third tier: Sonnet and Haiku save little against the plan's bars and cost quality.

## The split

| Who | Model | Does |
|---|---|---|
| Main session | whatever top-tier model the user picked | decomposes the task, decides the approach, accepts or rejects results, talks to the user |
| Subagents and workflow agents | Opus 5.5 | everything else: reading, searching, web fetching, writing code, debugging, review, drafting |

Rules:

1. **Name the model on every spawn.** `Agent` calls take `model: "opus"`. Workflow `agent()` calls take `{ model: 'opus' }`. A spawn with no model inherits the main session's model.
2. **The main session reads little.** Every main-session turn re-reads its whole context at top-tier rates. Hand file sweeps, long documents, logs and web pages to an Opus subagent and keep the conclusion.
3. **Opus first, top tier second.** Give the work to Opus. If the result fails acceptance (tests fail, the agent says it is unsure, a spot check finds a mistake), redo that piece in the main session or with a top-tier subagent.
4. **Top-tier subagents are the exception.** Use one only when the user names it, or when the pace check below says there is room. Say so in one line before spawning.
5. If the main session is already on Opus, everything runs on Opus and only the pace check applies.

## Pace check

Run it before the first spawn of a task, and again before each further fan-out of three or more agents.

1. Read the plan's usage: the weekly all-models bar, the weekly top-tier bar (labelled Fable), and when they reset. In the Claude desktop app, call `mcp__ccd_session_mgmt__get_usage`. Elsewhere, use whatever usage tool the session has, or ask the user for the numbers from `/usage`.
2. Run the script with those numbers:

   ```bash
   python3 ~/.claude/skills/model-routing/scripts/pace.py --weekly 5 --top 9 --resets-at 2026-11-25T05:00:00Z
   ```

   On a plan with a 5-hour window, add `--session <percent> --session-resets-at <time>`.
3. Follow the verdict.

The script compares each bar with the even-burn line: percent used against percent of the week elapsed. A bar more than 10 points off the line changes the verdict (`--margin` adjusts this).

| Verdict | Meaning | What to do |
|---|---|---|
| `HOLD` | On pace | Default split |
| `ROOM_TOP` | Top-tier bar is behind the line | Hard subtasks (review, stubborn bugs, final synthesis) may go to top-tier subagents |
| `USE_IT` | Less than a day to reset with top-tier quota left | Escalate freely; unused quota expires |
| `BACK_OFF_TOP` | Top-tier bar is ahead of the line | Main session delegates more and keeps its context small; no top-tier subagents |
| `BACK_OFF_ALL` | Weekly bar is ahead of the line | Fewer agents, lower effort on mechanical stages, no top-tier subagents |
| `SESSION_FULL` | 5-hour window at 85% or more | Finish the current step; hold new fan-outs until it resets |
| `MINIMUM` | Weekly bar at 90% or more | Only what was asked, no extra fan-out |
| `SWITCH_MAIN` | Top-tier bar at 90% or more | Suggest the user switch the main session to Opus |

Report the verdict to the user in one short line when it is anything other than `HOLD`.

## When usage can't be read

Use the default split and skip the escalations: main session on the top-tier model, every subagent on Opus, no top-tier subagents.
