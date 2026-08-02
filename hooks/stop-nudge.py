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
import re
import subprocess
import sys
import tempfile


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if not isinstance(data, dict):
        return
    # Already continuing because a Stop hook blocked — never block again (loop guard).
    if data.get("stop_hook_active"):
        return
    # Marker filename must stay inside tempdir even for a hostile session_id.
    session_id = re.sub(r"[^A-Za-z0-9._-]", "_", str(data.get("session_id") or "unknown"))[:80]
    try:
        marker = os.path.join(tempfile.gettempdir(), f"claude-tend-nudge-{session_id}")
        if os.path.exists(marker):  # one nudge per session
            return
    except OSError:
        return  # no usable temp dir at all — never break the Stop event
    cwd = data.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()
    try:
        probe = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return  # git not installed — never break the Stop event
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return  # not a project; nothing to tend
    try:
        open(marker, "w").close()
    except OSError:
        return  # can't record "already nudged" — skip rather than risk re-nudging every stop
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
