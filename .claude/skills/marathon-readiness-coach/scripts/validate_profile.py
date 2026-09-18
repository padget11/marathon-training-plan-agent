#!/usr/bin/env python3
"""Validate and normalize state/runner-profile.yaml in place.

Usage: python validate_profile.py <path-to-runner-profile.yaml> [--raw-fields <comma-list>]

--raw-fields names which distance fields (typical_weekly_distance_km, longest_recent_run_km)
hold a freshly-stated raw number in the profile's `units` this call, and so should be
converted imperial->km. Omitted (the onboarding call site, unchanged): both distance
fields are treated as raw, matching original behavior. Passed explicitly by the Amend
profile journey, naming only the field(s) the user just restated - every other numeric
field is already km-normalized from a prior call and must not be converted again. Pass
`--raw-fields ""` to convert nothing (amending a non-distance field).

Exit codes:
  0 - valid; file rewritten normalized (defaults applied, imperial->km converted,
      weekday codes lowercased, updated_at stamped)
  1 - validation failed; every violation is printed to stderr, file left untouched
  2 - usage/IO error (file missing, or YAML doesn't parse)
"""
import sys
import datetime
import argparse
import yaml

REQUIRED_FIELDS = [
    "marathon_date",
    "goal_type",
    "units",
    "running_experience",
    "typical_weekly_distance_km",
    "longest_recent_run_km",
    "available_running_days",
    "preferred_long_run_day",
]

VALID_GOAL_TYPES = {"complete_first_marathon"}
VALID_UNITS = {"metric", "imperial"}
MILES_TO_KM = 1.609344

WEEKDAY_ALIASES = {
    "mon": "mon", "monday": "mon",
    "tue": "tue", "tues": "tue", "tuesday": "tue",
    "wed": "wed", "weds": "wed", "wednesday": "wed",
    "thu": "thu", "thur": "thu", "thurs": "thu", "thursday": "thu",
    "fri": "fri", "friday": "fri",
    "sat": "sat", "saturday": "sat",
    "sun": "sun", "sunday": "sun",
}

DEFAULTS = {
    "id": "owner",
    "goal_type": "complete_first_marathon",
    "target_time": None,
    "units": "metric",
    "mobility_preferences": [],
    "strength": {"experience": None, "equipment": [], "preferred_sessions_per_week": None},
    "user_entered_restrictions": [],
}


def normalize_weekday(raw, field_name, errors):
    if not isinstance(raw, str):
        errors.append(f"{field_name}: '{raw}' is not a recognized day of the week")
        return None
    code = WEEKDAY_ALIASES.get(raw.strip().lower())
    if code is None:
        errors.append(f"{field_name}: '{raw}' is not a recognized day of the week")
    return code


DISTANCE_FIELDS = ("typical_weekly_distance_km", "longest_recent_run_km")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile_path")
    parser.add_argument("--raw-fields", default=None)
    try:
        args = parser.parse_args()
    except SystemExit:
        return 2

    if args.raw_fields is None:
        fields_to_convert = set(DISTANCE_FIELDS)
    else:
        fields_to_convert = {f.strip() for f in args.raw_fields.split(",") if f.strip()}

    path = args.profile_path
    try:
        with open(path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2
    except yaml.YAMLError as e:
        print(f"ERROR: could not parse YAML: {e}", file=sys.stderr)
        return 2

    errors = []

    if not isinstance(doc, dict) or "runner" not in doc or not isinstance(doc["runner"], dict):
        print("ERROR: file must contain a top-level 'runner:' mapping", file=sys.stderr)
        return 1

    runner = dict(doc["runner"])

    for field in REQUIRED_FIELDS:
        value = runner.get(field)
        if value is None or value == "" or value == []:
            errors.append(f"{field}: required field is missing")

    goal_type = runner.get("goal_type")
    if goal_type is not None and goal_type not in VALID_GOAL_TYPES:
        errors.append(f"goal_type: '{goal_type}' is not a supported goal type "
                       f"(only {sorted(VALID_GOAL_TYPES)} is defined)")

    units = runner.get("units")
    if units is not None and units not in VALID_UNITS:
        errors.append(f"units: '{units}' must be one of {sorted(VALID_UNITS)}")

    marathon_date = runner.get("marathon_date")
    parsed_date = None
    if marathon_date is not None:
        try:
            parsed_date = datetime.date.fromisoformat(str(marathon_date))
            if parsed_date <= datetime.date.today():
                errors.append(f"marathon_date: '{marathon_date}' must be in the future")
        except ValueError:
            errors.append(f"marathon_date: '{marathon_date}' is not a valid ISO date (YYYY-MM-DD)")

    for field in ("typical_weekly_distance_km", "longest_recent_run_km"):
        value = runner.get(field)
        if value is not None:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                errors.append(f"{field}: must be a positive number, got '{value}'")

    normalized_days = None
    available_days = runner.get("available_running_days")
    if available_days is not None:
        if not isinstance(available_days, list) or len(available_days) == 0:
            errors.append("available_running_days: must be a non-empty list")
        else:
            normalized_days = []
            for day in available_days:
                code = normalize_weekday(day, "available_running_days", errors)
                if code is not None and code not in normalized_days:
                    normalized_days.append(code)

    normalized_long_run_day = None
    preferred_long_run_day = runner.get("preferred_long_run_day")
    if preferred_long_run_day is not None:
        normalized_long_run_day = normalize_weekday(
            preferred_long_run_day, "preferred_long_run_day", errors
        )
        if (
            normalized_long_run_day is not None
            and normalized_days is not None
            and normalized_long_run_day not in normalized_days
        ):
            errors.append(
                "preferred_long_run_day: must be one of available_running_days "
                f"({normalized_days})"
            )

    for field in ("mobility_preferences", "user_entered_restrictions"):
        value = runner.get(field)
        if value is not None and not isinstance(value, list):
            errors.append(f"{field}: must be a list, got '{value}'")

    strength = runner.get("strength")
    if strength is not None:
        if not isinstance(strength, dict):
            errors.append(f"strength: must be a mapping, got '{strength}'")
        else:
            equipment = strength.get("equipment")
            if equipment is not None and not isinstance(equipment, list):
                errors.append(f"strength.equipment: must be a list, got '{equipment}'")
            sessions_per_week = strength.get("preferred_sessions_per_week")
            if sessions_per_week is not None:
                if (
                    not isinstance(sessions_per_week, int)
                    or isinstance(sessions_per_week, bool)
                    or not (0 <= sessions_per_week <= 4)
                ):
                    errors.append(
                        "strength.preferred_sessions_per_week: must be an integer from 0 to 4, "
                        f"got '{sessions_per_week}'"
                    )

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Normalize: apply defaults, convert imperial distances to km, lowercase weekdays,
    # stamp updated_at.
    for key, default in DEFAULTS.items():
        runner.setdefault(key, default)

    if units == "imperial":
        for field in DISTANCE_FIELDS:
            if field in fields_to_convert:
                runner[field] = round(runner[field] * MILES_TO_KM, 2)

    runner["available_running_days"] = normalized_days
    runner["preferred_long_run_day"] = normalized_long_run_day
    runner["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")

    doc["runner"] = runner
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, sort_keys=False, default_flow_style=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
