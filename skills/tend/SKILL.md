---
name: tend
description: Distill non-obvious knowledge learned this session into the project's CLAUDE.md (or AGENTS.md) and prune what went stale, so future agents start smarter. Use after significant work in a repo - landing a nontrivial change, a debugging session that revealed a gotcha, discovering a documented command is wrong, or being corrected about a project convention. Also on "update CLAUDE.md", "document what we learned", "tend the docs". Usage - /tend [optional focus area]
---

# Tend — keep the project's CLAUDE.md true, short, and load-bearing

A project CLAUDE.md is read into every future session's context. Every line costs tokens in every session forever, so a line earns its place only by changing what an agent would do. You are as much a pruner as a writer: deleting a stale line is worth as much as adding a good one, and "nothing worth adding" is a valid outcome.

Run this in the session that did the work — the transcript is the input. A fresh subagent has nothing to harvest; never delegate this step.

If an argument was given, treat it as the focus area (e.g. `/tend the build tooling`), but still fix stale claims you notice elsewhere.

## 1. Find the files

- Project root: `git rev-parse --show-toplevel`; outside a git repo, the directory the work happened in. In scope: root `CLAUDE.md`, nested `CLAUDE.md` files in directories you worked in, and `AGENTS.md`.
- If the project keeps its agent docs in `AGENTS.md` (no `CLAUDE.md`, or `CLAUDE.md` is a symlink or one-line pointer to it), edit `AGENTS.md` instead.
- `CLAUDE.md` can import other files via `@path` lines. Follow imports when reading, and when a fact's natural home is an imported file (e.g. `@docs/testing.md`), edit it there — never duplicate it in the importer.
- Never edit `CLAUDE.local.md` or `~/.claude/CLAUDE.md` here — those are personal, not project docs.
- No file at all? Create a root `CLAUDE.md` only if step 2 produces real material. Never scaffold empty sections.

## 2. Harvest the session

Answer each question, collecting candidate facts:

- What did I discover the hard way — by trial, error, or grep — that one line would have told me upfront?
- Where was I wrong? A command that failed, a test I broke, a user correction, a review finding. What line would have prevented it?
- What did the user state as a project rule ("always X", "never Y", "we use Z here")?
- Which build / test / run / verify commands actually work, where the obvious guess fails?
- What invariant does the code not announce? Generated files, pairs kept in sync by hand, ordering constraints, load-bearing hacks.
- Which existing CLAUDE.md line did I misread, overlook, or find wrong? An instruction that failed to instruct is a bug — rewrite it so the next agent can't miss it.

This works the same outside software: a docs, research, or data project also has real commands, invariants, and gotchas.

Then filter every candidate through four gates; drop it unless ALL hold:

1. **Non-obvious** — two minutes of reading the project would not reveal it.
2. **Durable** — still true after this branch merges. Not narration of what we just did.
3. **Behavior-changing** — a future agent acts differently for knowing it.
4. **Project-scoped and committable** — personal preferences (how the user likes to be addressed, their formatting tastes) belong in their own global config, never in a committed team file. Same for secrets, tokens, and anything else that should not live in the repo.

Zero survivors is normal — never pad the file. But don't stop yet: run step 3's staleness check first. "Nothing to add and nothing stale" is the full no-op outcome; say so and stop there.

## 3. Verify before writing

- Read the current file(s) in full.
- Recheck existing claims that touch areas you worked in: do the referenced commands still exist (package.json / Makefile / justfile / scripts)? The paths? Is the described behavior still what you observed? Stale → fix or delete.
- Human-written rule lines ("always/never", style edicts) are authoritative: tighten or relocate them, never silently drop them. If one looks wrong, keep it and flag it to the user instead.

## 4. Edit

- Rewrite in place; don't append a new section at the end. Merge each fact where a reader would look for it.
- Right scope: package-specific facts go in that package's nested CLAUDE.md; repo-wide facts at root.
- One fact per line — imperative, concrete: the exact command, the path, the rule. Include a "why" only when the why is what prevents the mistake.
- Match the file's existing structure and voice. Creating fresh? Only sections you can actually fill (typically `## Commands`, `## Architecture`, `## Gotchas`).
- Budget: aim under ~60 lines per file; past ~100, compress or delete before adding. Added three lines? Look for three to remove.

## 5. Hand off

Summarize the diff for the user — one bullet per change, with a short why where it isn't self-evident. Leave the change uncommitted unless the flow you're in already commits, in which case include it in that commit.

## What earns a line

| ✗ Don't write | ✓ Write |
|---|---|
| "This project uses TypeScript with a src/ directory." | (nothing — obvious in seconds) |
| "We recently migrated from Jest to Vitest." | "Tests: `pnpm vitest run` — plain `pnpm test` is watch mode and hangs non-interactive shells." |
| "The database layer is important." | "`src/db/schema.ts` is generated — edit `schema.prisma`, then run `pnpm db:generate`." |
| "Be careful with error handling." | "Route handlers return `Result<T>`, never throw — thrown errors skip the audit-log middleware." |
| "Follow best practices for new endpoints." | "New endpoints need an entry in `openapi.yaml`; CI diffs it against the router." |

## Traps

- **Changelog trap** — "we just refactored X". That's git history, not guidance.
- **Tour-guide trap** — narrating the directory tree anyone can `ls`.
- **Wiki trap** — restating what the code says plainly. Long-form detail belongs in docs/, with at most a pointer here.
- **Hedge trap** — "consider", "generally", "might want to". If it isn't a rule, it doesn't earn a line.
- **Trophy trap** — recording what this session accomplished. The file is for the next agent, not about this one.
