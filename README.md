# tend — keep project CLAUDE.md files sharp

A [Claude Code](https://claude.com/claude-code) skill that maintains your project-level `CLAUDE.md` after significant work: it harvests the session for non-obvious knowledge (gotchas discovered the hard way, commands that actually work, invariants the code doesn't announce), verifies existing claims against the current code, folds the survivors in, and prunes what went stale.

`/init` writes the first draft of a CLAUDE.md. `tend` is the maintenance half: it keeps the file true.

## Install

As a plugin (recommended):

```
/plugin marketplace add alexgaoth/claude-tend
/plugin install tend
```

Via [skills.sh](https://skills.sh/) (installs the skill for Claude Code and other agents):

```
npx skills add alexgaoth/claude-tend
```

Or manually — copy `skills/tend/SKILL.md` to `~/.claude/skills/tend/SKILL.md` and restart your session.

## Use

At the end of (or during) a session that did real work in a repo:

```
/tend
/tend the build tooling        # optional focus area
```

Claude can also invoke it on its own after finishing significant work — the skill's description invites that — but model-invocation is best-effort. For a deterministic reminder, see the hook below.

## What it actually does

1. **Find** the right file — root `CLAUDE.md`, nested per-package ones, or `AGENTS.md` when that's the project's source of truth. Personal files (`CLAUDE.local.md`, `~/.claude/CLAUDE.md`) are never touched.
2. **Harvest** the session: what was discovered the hard way, what went wrong that one line would have prevented, rules the user stated, commands that actually work, invariants the code doesn't announce.
3. **Gate** every candidate — it must be non-obvious, durable, behavior-changing, and project-scoped, or it's dropped. Zero survivors means the skill says so and stops; no padding.
4. **Verify** existing claims in areas the session touched — stale commands and dead paths get fixed or deleted.
5. **Edit** in place — merge rather than append, facts at the right scope, a ~60-line target per file with hard pressure past ~100. The diff is summarized and left uncommitted for review.

## The philosophy

A `CLAUDE.md` is not documentation — it's **context every future session pays for**. Every line is loaded into every conversation in that repo, forever. So the skill is built around a budget, not a wiki:

- A line earns its place only if it **changes what an agent would do**.
- **Deleting a stale line is worth as much as adding a good one.** A wrong claim in CLAUDE.md is worse than no claim, because agents trust it over the code.
- The highest-value source is **friction**: the places where this session's agent guessed wrong are exactly where the next one will.

## How it lives (design notes)

- **User-level skill, project-level output.** The skill applies to every repo, so it installs once at user level. The knowledge it produces lands in each repo's committed `CLAUDE.md`, where every teammate's agent — and every future session — inherits it.
- **In-session, never a subagent or cron job.** The input is the session's lived experience: the failed commands, the corrections, the surprises. A fresh subagent or scheduled bot has no transcript to harvest; the most a cron job could do is staleness-checking, which is the lesser half of the job.
- **Three trigger tiers**, escalating in reliability:
  1. *Model-invoked* — the skill description invites Claude to run it after significant work. Zero setup, best-effort.
  2. *Manual* — `/tend` when you know the session earned it.
  3. *Hook-enforced* — an opt-in `Stop` hook that, once per session, asks the model to judge whether the session warrants a tend before finishing. Deterministic, at the cost of one extra model turn on the first stop inside a repo.

### The optional Stop-hook nudge

Add to `~/.claude/settings.json`, adjusting the path to your clone:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "python3 /absolute/path/to/claude-tend/hooks/stop-nudge.py" }
        ]
      }
    ]
  }
}
```

It fires at most once per session, only inside git repos, and always lets the model decide "this session was trivial, finish anyway." The `stop_hook_active` guard prevents blocking loops.

## License

MIT
