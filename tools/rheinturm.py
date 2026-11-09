#!/usr/bin/env python3
"""Handle a "light up the Rheinturm" issue.

Input comes ONLY via environment variables (never interpolated into a shell):
  ISSUE_TITLE   e.g. "rheinturm: red"
  ISSUE_USER    GitHub login of the issue author
Writes state/rheinturm.json when the title names an allowed color and prints
`result=ok|invalid` and `color=<name>` for $GITHUB_OUTPUT.
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "rheinturm.json"

# name -> (light-mode fill, dark-mode fill)
COLORS = {
    "blue": ("#1d48c0", "#4d6fd0"),
    "red": ("#dc2626", "#ef4444"),
    "green": ("#16a34a", "#22c55e"),
    "purple": ("#7c3aed", "#8b5cf6"),
    "orange": ("#ea580c", "#f97316"),
    "pink": ("#db2777", "#ec4899"),
    "gold": ("#ca8a04", "#eab308"),
}
DEFAULT = {"color": "blue", "user": None, "at": None}


def load_state():
    try:
        s = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(DEFAULT)
    if s.get("color") not in COLORS:
        return dict(DEFAULT)
    user = s.get("user")
    if user is not None and not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", str(user)):
        s["user"] = None
    return s


def main():
    title = os.environ.get("ISSUE_TITLE", "")
    user = os.environ.get("ISSUE_USER", "")
    m = re.fullmatch(r"\s*rheinturm:\s*([a-z]+)\s*", title.lower())
    color = m.group(1) if m else ""
    valid_user = re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", user) is not None
    if color not in COLORS or not valid_user:
        print("result=invalid")
        return 0
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({"color": color, "user": user,
                                 "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")},
                                indent=2) + "\n", encoding="utf-8")
    print("result=ok")
    print(f"color={color}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
