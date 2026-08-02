#!/usr/bin/env python3
"""Opt-in Stop hook for claude-tend.

Once per session, when the session tries to finish inside a git repo, asks the
model to consider running the `tend` skill first. The model stays the judge of
"significant" — a trivial session just finishes.

Wire it up in ~/.claude/settings.json (adjust the path to your clone):

    {
      "hooks": {
        "Stop": [
          {
            "hooks": [
              { "type": "command",
                "command": "python3 /absolute/path/to/claude-tend/hooks/stop-nudge.py" }
            ]
          }
        ]
      }
    }
"""
import json
import os
import subprocess
import sys
import tempfile


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    # Already continuing because a Stop hook blocked — never block again (loop guard).
    if data.get("stop_hook_active"):
        return
    session_id = data.get("session_id") or "unknown"
    marker = os.path.join(tempfile.gettempdir(), f"claude-tend-nudge-{session_id}")
    if os.path.exists(marker):  # one nudge per session
        return
    cwd = data.get("cwd") or os.getcwd()
    probe = subprocess.run(
        ["git", "-C", cwd, "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return  # not a project; nothing to tend
    open(marker, "w").close()
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": (
                    "claude-tend nudge (fires once per session): if this session did "
                    "significant work in this repo — a nontrivial change, surprising "
                    "debugging, corrected assumptions — run the `tend` skill to fold "
                    "what was learned into CLAUDE.md before finishing. If the session "
                    "was trivial, just finish."
                ),
            }
        )
    )


if __name__ == "__main__":
    main()
