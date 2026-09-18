# Adaptive Replanning: triggers and allowed actions (FR-014)

Loaded by [SKILL.md](../SKILL.md) section 12 before evaluating whether a disruption meets a trigger threshold,
and again before choosing an action.

## Triggers (concrete, not "use judgment")

Below every threshold, stay advisory (sections 9/10's existing behavior). At or above one:

- **Missed priority session** (`session-log` event `missed`, session `priority: priority` — normally the long
  run): always triggers.
- **2+ missed/skipped run sessions in the current week** (any priority): always triggers, for the remainder of
  that week.
- **Shortened priority session**: completed distance < 70% of planned — log as `modified`, not `missed`;
  triggers the same as a missed priority session.
- **Effort-mismatch pattern**: 2 consecutive check-ins where perceived effort is two or more steps above what
  the session's subtype implies (e.g. `easy`/`recovery` reported `hard`/`very_hard`) — a single instance stays
  advisory; the pattern triggers.
- **Concerning symptom or persistent/worsening pain** ([safety-rules.md](safety-rules.md)'s own SR-002/SR-003
  triggers): always triggers, in addition to (not instead of) the safety escalation language.
- **Reported unavailability for a planned day** (lightweight intake — the user says they can't make a session):
  always triggers, for that session specifically.
- **Reported unplanned/demanding exercise** (lightweight intake — e.g. "I did a hard hike Saturday"): advisory
  if isolated; triggers if it would otherwise stack against an already-planned hard session nearby.
- **Garmin data becoming unavailable**: never itself a trigger — proceed on whatever subjective evidence exists
  (SKILL.md section 2); don't block a decision on it either.

## Allowed actions (least disruptive first)

**Reduce** (cut distance/duration ~20-30%, matching "This week's plan" step 5's lower-load convention),
**replace** (swap a harder subtype back to `easy`/`recovery`), **move** (shift within the week — only for the
unavailability trigger, never creating two adjacent hard sessions), **remove** (convert to recovery — reserved
for a concerning-symptom trigger or a third disruption in one week).

Hard constraints on every action, no exceptions: never convert a rest/recovery day into a harder session to
compensate; never stack two hard sessions adjacently as a result of the change; never attempt to restore all
lost distance elsewhere this week (no catch-up — stated throughout this project, most explicitly in
`coaching-principles.md`'s progression section).
