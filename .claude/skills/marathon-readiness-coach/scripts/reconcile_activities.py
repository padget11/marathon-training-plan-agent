#!/usr/bin/env python3
"""Dedupe and classify Garmin activities against the current plan, matching
running activities to a planned session by date.

Usage:
  python reconcile_activities.py --plan <plan-v1.yaml> --activities <normalized.json> \
      [--session-log <session-log.jsonl>] [--check-ins <check-ins.jsonl>]

--activities is a small JSON file the skill writes itself after normalizing whatever
the Garmin MCP server returned:
  [{"garmin_activity_id", "date" (YYYY-MM-DD), "activity_type", "distance_km", "duration_minutes"}]
This normalization step is the one place that changes if the Garmin MCP server is
ever swapped (NFR-006) - this script never talks to Garmin directly.

--session-log is the append-only record of what actually happened to each planned
session (state/session-log.jsonl) - a missing file just means nothing has happened
yet (not an error, unlike --plan/--activities). A session with no record in this log
is still open ("planned"); the plan file's own `status` field is the plan *as
authored* and is never mutated after being written, so it is not consulted for
current status here.

--check-ins is state/check-ins.jsonl (also optional, missing = empty). An activity
can already have a check-in without ever having matched a planned session (e.g. it
predates the plan), so session-log alone isn't enough to avoid asking the check-in
questions again for the same activity - this closes that gap.

Prints a JSON array to stdout (empty array is a valid, non-error result):
  [{"garmin_activity_id", "date", "distance_km", "duration_minutes", "is_running",
    "duplicate", "matched_session_id"}]

Exit codes:
  0 - ran successfully (regardless of how many matches were found)
  1 - malformed plan or activities content (structurally present but invalid)
  2 - usage/IO error (file not found, bad JSON/YAML syntax)
"""
import sys
import json
import argparse
import datetime
import yaml

RUNNING_ACTIVITY_TYPES = {"running", "treadmill_running", "trail_running"}
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


def load_activities(path, errors):
    try:
        with open(path, "r", encoding="utf-8") as f:
            activities = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"ERROR: could not parse JSON: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(activities, list):
        errors.append("activities file must contain a JSON array")
        return None
    for i, a in enumerate(activities):
        if not isinstance(a, dict):
            errors.append(f"activities[{i}]: must be an object")
            continue
        for field in ("garmin_activity_id", "date", "activity_type"):
            if not a.get(field):
                errors.append(f"activities[{i}]: missing required field '{field}'")
    return activities


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


def already_linked_ids(plan_doc, session_log_records, check_in_records):
    # Legacy plan-file field, kept for backward compatibility with any session
    # linked before session-log.jsonl existed; new links only ever land in the log.
    ids = set()
    for week in plan_doc["plan"]["weeks"]:
        for session in week.get("sessions", []):
            linked = session.get("linked_garmin_activity_id")
            if linked:
                ids.add(linked)
    for record in session_log_records:
        activity_id = record.get("garmin_activity_id")
        if activity_id:
            ids.add(activity_id)
    for record in check_in_records:
        activity_id = record.get("garmin_activity_id")
        if activity_id:
            ids.add(activity_id)
    return ids


def sessions_with_outcomes(session_log_records):
    return {record["session_id"] for record in session_log_records if record.get("session_id")}


def session_date(week, session):
    start_date = datetime.date.fromisoformat(str(week["start_date"]))
    day_code = session.get("day")
    if day_code not in WEEKDAY_INDEX:
        return None
    return start_date + datetime.timedelta(days=WEEKDAY_INDEX[day_code])


def find_matching_session(plan_doc, activity_date, sessions_with_outcomes_ids):
    for week in plan_doc["plan"]["weeks"]:
        for session in week.get("sessions", []):
            if session.get("category") != "run":
                continue
            if session.get("id") in sessions_with_outcomes_ids:
                continue
            s_date = session_date(week, session)
            if s_date is not None and s_date.isoformat() == activity_date:
                return session.get("id")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--activities", required=True)
    parser.add_argument("--session-log", default=None)
    parser.add_argument("--check-ins", default=None)
    try:
        args = parser.parse_args()
    except SystemExit:
        return 2

    errors = []
    plan_doc = load_plan(args.plan, errors)
    activities = load_activities(args.activities, errors)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    session_log_records = load_jsonl_records(args.session_log)
    check_in_records = load_jsonl_records(args.check_ins)
    linked_ids = already_linked_ids(plan_doc, session_log_records, check_in_records)
    outcome_ids = sessions_with_outcomes(session_log_records)
    results = []
    for activity in activities:
        activity_id = activity["garmin_activity_id"]
        duplicate = activity_id in linked_ids
        is_running = activity["activity_type"] in RUNNING_ACTIVITY_TYPES
        matched_session_id = None
        if not duplicate and is_running:
            matched_session_id = find_matching_session(plan_doc, activity["date"], outcome_ids)
        results.append({
            "garmin_activity_id": activity_id,
            "date": activity["date"],
            "distance_km": activity.get("distance_km"),
            "duration_minutes": activity.get("duration_minutes"),
            "is_running": is_running,
            "duplicate": duplicate,
            "matched_session_id": matched_session_id,
        })

    print(json.dumps(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
