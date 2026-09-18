#!/usr/bin/env python3
"""Write a new versioned plan file, superseding whatever was active before.

Usage: python version_plan.py --new-plan <draft.yaml> --plans-dir <state/plans/>

Exit codes:
  0 - written; prints {"path": "...", "version": n} to stdout
  1 - draft plan fails structural validation (missing weeks, an empty week, a
      session missing category/day/status)
  2 - usage/IO error (file missing, YAML doesn't parse, plans-dir not writable)
"""
import sys
import os
import re
import json
import argparse
import yaml

PLAN_FILE_RE = re.compile(r"^plan-v(\d+)\.yaml$")
REQUIRED_SESSION_FIELDS = ("category", "day", "status")


def next_version(plans_dir):
    highest = 0
    if os.path.isdir(plans_dir):
        for name in os.listdir(plans_dir):
            m = PLAN_FILE_RE.match(name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def validate_draft(doc, errors):
    if not isinstance(doc, dict) or "plan" not in doc or not isinstance(doc["plan"], dict):
        errors.append("file must contain a top-level 'plan:' mapping")
        return
    plan = doc["plan"]
    weeks = plan.get("weeks")
    if not isinstance(weeks, list) or len(weeks) == 0:
        errors.append("plan.weeks: must be a non-empty list")
        return
    for i, week in enumerate(weeks):
        if not isinstance(week, dict):
            errors.append(f"plan.weeks[{i}]: must be a mapping")
            continue
        sessions = week.get("sessions")
        if not isinstance(sessions, list) or len(sessions) == 0:
            errors.append(f"plan.weeks[{i}] (week_number={week.get('week_number')}): "
                           f"sessions must be a non-empty list")
            continue
        for j, session in enumerate(sessions):
            if not isinstance(session, dict):
                errors.append(f"plan.weeks[{i}].sessions[{j}]: must be a mapping")
                continue
            for field in REQUIRED_SESSION_FIELDS:
                if not session.get(field):
                    errors.append(
                        f"plan.weeks[{i}].sessions[{j}] (id={session.get('id')}): "
                        f"missing required field '{field}'"
                    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new-plan", required=True)
    parser.add_argument("--plans-dir", required=True)
    try:
        args = parser.parse_args()
    except SystemExit:
        return 2

    try:
        with open(args.new_plan, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.new_plan}", file=sys.stderr)
        return 2
    except yaml.YAMLError as e:
        print(f"ERROR: could not parse YAML: {e}", file=sys.stderr)
        return 2

    errors = []
    validate_draft(doc, errors)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    try:
        os.makedirs(args.plans_dir, exist_ok=True)
        version = next_version(args.plans_dir)

        # Supersede whatever plan was previously active.
        for name in os.listdir(args.plans_dir):
            m = PLAN_FILE_RE.match(name)
            if m:
                prior_path = os.path.join(args.plans_dir, name)
                with open(prior_path, "r", encoding="utf-8") as f:
                    prior_doc = yaml.safe_load(f)
                if isinstance(prior_doc, dict) and isinstance(prior_doc.get("plan"), dict):
                    if prior_doc["plan"].get("status") == "active":
                        prior_doc["plan"]["status"] = "superseded"
                        with open(prior_path, "w", encoding="utf-8") as f:
                            yaml.safe_dump(prior_doc, f, sort_keys=False, default_flow_style=False)

        doc["plan"]["id"] = f"plan-{version}"
        doc["plan"]["version"] = version
        doc["plan"].setdefault("status", "active")

        new_path = os.path.join(args.plans_dir, f"plan-v{version}.yaml")
        with open(new_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, sort_keys=False, default_flow_style=False)
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(json.dumps({"path": new_path, "version": version}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
