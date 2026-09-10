# Marathon Readiness Coach — Technical Specification

**Status:** Draft, derived from [requirements.md](requirements.md) and [features.md](features.md). Resolves some
of the SRS's Open Design Decisions (section 16) with a recommended default; each resolution is called out below
and remains changeable.

## 1. Architectural stance

This is a **Claude Skill running locally on the user's machine**, not a client/server product. There is no
custom backend, no database, and no hosted service for the MVP — the "app" is a conversational skill plus a
folder of local files. This follows directly from the scope: one user, one machine, no calendar integration, no
multi-user concerns (section 3.1). Building a server/DB/API layer for that scope would add operational surface
(auth, hosting, backups-as-a-service) the requirements never ask for, and would work against NFR-006
(portability) by giving the coaching logic more to depend on.

```
┌─────────────────────────────────────────────────────────────────┐
│ User (conversational interface: Claude Code / Claude Desktop)   │
└───────────────────────────────┬───────────────────────────────┘
                                 │
                                 v
┌─────────────────────────────────────────────────────────────────┐
│ marathon-readiness-coach skill                                   │
│                                                                   │
│  SKILL.md ── workflow, triggers, decision sequence, response     │
│              format; orchestrates everything below               │
│                                                                   │
│  references/ ── loaded on demand, not kept in the main prompt:   │
│    coaching-principles.md · mobility-guidance.md ·               │
│    strength-guidance.md · safety-rules.md · output-templates.md  │
│                                                                   │
│  scripts/ ── deterministic, called as tools, never left to the   │
│    LLM's judgment: validate_profile · reconcile_activities ·     │
│    version_plan · compile_weekly_summary                          │
└───────────┬───────────────────────────────────────┬─────────────┘
            │                                        │
            v                                        v
┌───────────────────────────┐          ┌─────────────────────────────┐
│ Garmin MCP server          │          │ state/ (local files)        │
│ (swappable, section 5.1)   │          │ runner-profile.yaml         │
│ - activities, HR, sleep,   │          │ plans/plan-v{n}.yaml        │
│   HRV, training status     │          │ session-log.jsonl           │
└───────────┬─────────────────┘          │ check-ins.jsonl             │
            │                             │ weekly-reviews.jsonl        │
            │                             │ coaching-decisions.jsonl    │
            │                             │ corrections.jsonl           │
            │                             └─────────────────────────────┘
            v
     Garmin Connect
     (source of truth for recorded activities/metrics)
```

## 2. Components

### 2.1 SKILL.md — orchestration

Contains the workflow logic: which of the six user journeys (SRS section 11) is active, what to ask for versus
what to retrieve, the order of operations for each journey, and the standard response structure (SRS section
10.4: Recommendation / Why / Updated week / Check-in). It calls the Garmin MCP server for data, calls `scripts/`
for anything deterministic, and loads a `references/` file only when the current step needs it — e.g. it
consults `references/coaching-principles.md` when generating or adjusting a plan, but not when just recording a
check-in.

SKILL.md does **not** contain the evidence/rules content itself — that separation (thin orchestrator, fat
references loaded on demand) is what keeps the main prompt small and keeps `references/coaching-principles.md`
independently reviewable and updatable (NFR-007).

### 2.2 references/ — planning and safety rules

- `coaching-principles.md` — done ([docs/references/coaching-principles.md](references/coaching-principles.md)).
- `mobility-guidance.md`, `strength-guidance.md` — not yet written; should follow the same evidence-graded
  pattern once drafted.
- `safety-rules.md` — the operational form of SR-001–SR-007: exact trigger conditions and escalation language,
  which SRS Open Design Decision #9 explicitly leaves unresolved. This needs to be precise enough that the skill
  applies it consistently, not just a restatement of the SRS prose.
- `output-templates.md` — the concrete markdown templates for each response type (weekly plan, weekly review,
  readiness assessment, post-run check-in prompt), so formatting is consistent without re-deriving it every time.

### 2.3 scripts/ — deterministic logic

Four scripts, extending SRS section 14's list by one (`compile_weekly_summary.py` — see rationale below),
implemented as small Python (or Node) programs the skill invokes as tools rather than tasks the LLM reasons
through free-form:

| Script | Responsibility | Why it must be deterministic |
|---|---|---|
| `validate_profile.py` | Checks a runner-profile edit against the schema (required fields, units, no target-time field required) before it's saved. | A malformed profile silently corrupts every downstream plan; this must fail loudly and consistently, not "usually." |
| `reconcile_activities.py` | Dedupes Garmin activities against what's already recorded, flags non-running activities, matches a Garmin activity to its check-in. | FR-003's "duplicate activities are not counted twice" and "non-running activities are not treated as runs" are exact-match problems, not judgment calls. |
| `version_plan.py` | Bumps the plan version, writes the new `plan-v{n}.yaml`, and links it to the `coaching-decision` record that caused the change. | FR-014/FR-017 require that replanning creates a new version and that every version traces to the evidence considered — version numbering must be monotonic and never skipped or reused. |
| `compile_weekly_summary.py` | Tallies planned-vs-completed sessions, total distance/duration, and mobility/strength completion from `session-log.jsonl` + `check-ins.jsonl`. Also serves Data Status View's status fields (period covered, outstanding check-ins) by scanning the same files, and derives "most recent successful Garmin sync" as the latest timestamp among any `source: garmin` record — no separate sync-log file needed, since every Garmin-sourced record already carries a timestamp and its source. | FR-015's "total recorded running distance and duration" and FR-020's status fields are counts and date-range facts, not judgment calls — an LLM re-deriving them from raw logs each time risks silent arithmetic drift. The *interpretation* built on top of these tallies (what helped, what needs attention) stays with the skill; only the tallying itself is scripted. |

Each script is a plain CLI/function taking the relevant state files as input and returning success/failure plus
structured output — no LLM call inside them.

### 2.4 Garmin MCP server

External dependency, not built as part of this project. The skill talks to it only through whatever tools it
exposes (list activities, get activity detail, get sleep/HRV/training-status where available). Per NFR-006, no
coaching logic should assume a specific MCP implementation's tool names or response shape beyond a thin adapter
layer — if that adapter doesn't already exist as a stable convention by the time this is built, it's worth
writing one function that normalizes whatever the chosen MCP server returns into the fields the skill actually
uses, so swapping servers later touches one place, not every reference to Garmin data.

**Open (SRS Open Design Decision #1–2):** which MCP implementation, and which of the "where available" fields
(training load, HRV, training readiness) it actually exposes. This can't be resolved on paper — it needs
picking a real server and checking what it returns.

### 2.5 state/ — persistence

Plain files, not a database, matching the schemas in SRS section 7 directly:

```
state/
├── runner-profile.yaml          # current effective profile, validated on every write
├── corrections.jsonl            # append-only: every manual correction (FR-018) — profile field
│                                 #   changes, activity reclassification, plan overrides — with
│                                 #   old value, new value, and timestamp, so runner-profile.yaml
│                                 #   being "current state only" doesn't lose the audit trail FR-018
│                                 #   requires
├── plans/
│   ├── plan-v1.yaml
│   ├── plan-v2.yaml
│   └── ...                      # old versions kept, never deleted (FR-014, NFR-003)
├── session-log.jsonl            # append-only: one record per session status event (planned,
│                                 #   completed, modified, skipped, missed), linked to a plan
│                                 #   version and, where applicable, a Garmin activity ID — this is
│                                 #   what lets "mark a run complete" happen without bumping the
│                                 #   whole plan to a new version each time
├── check-ins.jsonl              # append-only: post-run + weekly wellbeing check-ins
├── weekly-reviews.jsonl         # append-only: one record per generated weekly review (FR-015),
│                                 #   retained per section 7.3 so past reviews stay inspectable and
│                                 #   Completion-Readiness Assessment can reference review history
│                                 #   without re-deriving it
└── coaching-decisions.jsonl     # append-only: one record per material plan change (FR-017)
```

Rationale for this layout:
- **Append-only `.jsonl` for check-ins, decisions, sessions, reviews and corrections** gives an audit trail
  (NFR-008) without any extra bookkeeping — nothing is ever rewritten, so history can't be silently lost. This
  also resolves a gap in an earlier draft of this spec, which had no file for session-completion state, weekly
  reviews, or profile-correction history even though `features.md`'s Persistent State Model and FR-018 both
  require retaining them.
- **Session status is tracked separately from the plan file it refers to.** A plan version (`plan-v{n}.yaml`) is
  the plan *as authored*; `session-log.jsonl` is what actually happened against it. Marking a run complete is
  routine and frequent — it shouldn't force a new plan version each time, which is reserved for FR-014's
  "material change" bar (missed sessions, load adjustments, etc.).
- **One file per plan version** rather than a single file with an embedded version history keeps "which version
  was active when a given check-in happened" a matter of filename/timestamp, not a query into a larger
  structure.
- Every record includes a `source` field (`garmin` / `user` / `agent`) per the provenance requirement in
  section 7.3 — this is what lets FR-017's traceability and FR-010's evidence-conflict explanations actually be
  built from the data rather than reconstructed from memory.

**Open (SRS Open Design Decision #3):** exact on-disk location and whether it needs OS-level encryption at
rest. For a single-user local file store, restrictive file permissions (NFR-004) are the minimum; full-disk or
per-file encryption is worth doing if the machine is shared or the files could sync to a cloud drive, but isn't
implied by anything in the SRS as written.

## 3. Control flow by journey

Mapping SRS section 11's six journeys onto the components above — this is the level of detail SKILL.md's
decision sequence needs to implement:

1. **Onboarding** → SKILL.md calls Garmin MCP for recent history → `validate_profile.py` on the assembled
   profile → writes `runner-profile.yaml` → no plan yet.
2. **Create first plan** → loads `references/coaching-principles.md` (progression, tapering, strength) →
   generates phased plan → `version_plan.py` writes `plans/plan-v1.yaml`, seeding `session-log.jsonl` with each
   session's initial `planned` status → writes a `coaching-decisions.jsonl` record citing the baseline evidence
   used.
3. **Post-run review** → Garmin MCP for the new activity → `reconcile_activities.py` to dedupe/classify it →
   appends a `completed` (or `modified`) entry to `session-log.jsonl` for the matching planned session → SKILL.md
   asks the check-in questions → appends to `check-ins.jsonl` linked to the activity ID.
4. **Missed session** → SKILL.md reads current `plan-v{n}.yaml` + `session-log.jsonl` + recent `check-ins.jsonl`
   → appends a `missed` entry to `session-log.jsonl` → applies `references/coaching-principles.md` (no catch-up,
   conservative progression) → `version_plan.py` writes `plan-v{n+1}.yaml` → decision record explains the change.
5. **Weekly review + next plan** → Garmin MCP for the week's data → `compile_weekly_summary.py` tallies that
   week's `session-log.jsonl` + `check-ins.jsonl` entries (planned vs. completed, totals, mobility/strength
   completion) → SKILL.md builds the interpretation on top of those tallies (objective / subjective /
   interpretation, kept distinguishable per FR-015) → appends the result to `weekly-reviews.jsonl` → generates
   next week → new plan version.
6. **Readiness check** → reads plan history, `session-log.jsonl`, check-in history, `weekly-reviews.jsonl` (if
   any exist — not required, since readiness must be answerable before a first weekly review has ever run), and
   decision history → no new plan version written; this is a read-only synthesis over existing state.

A manual correction (FR-018 — editing the profile, reclassifying an activity, overriding a proposed plan)
appends to `corrections.jsonl` regardless of which journey triggered it, in addition to whatever state file the
correction itself touches (`runner-profile.yaml`, `session-log.jsonl`, or a new plan version).

Journeys 3–5 are the ones that need a trigger — see below.

## 4. Runtime model and the "who starts it" problem

There is no background process in this design; nothing runs unless the user opens Claude and invokes the skill
(SRS Open Design Decision #5). For the MVP, that's an acceptable and honestly-scoped default given the
single-user, no-calendar-integration constraints (section 3.1) — but it means post-run and weekly check-ins are
pull, not push: the user has to remember to ask.

**Recommended default:** ship the MVP pull-only, and layer a nudge on top as a Should-have rather than blocking
the MVP on it — e.g. a scheduled OS task or the `schedule`/`loop` mechanisms available in this environment that
periodically prompts "log your run" / "weekly check-in due," which still just invokes the same skill rather than
requiring a separate always-on service.

## 5. Security and privacy

- Garmin credentials/tokens live wherever the chosen MCP server keeps them — never in `state/`, never logged,
  never echoed in conversation (SR-007). SKILL.md should never need to see a token to function.
- `state/` should not be committed to version control if this repo is ever made public or shared — it's the
  user's personal training/health data. A `.gitignore` entry for `state/` (or wherever it ends up living) is
  needed before any real data is stored there.
- Data minimisation (NFR-005/7.4): store retrieved Garmin summaries needed for planning and review, not full raw
  activity tracks (GPS traces, per-second HR) — those stay in Garmin and get re-fetched if ever needed, rather
  than duplicated locally.

## 6. Portability and future scope

- Swapping the Garmin MCP server should only touch the thin adapter mentioned in 2.4, not `SKILL.md` or
  `references/`.
- The `Could Have` items in [features.md](features.md) (structured workouts written back to Garmin, charts,
  voice check-ins) all extend this design without changing it: writing to Garmin is a new MCP tool call, charts
  read the same `state/` files, voice is a different input surface in front of the same skill.

## 7. Explicitly not part of this spec

No mobile app, no web UI, no multi-user auth, no cloud hosting, no database migrations — none of these are
implied by the requirements, and adding them now would be building for a hypothetical future version rather
than the one this repo describes.
