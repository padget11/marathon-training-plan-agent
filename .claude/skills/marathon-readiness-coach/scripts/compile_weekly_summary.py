#!/usr/bin/env python3
"""Tally planned-vs-completed run sessions and long-run progression from the active
plan and session-log, as of a given date.

Usage:
  python compile_weekly_summary.py --plan <plan-v{n}.yaml> --session-log <session-log.jsonl> \
      [--check-ins <check-ins.jsonl>] [--as-of <YYYY-MM-DD>] [--week-start <YYYY-MM-DD>]

Introduced for Completion-Readiness Assessment (FR-016), which needs consistency and
long-run-progression facts as plain counts/date-range arithmetic, not judgment calls an
LLM should re-derive from raw logs each time (docs/technical-specification.md section
2.3). Extended for Weekly Review Generation (FR-015), which additionally needs one
specific week's per-category completion and total run distance/duration - --week-start
adds a "week" object to the output without changing anything else; omit it to get
exactly the original plan-to-date-only behavior.

A run session is "due" if its planned date (week.start_date + weekday offset) is on or
before --as-of (default: today). Sessions with no session-log record are still
"planned" (see reconcile_activities.py's docstring for why the plan file's own status
field is never consulted for this). long_run_progression only includes subtype: long
sessions with a completed/modified session-log record carrying distance_km - a missed
or skipped long run contributes to the session counts but not to the distance series.

Prints a JSON object to stdout:
  {"as_of", "run_sessions": {"total_due", "completed", "missed", "skipped", "modified",
   "pending", "still_planned_future"}, "consistency_ratio", "long_run_progression":
   [{"date", "session_id", "distance_km"}], "most_recent_post_run_check_in",
   "most_recent_weekly_check_in", "week": <only present if --week-start given>}
`pending` = due (planned date on or before --as-of) but no session-log record yet -
distinct from `still_planned_future` (not due yet).

With --week-start, "week" is:
  {"week_start", "by_category": {"run"|"mobility"|"strength"|"recovery": {"planned",
   "completed", "modified", "missed", "skipped", "pending"}}, "total_run_distance_km",
   "total_run_duration_minutes", "long_run_completed"}
"planned" per category counts every session in that category that week (regardless of
outcome); the rest are mutually exclusive outcome counts exactly like run_sessions
above. total_run_distance_km/total_run_duration_minutes sum session-log distance_km/
duration_minutes for that week's completed/modified run sessions only. long_run_completed
is true if the week's subtype: long session has a completed/modified session-log record.

Exit codes:
  0 - ran successfully
  1 - malformed plan content (structurally present but invalid)
  2 - usage/IO error (file not found, bad JSON/YAML syntax)
"""
import sys
import json
import argparse
import datetime
import yaml

WEEKDAY_INDEX = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def load_plan(path, errors):
    try:
        with open(path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"ERROR: could not parse YAML: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(doc, dict) or not isinstance(doc.get("plan"), dict):
        errors.append("plan file must contain a top-level 'plan:' mapping")
        return None
    weeks = doc["plan"].get("weeks")
    if not isinstance(weeks, list):
        errors.append("plan.weeks: must be a list")
        return None
    return doc


def load_jsonl_records(path):
    if path is None:
        return []
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except FileNotFoundError:
        return []
    return records


def session_date(week, session):
    start_date = datetime.date.fromisoformat(str(week["start_date"]))
    day_code = session.get("day")
    if day_code not in WEEKDAY_INDEX:
        return None
    return start_date + datetime.timedelta(days=WEEKDAY_INDEX[day_code])


def latest_event_for_session(session_log_records, session_id):
    latest = None
    for record in session_log_records:
        if record.get("session_id") != session_id:
            continue
        if latest is None or record.get("recorded_at", "") >= latest.get("recorded_at", ""):
            latest = record
    return latest


def most_recent_check_in(check_in_records, type_name):
    timestamps = [
        r.get("recorded_at") for r in check_in_records
        if r.get("type", "post_run") == type_name and r.get("recorded_at")
    ]
    return max(timestamps) if timestamps else None


CATEGORIES = ("run", "mobility", "strength", "recovery")


def compile_week(plan_doc, session_log_records, week_start_date, errors):
    week = None
    for w in plan_doc["plan"]["weeks"]:
        if str(w.get("start_date")) == week_start_date.isoformat():
            week = w
            break
    if week is None:
        errors.append(f"no week with start_date '{week_start_date.isoformat()}' found in plan")
        return None

    by_category = {
        cat: {"planned": 0, "completed": 0, "missed": 0, "skipped": 0, "modified": 0, "pending": 0}
        for cat in CATEGORIES
    }
    total_run_distance_km = 0.0
    total_run_duration_minutes = 0.0
    long_run_completed = False

    for session in week.get("sessions", []):
        category = session.get("category")
        if category not in by_category:
            continue
        by_category[category]["planned"] += 1
        event = latest_event_for_session(session_log_records, session.get("id"))
        if event is None:
            # No separate "not due yet" bucket per-category (unlike run_sessions above) -
            # a week-scoped review only makes sense once the week itself has passed, so
            # anything unrecorded here just means "nothing logged," regardless of date.
            by_category[category]["pending"] += 1
            continue
        outcome = event.get("event")
        if outcome in by_category[category]:
            by_category[category][outcome] += 1
        if category == "run" and outcome in ("completed", "modified"):
            if event.get("distance_km") is not None:
                total_run_distance_km += event["distance_km"]
            if event.get("duration_minutes") is not None:
                total_run_duration_minutes += event["duration_minutes"]
            if session.get("subtype") == "long":
                long_run_completed = True

    return {
        "week_start": week_start_date.isoformat(),
        "by_category": by_category,
        "total_run_distance_km": round(total_run_distance_km, 2),
        "total_run_duration_minutes": round(total_run_duration_minutes, 1),
        "long_run_completed": long_run_completed,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--session-log", required=True)
    parser.add_argument("--check-ins", default=None)
    parser.add_argument("--as-of", default=None)
    parser.add_argument("--week-start", default=None)
    try:
        args = parser.parse_args()
    except SystemExit:
        return 2

    errors = []
    plan_doc = load_plan(args.plan, errors)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    try:
        as_of = (
            datetime.date.fromisoformat(args.as_of) if args.as_of
            else datetime.date.today()
        )
    except ValueError:
        print(f"ERROR: --as-of '{args.as_of}' is not a valid ISO date (YYYY-MM-DD)", file=sys.stderr)
        return 2

    week_start_date = None
    if args.week_start:
        try:
            week_start_date = datetime.date.fromisoformat(args.week_start)
        except ValueError:
            print(f"ERROR: --week-start '{args.week_start}' is not a valid ISO date (YYYY-MM-DD)", file=sys.stderr)
            return 2

    session_log_records = load_jsonl_records(args.session_log)
    check_in_records = load_jsonl_records(args.check_ins)

    counts = {
        "completed": 0, "missed": 0, "skipped": 0, "modified": 0,
        "pending": 0, "still_planned_future": 0,
    }
    long_run_progression = []

    for week in plan_doc["plan"]["weeks"]:
        for session in week.get("sessions", []):
            if session.get("category") != "run":
                continue
            s_date = session_date(week, session)
            if s_date is None:
                continue
            event = latest_event_for_session(session_log_records, session.get("id"))
            if event is None:
                counts["still_planned_future" if s_date > as_of else "pending"] += 1
                continue
            outcome = event.get("event")
            if outcome in counts:
                counts[outcome] += 1
            if (
                session.get("subtype") == "long"
                and outcome in ("completed", "modified")
                and event.get("distance_km") is not None
            ):
                long_run_progression.append({
                    "date": s_date.isoformat(),
                    "session_id": session.get("id"),
                    "distance_km": event.get("distance_km"),
                })

    total_due = (
        counts["completed"] + counts["missed"] + counts["skipped"]
        + counts["modified"] + counts["pending"]
    )
    consistency_ratio = (
        round(counts["completed"] / total_due, 3) if total_due > 0 else None
    )
    long_run_progression.sort(key=lambda r: r["date"])

    result = {
        "as_of": as_of.isoformat(),
        "run_sessions": {"total_due": total_due, **counts},
        "consistency_ratio": consistency_ratio,
        "long_run_progression": long_run_progression,
        "most_recent_post_run_check_in": most_recent_check_in(check_in_records, "post_run"),
        "most_recent_weekly_check_in": most_recent_check_in(check_in_records, "weekly"),
    }

    if week_start_date is not None:
        week_errors = []
        week_result = compile_week(plan_doc, session_log_records, week_start_date, week_errors)
        if week_errors:
            for e in week_errors:
                print(f"ERROR: {e}", file=sys.stderr)
            return 1
        result["week"] = week_result

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
