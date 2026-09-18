# Marathon Readiness Coach — Feature Backlog

This backlog translates [requirements.md](requirements.md) (the SRS) into discrete, buildable features. Every
entry cites the FR/SR/section it traces to — the SRS remains the authority for full acceptance detail; the
criteria listed here are condensed for scannability. `Depends on` reflects build order, not priority.

---

## Progress

Tick a box once a feature meets its acceptance criteria below, not when work merely starts on it. See
[roadmap.md](roadmap.md) for the recommended build order.

### Must Have (MVP)

- [x] Persistent State Model
- [x] Safety Guardrails
- [x] Runner Profile Management
- [x] Garmin Connection & Auth Handling
- [x] Garmin Data Retrieval
- [x] Baseline Assessment
- [x] Initial Marathon Plan Generation
- [x] Running Session Type Library
- [x] Weekly Plan Generation
- [x] Mobility Planning
- [x] Strength Training Integration
- [x] Rest & Recovery Scheduling
- [x] Post-Run Check-in
- [x] Weekly Wellbeing Check-in
- [x] Evidence Conflict Resolution
- [x] Adaptive Replanning
- [x] Weekly Review Generation
- [x] Completion-Readiness Assessment
- [x] Decision Traceability & Explanation Log
- [x] Manual Data Entry & Correction

### Should Have

- [ ] Natural-Language Commands
- [ ] Data Status View
- [ ] Plan Version Comparison
- [ ] Low-Impact Cross-Training Alternatives
- [ ] Exportable Weekly Summary

### Could Have

- [ ] Structured Workouts Written Back to Garmin
- [ ] Charts and Trend Visualisations
- [ ] Voice-Based Check-ins
- [ ] Race-Day Checklist
- [ ] Shoe and Equipment Tracking

---

## Must Have (MVP)

### Persistent State Model
**Traces to:** SRS section 7 (Data Requirements)
**What it does:** The local storage layer for everything Garmin doesn't hold: runner profile, versioned training
plans, planned sessions, post-run and weekly check-ins, and coaching decisions. Foundational — every other
Must-have feature reads or writes through this.
**Depends on:** —
**Key acceptance criteria:**
- Garmin Connect remains the source of truth for Garmin-recorded activities/metrics; local state is the source
  of truth for preferences, feedback, plans, and coaching decisions.
- Provenance is preserved: imported, user-entered, and agent-generated data stay distinguishable.
- Retains: active profile, plan versions, session completion state, check-ins, weekly reviews, coaching decisions.
- Supports deletion/reset of locally persisted personal training state.
- Stores only what's needed for planning/review/traceability — no unnecessary full copies of raw Garmin datasets.

### Safety Guardrails
**Traces to:** SR-001 – SR-007
**What it does:** Cross-cutting behavioral constraints enforced across every coaching output, not a standalone
workflow — implemented as rules the other features must call into (e.g., before finalizing a check-in response
or a plan change).
**Depends on:** —
**Key acceptance criteria:**
- States clearly it is not a medical professional and does not diagnose (SR-001).
- Severe/sudden/worsening/concerning symptoms stop normal coaching for that session and prompt appropriate
  professional/urgent guidance (SR-002).
- Pain is never treated as a normal training metric; no injury rehab is prescribed; persistent/worsening pain
  triggers a recommendation to seek professional assessment (SR-003).
- Incomplete or conflicting evidence defaults to the lower-risk recommendation, with the uncertainty stated
  (SR-004).
- No guarantees of completion, results, or injury prevention (SR-005).
- A user request for more aggressive training never removes or weakens a relevant safety warning (SR-006).
- Secrets (tokens, passwords) never appear in prompts, logs, plan files, or conversational output (SR-007).

### Runner Profile Management
**Traces to:** FR-001
**What it does:** Create and maintain the single runner profile (marathon date, goal type, experience, weekly
distance, longest recent run, availability, equipment, restrictions, units).
**Depends on:** Persistent State Model
**Key acceptance criteria:**
- A profile can be created without a target finish time; goal is recorded as "first marathon."
- Profile can be amended without deleting existing training history.
- Downstream plans use the profile's stated availability and equipment.

### Garmin Connection & Auth Handling
**Traces to:** FR-002
**What it does:** Connects to Garmin Connect through the configured Garmin MCP server; detects and reports
connection/auth state; falls back to a limited manual mode when Garmin is unavailable.
**Depends on:** —
**Key acceptance criteria:**
- Distinguishes a successful retrieval from a connection failure.
- A connection failure never causes fabricated training data to appear.
- The user is told which relevant data could not be retrieved.
- Existing plans and manually recorded feedback stay available during an integration failure.
- No Garmin passwords/tokens are logged or displayed.

### Garmin Data Retrieval
**Traces to:** FR-003
**What it does:** Retrieves running activities and available recovery metrics (pace, HR, elevation, training
load/status, sleep, HRV, training readiness) subject to what the configured MCP implementation exposes, and
tags each value by source (Garmin / user-entered / agent-interpreted).
**Depends on:** Garmin Connection & Auth Handling
**Key acceptance criteria:**
- Every analysis states the period of Garmin data considered.
- Missing metrics are marked unavailable, never silently estimated.
- Duplicate activities are not double-counted; non-running activities are not treated as runs.
- A manually entered run can substitute when Garmin is unavailable, labeled as user-entered.

### Baseline Assessment
**Traces to:** FR-004
**What it does:** Establishes the starting point for the first plan from the profile, available Garmin history,
and any material information the agent must ask for directly.
**Depends on:** Runner Profile Management, Garmin Data Retrieval
**Key acceptance criteria:**
- The first plan is never generated solely from the marathon date.
- The baseline records which evidence was actually available.
- The user can correct an inaccurate baseline.
- Uncertainty from limited history is stated explicitly, not smoothed over.

### Initial Marathon Plan Generation
**Traces to:** FR-005
**What it does:** Builds the completion-oriented, phased plan (consistency → aerobic volume → long-run
development → recovery weeks → marathon-specific prep → taper) from the baseline to race day.
**Depends on:** Baseline Assessment, Running Session Type Library, Mobility Planning, Strength Training
Integration
**Key acceptance criteria:**
- Works without a target finish time.
- Each week has a clear purpose; every run has a session type and effort-based instruction.
- Mobility appears in the main plan, not as an optional note; strength is included at a supporting level.
- The final phase includes an explicit taper.

### Running Session Type Library
**Traces to:** FR-007
**What it does:** The catalog of supported running session types (easy, long, recovery, steady, run-walk,
technique/strides, controlled quality, optional low-impact cross-training) with effort-based guidance, used by
both plan generators.
**Depends on:** —
**Key acceptance criteria:**
- Every session type has a stated purpose and effort guidance understandable without sports-science background.
- No session requires goal-marathon pace when no target time exists.
- Run-walk is presented as a valid strategy, not a fallback/failure.
- Optional sessions are clearly distinguished from priority sessions.

### Weekly Plan Generation
**Traces to:** FR-006
**What it does:** Produces the detailed weekly plan (day, category, purpose, duration/distance, effort/warm-up/
cool-down guidance, completion criterion, cautions) from the current phase, recent completions, available
Garmin data, and recent subjective feedback.
**Depends on:** Initial Marathon Plan Generation, Running Session Type Library, Mobility Planning, Strength
Training Integration, Rest & Recovery Scheduling
**Key acceptance criteria:**
- Shows running, mobility, strength, and rest together in one view.
- Hard running sessions are not scheduled on consecutive days by default; strength never undermines the
  priority long run.
- Material departures from the broader plan are explained.
- The user can request a lower-load version of the week.

### Mobility Planning
**Traces to:** FR-011
**What it does:** Plans mobility work (ankles, calves, hips, glutes, hamstrings, thoracic, general prep/recovery
movement) adapted to run type, volume, reported stiffness, preferences, and available time.
**Depends on:** Runner Profile Management
**Key acceptance criteria:**
- Every week contains mobility work appropriate to that week's training, delivered as pre-run, post-run, or
  standalone sessions, each with a stated area/purpose.
- Reported pain prompts caution, not a prescriptive rehab routine — mobility is never framed as injury treatment.

### Strength Training Integration
**Traces to:** FR-012
**What it does:** Plans conservative, supporting strength sessions (squat/hinge/lunge/calf/single-leg/trunk/
upper-body patterns) that scale down as running load rises and shift to maintenance during peak prep and taper.
**Depends on:** Runner Profile Management
**Key acceptance criteria:**
- Appears in the weekly plan with purpose, exercise selection, sets/duration, and an effort limit.
- Adapts to the equipment recorded in the profile.
- Volume is reduced when running load or fatigue is high; never becomes a hypertrophy/max-strength program.
- Missed strength work is not automatically rescheduled next to a long or hard run.

### Rest & Recovery Scheduling
**Traces to:** FR-013
**What it does:** Explicitly schedules full rest, gentle mobility, optional easy walking, low-impact
cross-training, reduced-load weeks, and extra recovery after demanding/poorly tolerated sessions.
**Depends on:** Persistent State Model
**Key acceptance criteria:**
- Every weekly plan includes adequate recovery opportunities.
- A recovery day is never silently converted into a hard session to make up missed mileage.
- Reduced-load decisions carry a concise rationale; rest is never framed as a training failure.

### Post-Run Check-in
**Traces to:** FR-008
**What it does:** Requests concise subjective feedback (perceived effort, how it felt, energy, soreness,
concerning symptoms, confidence/enjoyment, free text) after a recorded or manually reported run, unless already
captured.
**Depends on:** Persistent State Model, Garmin Data Retrieval
**Key acceptance criteria:**
- Feedback links to the correct activity or manual entry; the raw response is retained unaltered.
- Normal exertion is distinguished from a report of pain or concerning symptoms.
- Already-answered check-ins aren't asked again; the user can skip a check-in.
- Recent check-ins inform future recommendations.

### Weekly Wellbeing Check-in
**Traces to:** FR-009
**What it does:** At least once per planning week, gathers general energy, motivation, stress, overall soreness,
perceived sleep, confidence in next week's training, and any other relevant factor.
**Depends on:** Persistent State Model
**Key acceptance criteria:**
- The weekly plan records whether a check-in was available for that week.
- Low energy, high soreness, or concerning feedback can reduce or modify the proposed load.
- Missing wellbeing feedback is disclosed, never papered over with invented assumptions.

### Evidence Conflict Resolution
**Traces to:** FR-010
**What it does:** Reconciles subjective reports against Garmin data without a fixed numeric weighting — surfaces
conflicts, asks for context when needed, and defaults conservative when safety/recovery is in question.
**Depends on:** Garmin Data Retrieval, Post-Run Check-in, Weekly Wellbeing Check-in, Safety Guardrails
**Key acceptance criteria:**
- A positive Garmin metric never overrides a reported pain.
- A single poor Garmin metric never auto-cancels training without context.
- Every resulting explanation identifies which part came from Garmin and which from the user.

### Adaptive Replanning
**Traces to:** FR-014
**What it does:** Reacts to missed/shortened/harder-or-easier-than-intended runs, poor recovery signals, pain
reports, unavailability, Garmin outages, or unplanned exercise by replacing, reducing, moving, or removing
sessions — never by compressing missed work into remaining days.
**Depends on:** Weekly Plan Generation, Post-Run Check-in, Weekly Wellbeing Check-in, Evidence Conflict Resolution
**Key acceptance criteria:**
- A missed session never automatically increases a later session.
- The revised week stays internally consistent; the previous plan version remains in history.
- Every adjustment records its evidence and rationale.

### Weekly Review Generation
**Traces to:** FR-015
**What it does:** Produces the weekly review: planned vs. completed, objective Garmin trends (with gaps called
out), subjective feedback summary, and coaching interpretation (what helped, what needs attention, proposed
changes, confidence/limitations).
**Depends on:** Weekly Plan Generation, Post-Run Check-in, Weekly Wellbeing Check-in, Garmin Data Retrieval
**Key acceptance criteria:**
- Objective data, user feedback, and coach interpretation stay clearly distinguishable.
- Never invents explanations for missing sessions.
- Feeds directly into the next weekly plan.
- Concerning feedback is surfaced, not buried in a general summary.

### Completion-Readiness Assessment
**Traces to:** FR-016
**What it does:** Assesses readiness to complete the marathon (consistency, long-run progression, recovery
ability, tolerance, confidence, remaining time, unresolved concerns) without a finish-time target, returning one
of: on track, progressing with areas to address, disrupted/uncertain, or insufficient evidence.
**Depends on:** Persistent State Model, Post-Run Check-in, Weekly Wellbeing Check-in, Baseline Assessment
**Key acceptance criteria:**
- Never requires or invents a target finish time, and never guarantees completion or injury-free training.
- Lists the evidence behind the status and states its limitations.
- Provides practical next priorities, not just a label.

### Decision Traceability & Explanation Log
**Traces to:** FR-017
**What it does:** Records, for every material plan change, what changed, the evidence considered, the reason,
the evidence's source (Garmin/user/plan state), and any uncertainty.
**Depends on:** Persistent State Model
**Key acceptance criteria:**
- The user can see why distance, intensity, strength, or recovery changed.
- Agent interpretation is never presented as a Garmin measurement.
- A plan version can be traced back to the check-ins and activities considered at the time it was created.

### Manual Data Entry & Correction
**Traces to:** FR-018
**What it does:** Lets the user add an unrecorded run, correct misclassified data, mark session status, add
late feedback, correct their profile, or override a proposed plan — all labeled and retained in an audit trail.
**Depends on:** Persistent State Model, Garmin Data Retrieval
**Key acceptance criteria:**
- Corrections never silently alter the original Garmin source record.
- The current plan reflects accepted corrections.
- The user can see the current effective value whenever Garmin and manual data disagree.

---

## Should Have

### Natural-Language Commands
**Traces to:** FR-019
**What it does:** Recognizes natural-language requests and may expose shortcut commands (`/create-plan`,
`/this-week`, `/log-feedback`, `/adjust-week`, `/weekly-review`, `/readiness`, `/profile`, `/data-status`) as
optional shortcuts, never required.
**Depends on:** Initial Marathon Plan Generation, Weekly Plan Generation, Post-Run Check-in, Weekly Wellbeing
Check-in, Adaptive Replanning, Weekly Review Generation, Completion-Readiness Assessment, Runner Profile
Management, Data Status View
**Key acceptance criteria:**
- Core workflows are fully completable in plain conversational language.
- Command output follows the same safety and evidence rules as conversational output.

### Data Status View
**Traces to:** FR-020
**What it does:** Shows Garmin connection state, last successful sync, period covered by retrieved data, missing
data types, outstanding check-ins, latest wellbeing check-in date, and current plan version.
**Depends on:** Garmin Connection & Auth Handling, Garmin Data Retrieval, Post-Run Check-in, Weekly Wellbeing
Check-in, Persistent State Model
**Key acceptance criteria:**
- The user can tell whether advice is based on current, partial, or unavailable Garmin data.
- Never exposes authentication secrets.

### Plan Version Comparison
**Traces to:** SRS section 13 (Should have)
**What it does:** Lets the user compare two plan versions to see what changed between them, built on top of the
versioning already required by Decision Traceability & Explanation Log.
**Depends on:** Persistent State Model, Decision Traceability & Explanation Log
**Key acceptance criteria:** Not separately detailed in the SRS beyond being named as a should-have; scope to be
refined during implementation against FR-017's traceability requirements.

### Low-Impact Cross-Training Alternatives
**Traces to:** SRS section 13 (Should have); overlaps FR-007, FR-013
**What it does:** Offers a low-impact cross-training substitute (e.g., cycling, swimming) for a running session
when appropriate, as an optional alternative rather than a required swap.
**Depends on:** Running Session Type Library, Weekly Plan Generation
**Key acceptance criteria:** Uses the same optional-vs-priority distinction as FR-007; not separately detailed
beyond that in the SRS.

### Exportable Weekly Summary
**Traces to:** SRS section 13 (Should have)
**What it does:** Exports the weekly review/plan in a shareable form.
**Depends on:** Weekly Review Generation
**Key acceptance criteria:** Not separately detailed in the SRS beyond being named as a should-have.

---

## Could Have

### Structured Workouts Written Back to Garmin
**Traces to:** SRS sections 2.3, 13
**Depends on:** Garmin Connection & Auth Handling, Weekly Plan Generation

### Charts and Trend Visualisations
**Traces to:** SRS section 13
**Depends on:** Garmin Data Retrieval, Weekly Review Generation

### Voice-Based Check-ins
**Traces to:** SRS sections 2.3, 13
**Depends on:** Post-Run Check-in, Weekly Wellbeing Check-in

### Race-Day Checklist
**Traces to:** SRS section 13
**Depends on:** Completion-Readiness Assessment, Initial Marathon Plan Generation (taper phase)

### Shoe and Equipment Tracking
**Traces to:** SRS sections 2.3, 13
**Depends on:** Runner Profile Management, Manual Data Entry & Correction

---

## Explicitly Out of Scope (Won't Have, MVP)

Per SRS sections 2.2 and 13 — called out here so the backlog documents boundaries, not just work items:

- Multiple users, social/sharing features, a coach/administrator portal
- Outlook or other calendar integration
- Target finish-time optimisation or competitive race-time prediction
- Nutrition or hydration prescriptions
- Medical diagnosis, injury diagnosis, or rehabilitation plans
- Real-time monitoring or coaching during a run; emergency response
- A full bodybuilding, powerlifting, or muscle-gain programme
- Anything positioned as a replacement for a doctor, physiotherapist, or qualified running coach
