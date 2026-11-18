#!/usr/bin/env python3
"""Pace check for a Claude plan's usage bars.

Compares each bar against the even-burn line (percent used == percent of the
window elapsed) and prints one verdict that says whether to keep the default
model split, back off, or escalate.

    pace.py --weekly 5 --top 9 --resets-at 2026-11-25T05:00:00Z
    pace.py --weekly 40 --top 62 --resets-at 2026-11-25T05:00:00Z \
            --session 85 --session-resets-at 2026-11-20T19:00:00Z

Standard library only. Python 3.8+.
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone


def parse_time(text):
    text = text.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    # Python < 3.11 only accepts 0, 3 or 6 fractional digits.
    if "." in text:
        head, rest = text.split(".", 1)
        digits = ""
        while rest and rest[0].isdigit():
            digits, rest = digits + rest[0], rest[1:]
        text = "%s.%s%s" % (head, (digits + "000000")[:6], rest)
    when = datetime.fromisoformat(text)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when


def percent(text):
    value = float(text)
    if not 0 <= value <= 100:
        raise argparse.ArgumentTypeError("percent must be between 0 and 100")
    return value


def span(delta):
    seconds = max(0, int(delta.total_seconds()))
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    if days:
        return "%dd %dh" % (days, hours)
    return "%dh %dm" % (hours, rest // 60)


VERDICTS = {
    "SWITCH_MAIN": "Top-tier bar is nearly spent. Suggest the user switch the main "
                   "session to Opus. No top-tier subagents.",
    "MINIMUM": "Weekly bar is nearly spent. Do only what was asked; no fan-out "
               "beyond what the task cannot do without.",
    "SESSION_FULL": "Session window is nearly full. Finish the current step and "
                    "hold new fan-outs until it resets.",
    "BACK_OFF_ALL": "The whole week is burning ahead of the line. Fewer agents, "
                    "lower effort on mechanical stages, no top-tier subagents.",
    "BACK_OFF_TOP": "Top-tier is burning ahead of the line. Main session delegates "
                    "more to Opus and keeps its context small. No top-tier subagents.",
    "USE_IT": "Top-tier quota will expire unused. Escalate freely: top-tier "
              "subagents are fine for anything that benefits. Say so in one line.",
    "ROOM_TOP": "Top-tier is behind the line. Hard subtasks (review, stubborn "
                "bugs, final synthesis) may go to top-tier subagents. Say so in "
                "one line first.",
    "HOLD": "On pace. Default split: main on the top-tier model, subagents on Opus.",
}


def decide(weekly, top, elapsed, remaining_days, margin, session=None):
    line = 100.0 * elapsed
    if top >= 90:
        return "SWITCH_MAIN"
    if weekly >= 90:
        return "MINIMUM"
    if session is not None and session >= 85:
        return "SESSION_FULL"
    if weekly - line > margin:
        return "BACK_OFF_ALL"
    if top - line > margin:
        return "BACK_OFF_TOP"
    if remaining_days <= 1.0 and top < 70:
        return "USE_IT"
    if line - top > margin:
        return "ROOM_TOP"
    return "HOLD"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--weekly", type=percent, required=True,
                    help="weekly all-models bar, percent used")
    ap.add_argument("--top", "--fable", dest="top", type=percent, required=True,
                    help="weekly top-tier (Fable/Mythos) bar, percent used")
    ap.add_argument("--resets-at", required=True,
                    help="when the weekly bars reset, ISO 8601")
    ap.add_argument("--session", type=percent,
                    help="5-hour session bar, percent used (plans that have one)")
    ap.add_argument("--session-resets-at", help="when the session bar resets")
    ap.add_argument("--window-days", type=float, default=7.0)
    ap.add_argument("--margin", type=float, default=10.0,
                    help="points off the line before the verdict changes (default 10)")
    ap.add_argument("--now", help="override the current time (ISO 8601), for testing")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    resets = parse_time(args.resets_at)
    window = timedelta(days=args.window_days)
    left = resets - now
    if left > window or left.total_seconds() < 0:
        ap.error("--resets-at must be within the next %g days" % args.window_days)
    elapsed = 1.0 - left / window
    line = 100.0 * elapsed

    def row(name, used):
        projected = used / elapsed if elapsed >= 0.05 else None
        return {"bar": name, "used": used, "line": round(line, 1),
                "delta": round(used - line, 1) + 0.0,  # + 0.0 turns -0.0 into 0.0
                "projected": None if projected is None else round(projected, 1)}

    rows = [row("weekly", args.weekly), row("top-tier", args.top)]
    verdict = decide(args.weekly, args.top, elapsed, left / timedelta(days=1),
                     args.margin, args.session)
    out = {"elapsed_percent": round(line, 1), "resets_in": span(left),
           "bars": rows, "verdict": verdict, "action": VERDICTS[verdict]}
    if args.session is not None:
        out["session"] = {"used": args.session}
        if args.session_resets_at:
            out["session"]["resets_in"] = span(parse_time(args.session_resets_at) - now)

    if args.json:
        json.dump(out, sys.stdout, indent=2)
        print()
        return 0

    print("window: %.1f%% elapsed, resets in %s" % (line, out["resets_in"]))
    print("%-9s %5s %5s %6s %10s" % ("bar", "used", "line", "delta", "projected"))
    for r in rows:
        proj = "n/a" if r["projected"] is None else "%.0f%%" % r["projected"]
        print("%-9s %4.0f%% %4.0f%% %+6.0f %10s"
              % (r["bar"], r["used"], r["line"], r["delta"], proj))
    if args.session is not None:
        tail = ", resets in %s" % out["session"]["resets_in"] \
            if "resets_in" in out["session"] else ""
        print("session   %4.0f%%%s" % (args.session, tail))
    print("verdict: %s" % verdict)
    print("action:  %s" % VERDICTS[verdict])
    return 0


if __name__ == "__main__":
    sys.exit(main())
