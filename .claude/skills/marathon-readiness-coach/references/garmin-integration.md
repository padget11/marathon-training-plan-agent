# Garmin integration mechanics

Detailed tool signatures, response shapes, and the activity normalization contract for the `garmin` MCP server
(`mcp__garmin__*` tools, backed by **Taxuspt/garmin_mcp**). Load this whenever fetching or normalizing Garmin
data — see [SKILL.md](../SKILL.md) section 4 for when that applies and for the cross-cutting connection-failure
and correction-override rules, which live there, not here.

## Activity listing

- List recent activities: `mcp__garmin__get_activities_by_date(start_date, end_date, activity_type="", page=0,
  page_size=100)` — dates are `YYYY-MM-DD`, inclusive range, newest-first. Pass `activity_type="running"` to let
  the server pre-filter, but still apply the normalization/allow-list below yourself — the server's `running`
  filter is broader than our three canonical run categories. Paginate using `has_more`/`next_page` if a range
  ever needs more than one page (unlikely for the recent-context fetch in onboarding).
- Response shape: `{"count", "page", "page_size", "has_more", "date_range", "activities": [...]}`. Each activity
  has (at minimum) `id`, `name`, `type`, `event_type`, `start_time` ("YYYY-MM-DD HH:MM:SS"), `distance_meters`,
  `duration_seconds`. `type` is a Garmin `type_key` (confirmed via `mcp__garmin__get_activity_types`) — the
  running family includes `running`, `street_running`, `track_running`, `trail_running`, `treadmill_running`,
  `indoor_running`, `virtual_run`, `ultra_run`, `obstacle_run`.

## Recovery metrics

Confirmed live against the connected server (each is "where available" per FR-003; this account itself has
almost none of these populated, which is itself a real, expected case to handle, not a fixture artifact):

- `mcp__garmin__get_sleep_data(date)` → a `dailySleepDTO` object. Unavailable for that date if
  `sleepTimeSeconds` (and the other core fields) are `null` — this is a normal "not tracked that night" result,
  not an error.
- `mcp__garmin__get_hrv_data(date)`, `mcp__garmin__get_training_readiness(date)`,
  `mcp__garmin__get_training_load_balance(date)` → each returns a plain human-readable string like
  `"No HRV data found for 2026-09-16."` when unavailable, instead of a structured empty object. Detect this by
  checking whether the result is a "no ... data found" string rather than the expected object shape — this is
  the unavailable case, not a connection failure.
- `mcp__garmin__get_training_status(date)` → an object that's just `{"date": "..."}` with nothing else when
  there's no status data for that date.
- `mcp__garmin__get_body_battery(start_date, end_date)` → a list of `{"date", "charged", "drained", "events"}`.
  `charged`/`drained` as `null` means no data that day; both present as low/zero numbers with `events: []` is a
  genuine (if unremarkable) reading, not an absence — don't conflate the two.
- Whichever of these come back unavailable: say so plainly (e.g., "no sleep or HRV data is available for this
  period"), never estimate a value in their place. None of these are persisted locally — re-fetch when needed
  per NFR-005's data-minimization principle; this is a presentation-time fetch, not a new state file.

## Normalization contract

Do this immediately after any Garmin fetch, before anything else touches the data: map each returned activity
into this shape and write it to a small JSON file:
```json
[{"garmin_activity_id": "...", "date": "YYYY-MM-DD", "activity_type": "running", "distance_km": 8.1, "duration_minutes": 47}]
```
Field mapping: `garmin_activity_id` = `id`; `date` = the date portion of `start_time`; `distance_km` =
`distance_meters / 1000`; `duration_minutes` = `duration_seconds / 60`. `activity_type` collapses Garmin's `type`
onto our three-way allow-list: `trail_running` → `trail_running`; `treadmill_running` or `indoor_running` →
`treadmill_running`; `running`, `street_running`, `track_running`, `virtual_run`, `ultra_run`, `obstacle_run` →
`running`. Anything outside the running family (e.g. `cycling`, `strength_training`) keeps the server's own
`type` value unchanged — that's what marks it non-running to `reconcile_activities.py`; don't guess a running
type for something ambiguous. This file is what `scripts/reconcile_activities.py` reads; it's the only place
that needs to change if the Garmin MCP server is ever swapped.

Apply [SKILL.md](../SKILL.md) section 4's correction-override rule before finalizing `activity_type` — a
user-confirmed reclassification in `state/corrections.jsonl` always wins over the mapping above.
