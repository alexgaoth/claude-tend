# CLAUDE.md

## Gotchas

- Every failure path in `hooks/stop-nudge.py` must print nothing and exit 0 — output or a traceback there surfaces as an error on the user's Stop event. New code goes inside the existing guards; a new failure mode gets its own silent return.
- The hook dedupes via `${TMPDIR:-/tmp}/claude-tend-nudge-<session_id>`. Re-running with the same session_id is silently a no-op — delete the marker between manual tests, or the nudge "mysteriously" won't fire.
- The skill name `tend` is kept in sync by hand across four places: the `skills/tend/` directory name, the SKILL.md frontmatter `name:`, `.claude-plugin/plugin.json`, and the `plugins` entry in `.claude-plugin/marketplace.json`. A rename or a new skill must touch all of them.
- `skills/tend/SKILL.md` stays under ~120 lines and its frontmatter description under 1024 chars — the description is what drives model auto-invocation, and the skill must practice the budget it preaches.
- README behavior claims are testable guarantees (fail-silent, once-per-session, git-repos-only), not prose: any change to hook or skill behavior must update the matching README sentence.

## Testing the hook

No test framework — verify by piping payloads from the repo root:

    echo '{"session_id":"t1","cwd":"'$PWD'"}' | python3 hooks/stop-nudge.py   # block JSON, exit 0
    # same session_id again → silence; "stop_hook_active": true → silence; non-git cwd → silence
    echo not-json | python3 hooks/stop-nudge.py                               # silence, exit 0
    rm -f "${TMPDIR:-/tmp}/claude-tend-nudge-t1"

When touching marker code, also cover the no-tempdir path: monkeypatch `tempfile.gettempdir` to raise `FileNotFoundError`, run the script via `runpy` — it must stay silent and exit 0.
