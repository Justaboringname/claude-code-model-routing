# model-routing

A Claude Code skill that splits work between a top-tier main session (Mythos / Fable) and Opus subagents, and paces it against your plan's weekly usage bars.

一个 Claude Code skill:主会话用顶配模型(Mythos / Fable),子 agent 用 Opus,并对照订阅的周额度条控制节奏。

[English](#english) · [中文](#中文)

## English

### Why

On a Claude subscription, Mythos 5.2 and Fable 5.2 drain the plan much faster than Opus 5.5:

| | Mythos / Fable 5.2 | Opus 5.5 | Ratio |
|---|---|---|---|
| Input / output list price, per million tokens | $8 / $40 | $4 / $20 | 2× |
| Cache read list price | $0.20 | $0.20 | 1× |
| Plan usage taken per list-price dollar | | | about 2.5× |

That is about 4× per token for a cache-heavy Claude Code session, 5× at most. The top-tier models can also use at most half of the weekly allowance, so a week spent only on them leaves the other half unused.

The 2.5× and 4× figures come from one account's usage logs in November 2026. Anthropic does not publish them.

### What the skill does

- Keeps the main session on the top-tier model for decomposing the task, deciding, accepting results and talking to you.
- Sends everything else to Opus subagents, with the model named on every spawn.
- Tries Opus first and redoes a piece on the top tier only when the Opus result fails acceptance.
- Runs a pace check before fanning out: each usage bar against the even-burn line (percent used against percent of the week elapsed), with one verdict that says hold, back off, or escalate.

### Install

```bash
git clone https://github.com/Justaboringname/claude-code-model-routing ~/.claude/skills/model-routing
```

Start a new Claude Code session. The skill loads when a task is about to spawn subagents, or when you ask about model split or quota pacing. To make it apply to every task, add a line to your `~/.claude/CLAUDE.md`:

```markdown
Before spawning subagents or a workflow, follow the `model-routing` skill.
```

### The pace check on its own

```bash
python3 ~/.claude/skills/model-routing/scripts/pace.py --weekly 40 --top 70 --resets-at 2026-11-25T05:00:00Z
```

```text
window: 50.0% elapsed, resets in 3d 12h
bar        used  line  delta  projected
weekly      40%   50%    -10        80%
top-tier    70%   50%    +20       140%
verdict: BACK_OFF_TOP
action:  Top-tier is burning ahead of the line. Main session delegates more to Opus and keeps its context small. No top-tier subagents.
```

`--weekly` is the all-models bar and `--top` is the Fable bar from `/usage`. Add `--session` on plans with a 5-hour window, `--margin` to change the 10-point tolerance, `--json` for machine output. Python 3.8+, standard library only.

| Verdict | When |
|---|---|
| `HOLD` | Both bars within the margin |
| `ROOM_TOP` | Top-tier bar behind the line |
| `USE_IT` | Under a day to reset with top-tier quota left |
| `BACK_OFF_TOP` | Top-tier bar ahead of the line |
| `BACK_OFF_ALL` | Weekly bar ahead of the line |
| `SESSION_FULL` | 5-hour window at 85% or more |
| `MINIMUM` | Weekly bar at 90% or more |
| `SWITCH_MAIN` | Top-tier bar at 90% or more |

## 中文

### 为什么

订阅里 Mythos 5.2 / Fable 5.2 吃额度比 Opus 5.5 快得多:

- 输入、输出、缓存写的标价是 Opus 的 2 倍($8 / $40 对 $4 / $20),缓存读同价($0.20)。
- 每 1 美元标价的用量,吃掉的额度约是 Opus 的 2.5 倍。
- 合起来,Claude Code 这种缓存读占大头的用法约 4 倍,上限 5 倍。
- 顶配模型最多只能用周额度的一半,只用它等于另一半白扔。

2.5 倍和 4 倍来自一个账号 2026 年 11 月的用量日志,Anthropic 没有公布过。

### 它做什么

- 主会话留在顶配模型上,只做拆任务、定方案、验收和对话。
- 其余的活交给 Opus 子 agent,每次起 agent 都写明模型。
- 先让 Opus 做,结果没过验收再用顶配重做那一块。
- 起多个 agent 之前查一次配速:每条额度对照匀速线(已用百分比对本周已过百分比),给出一个结论:照常、收一收,还是可以升档。

### 安装

```bash
git clone https://github.com/Justaboringname/claude-code-model-routing ~/.claude/skills/model-routing
```

开一个新的 Claude Code 会话即可。想让它对每个任务都生效,在 `~/.claude/CLAUDE.md` 里加一行:

```markdown
起子 agent 或 workflow 之前,先按 `model-routing` skill 查配速、定模型。
```

### 单独跑配速脚本

用法和输出见上面英文部分。`--weekly` 填 `/usage` 里的全模型周条,`--top` 填 Fable 条。

## License

MIT
