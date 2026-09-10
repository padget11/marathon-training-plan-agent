# Marathon Readiness Coach

## Software Requirements Specification

**Document status:** Draft for MVP  
**Primary user:** The owner and sole user of the application  
**Purpose:** Support preparation for a first marathon, with the priority of reaching the start line healthy, prepared and confident, and completing the event safely rather than achieving a target finish time.

---

## 1. Product Overview

### 1.1 Product vision

The Marathon Readiness Coach is a personal AI-supported training assistant that combines Garmin Connect data with the user's own feedback to create and adapt a first-marathon training plan.

The coach will plan and review:

- Running sessions
- Mobility sessions
- Strength sessions
- Rest and recovery
- Marathon preparation progress

The product will focus on consistency, gradual progression, recovery and completion readiness. It will not optimise training around a target race time unless that requirement is deliberately added in a future version.

### 1.2 Problem statement

Static marathon plans assume that every planned session is completed and often do not account for how the runner feels. Garmin provides useful measured data, but measured data alone does not describe soreness, confidence, discomfort, motivation or perceived effort.

The product must combine:

1. Objective data from Garmin Connect
2. Subjective feedback from the user
3. The current training plan and recent training history
4. Conservative first-marathon planning rules

### 1.3 Success statement

The product is successful if it helps the user train consistently, adapt safely when sessions are missed or recovery is poor, incorporate mobility and strength work, and build sufficient readiness to complete a first marathon.

---

## 2. Scope

### 2.1 In scope for the MVP

- One user only
- A persistent runner profile
- Garmin Connect integration through an MCP server
- Import or retrieval of relevant Garmin running and recovery information
- Initial marathon plan generation
- Weekly plans containing running, mobility, strength and recovery
- Post-run check-ins
- Weekly wellbeing check-ins
- Adaptive replanning
- Weekly reviews
- Marathon completion-readiness assessments
- Explanations for material planning changes
- Persistent storage of plans, check-ins and coaching decisions
- Conservative safety rules and escalation language

### 2.2 Out of scope for the MVP

- Multiple users
- Social features or sharing
- Coach or administrator portal
- Outlook or other calendar integration
- Target finish-time optimisation
- Competitive race-time prediction
- Nutrition or hydration prescriptions
- Medical diagnosis
- Injury diagnosis or rehabilitation plans
- Real-time monitoring during a run
- Emergency response
- A full bodybuilding, powerlifting or muscle-gain programme
- Replacement for advice from a doctor, physiotherapist or qualified running coach

### 2.3 Possible future scope

- Sending structured workouts to Garmin
- Race-day pacing guidance
- Nutrition and hydration planning using appropriately reviewed guidance
- Training-plan visualisation
- Voice-based post-run check-ins
- Route planning
- Shoe and equipment tracking
- Export of plans and reviews

---

## 3. User and Operating Assumptions

### 3.1 User

There is one persona: the application's owner and sole user.

The user:

- Is preparing for their first marathon
- Uses Garmin to record running and related fitness information
- Does not currently have a target finish time
- Wants the plan to focus on successful completion
- Wants mobility included as a core part of training
- Wants appropriate strength training included
- Wants the agent to consider both Garmin data and how each run felt
- Does not require calendar integration

### 3.2 Assumptions

- The user has a compatible Garmin account and records relevant activities.
- The selected Garmin MCP server can access the required Garmin data.
- Garmin data may occasionally be missing, delayed or incomplete.
- The user can provide basic information that Garmin does not contain.
- The agent will be used regularly enough to capture post-run and weekly feedback.
- Where data is absent or conflicting, the system will favour a conservative recommendation and disclose the uncertainty.

---

## 4. Product Principles

The following principles shall guide all planning and recommendations, in priority order:

1. **Health and safety:** Avoid advice likely to increase injury or excessive-fatigue risk.
2. **Completion before speed:** Prepare the user to complete a first marathon rather than chase a finish time.
3. **Consistency before intensity:** Prefer repeatable training over isolated hard sessions.
4. **Subjective and objective evidence:** Treat user feedback as essential evidence, not a secondary note.
5. **Recovery is training:** Schedule rest, mobility and reduced-load periods deliberately.
6. **Minimum effective strength:** Use strength work to support running without creating unnecessary fatigue.
7. **Explain material changes:** State why the plan has changed and what evidence informed the decision.
8. **No catch-up training:** Do not compress missed mileage or hard sessions into the remaining days of a week.
9. **Uncertainty must be visible:** Do not present incomplete Garmin data or uncertain conclusions as facts.
10. **User control:** The user can accept, reject or request a change to any proposed session.

---

## 5. System Context and Conceptual Architecture

```text
Garmin Connect
      |
      v
Garmin MCP Server
      |
      v
Marathon Readiness Coach
      |
      +--> Coaching skill and planning rules
      +--> Runner profile
      +--> Training plan and session history
      +--> Subjective check-ins
      +--> Weekly reviews and readiness history
```

### 5.1 Separation of responsibilities

#### Garmin Connect

Garmin Connect is the source of truth for recorded activities and Garmin-produced health, recovery and training metrics.

#### Garmin MCP server

The MCP server provides tools through which the agent can request available Garmin data. The MCP integration should not be treated as the system of record for the user's plan or subjective feedback.

#### Coaching skill

The coaching skill contains the reusable instructions, decision rules, output formats and safety constraints that govern how the agent plans and reviews training.

#### Local application state

Local application state stores information that may not exist in Garmin, including:

- Marathon date
- First-marathon goal
- Availability and preferences
- Strength equipment
- Mobility preferences
- Planned sessions
- User check-ins
- Missed-session reasons
- Soreness or discomfort reports
- Planning adjustments and their rationales

---

## 6. Functional Requirements

Priority labels:

- **Must:** Required for the MVP
- **Should:** Important, but the MVP can operate with a limited version
- **Could:** Optional enhancement

### FR-001: Runner profile

**Priority:** Must

The system shall create and maintain a single runner profile.

The profile shall support:

- Marathon date
- Goal type, defaulting to `complete first marathon`
- Running experience
- Current typical weekly running distance
- Longest recent run
- Preferred or available running days
- Preferred long-run day
- Current mobility practice
- Current strength-training experience
- Available strength equipment
- Relevant restrictions voluntarily entered by the user
- Units, defaulting to kilometres

The system shall not require a target finish time.

If a target time is not provided, the system shall generate sessions using effort, conversational intensity, heart-rate information where appropriate, and completion-oriented progression rather than goal-race pace.

#### Acceptance criteria

- A profile can be created without a target finish time.
- The saved goal clearly identifies this as the user's first marathon.
- The profile can be amended without deleting existing training history.
- The plan uses the user's stated availability and equipment.

---

### FR-002: Garmin authentication and connection

**Priority:** Must

The system shall connect to Garmin Connect through a configured Garmin MCP server.

The system shall:

- Detect whether the Garmin connection is available
- Report authentication or connection failures clearly
- Avoid logging Garmin passwords or tokens in application output
- Avoid displaying secrets in agent responses
- Continue in a limited manual mode if the Garmin service is temporarily unavailable

#### Acceptance criteria

- The system can distinguish between a successful data retrieval and a connection failure.
- A connection failure does not cause fabricated training data to appear.
- The user is told which relevant data could not be retrieved.
- Existing plans and manually recorded feedback remain available during an integration failure.

---

### FR-003: Garmin data retrieval

**Priority:** Must

Subject to data made available by the configured MCP implementation, the system shall retrieve relevant information such as:

- Running activities
- Activity date and duration
- Distance
- Pace or speed
- Heart-rate information
- Elevation information, where available
- Training load or training-status information, where available
- Sleep information, where available
- HRV information, where available
- Training readiness or similar recovery information, where available

The system shall distinguish between:

- Data returned by Garmin
- User-entered information
- Agent-generated interpretation

The system shall not invent missing metrics.

#### Acceptance criteria

- Every analysis identifies the period of Garmin data considered.
- Missing metrics are marked as unavailable rather than estimated without disclosure.
- Duplicate activities are not counted twice.
- Non-running activities are not treated as runs.
- A manually entered run can be included when Garmin data is unavailable, provided it is labelled as user entered.

---

### FR-004: Baseline assessment

**Priority:** Must

Before generating the first plan, the system shall establish a baseline from:

- Runner profile
- Available recent Garmin running history
- Longest recent run
- Recent consistency
- Current mobility and strength habits
- User-reported current condition

The agent shall ask only for material information that is missing and cannot be obtained from Garmin.

The baseline shall not produce a competitive finish-time target by default.

#### Acceptance criteria

- The first plan is not generated solely from the marathon date.
- The baseline records which evidence was available.
- The user can correct an inaccurate baseline.
- Uncertainty caused by limited history is explicitly stated.

---

### FR-005: Initial marathon plan

**Priority:** Must

The system shall create a completion-oriented marathon preparation plan from the baseline to the marathon date.

The plan shall include phases appropriate to the user's available preparation period, which may include:

- Establishing consistency
- Building aerobic volume
- Developing the long run
- Recovery or reduced-load weeks
- Marathon-specific preparation
- Tapering before the event

The plan shall include:

- Running sessions
- Mobility sessions
- Strength sessions
- Rest or recovery days
- A planned long-run progression
- Review points at which the plan can be adjusted

The plan shall remain adaptable and shall not assume every future session will be completed exactly as planned.

#### Acceptance criteria

- The plan works without a target finish time.
- Each planned week contains a clear purpose.
- Each run identifies session type and an effort-based instruction.
- Mobility is visible in the main plan rather than presented as an optional note.
- Strength is included at an appropriate supporting level.
- The final phase contains an explicit taper.

---

### FR-006: Weekly plan generation

**Priority:** Must

The system shall generate a detailed weekly plan using:

- The current plan phase
- Completed recent sessions
- Garmin recovery and training information that is available
- Recent subjective feedback
- Missed or modified sessions
- Current soreness, energy and motivation
- User availability stored in the profile

Each weekly plan shall include, as applicable:

- Session day
- Session category
- Purpose
- Duration or distance
- Effort guidance
- Warm-up guidance
- Cool-down or mobility guidance
- A concise completion criterion
- Any relevant caution or modification

#### Acceptance criteria

- The weekly plan shows all running, mobility, strength and rest sessions together.
- Hard running sessions are not scheduled on consecutive days by default.
- Strength work does not undermine the priority long run.
- The agent explains any material departure from the broader plan.
- The user can request a lower-load version of the week.

---

### FR-007: Running session types

**Priority:** Must

The system shall support the following categories where appropriate:

- Easy run
- Long run
- Recovery run
- Steady run
- Run-walk session
- Technique or strides session
- Controlled quality session
- Optional low-impact cross-training alternative

For this first-marathon, completion-oriented MVP:

- Easy and long runs shall form the main running foundation.
- Quality sessions shall be introduced conservatively.
- Run-walk shall be treated as a valid strategy rather than a failure.
- Sessions shall use effort-based descriptions where no time goal exists.

#### Acceptance criteria

- Every running session has a stated purpose.
- Effort guidance is understandable without advanced sports-science knowledge.
- The plan does not require goal-marathon pace when no target time exists.
- Optional sessions are clearly distinguished from priority sessions.

---

### FR-008: Post-run check-in

**Priority:** Must

After a recorded or manually reported run, the agent shall request subjective feedback unless feedback for that run already exists.

The check-in shall be concise and cover:

- Overall perceived effort
- How the run felt
- Energy level
- Muscle soreness or discomfort
- Any unusual breathing, dizziness, pain or other concerning symptom the user chooses to report
- Confidence or enjoyment, where useful
- Optional free-text comments

A minimum check-in may use:

```text
How did that run feel overall: very easy, easy, moderate, hard or very hard?
Any pain, unusual discomfort or heavy fatigue?
```

The user shall be able to skip a check-in.

#### Acceptance criteria

- Feedback is linked to the correct activity or manually entered run.
- The raw user response is retained without changing its meaning.
- The system distinguishes normal exertion from a user report of pain or concerning symptoms.
- Repeated check-in questions are avoided once a response has been stored.
- Future recommendations consider recent check-ins.

---

### FR-009: Weekly wellbeing check-in

**Priority:** Must

At least once per planning week, the system shall request a broader wellbeing check-in covering:

- General energy
- Motivation
- Stress
- Overall soreness
- Sleep as perceived by the user
- Confidence about the next week's training
- Any factor likely to affect training

The system shall allow structured answers and free text.

#### Acceptance criteria

- The weekly plan records whether a wellbeing check-in was available.
- Low energy, high soreness or concerning feedback can reduce or modify the proposed load.
- Missing wellbeing feedback is disclosed and does not result in invented assumptions.

---

### FR-010: Subjective and Garmin evidence handling

**Priority:** Must

The system shall consider both subjective reports and available Garmin data.

The system shall not use a fixed numerical weighting unless a validated rule is deliberately configured.

Where subjective and Garmin evidence conflict, the system shall:

1. Identify the conflict
2. Ask for relevant context when necessary
3. Favour a conservative decision when safety or recovery may be affected
4. Explain the basis of the recommendation

Example:

```text
Garmin readiness appears normal, but you reported increasing calf pain over two runs. The next run is being replaced with rest or gentle mobility, and the coach recommends seeking an appropriate professional assessment if the pain persists or worsens.
```

#### Acceptance criteria

- A positive Garmin metric does not override a report of pain.
- A single poor Garmin metric does not automatically cancel training without context.
- The explanation identifies which information came from Garmin and which came from the user.

---

### FR-011: Mobility planning

**Priority:** Must

The system shall treat mobility as a planned training component.

Mobility recommendations may address:

- Ankles
- Calves
- Hips
- Glutes
- Hamstrings
- Thoracic movement
- General pre-run movement preparation
- Gentle post-run or recovery movement

Mobility sessions shall be adapted according to:

- Run type
- Running volume
- User-reported stiffness
- User preferences
- Available time

The agent shall avoid representing mobility as treatment for an injury.

#### Acceptance criteria

- Each week contains planned mobility work appropriate to that week's training.
- Mobility may be delivered as short pre-run preparation, post-run work or standalone sessions.
- The plan identifies the intended area or purpose.
- Reported pain prompts caution rather than a prescriptive rehabilitation routine.

---

### FR-012: Strength-training integration

**Priority:** Must

The system shall include strength training to support running durability and general physical preparedness.

The system shall:

- Establish the user's current strength experience
- Establish available equipment
- Begin conservatively for a user new to strength training
- Typically plan one or two sessions where recovery and running load allow
- Reduce session volume during high-running-load periods
- Use maintenance-oriented sessions during peak marathon preparation
- Reduce or remove fatiguing strength work during the taper
- Avoid placing demanding lower-body strength immediately before the priority long run

Strength content may include appropriate patterns such as:

- Squat or sit-to-stand pattern
- Hinge pattern
- Split-stance or lunge pattern
- Calf work
- Single-leg stability
- Trunk stability
- Upper-body movements for balanced general strength

The strength component shall not become a separate hypertrophy or maximal-strength programme.

#### Acceptance criteria

- Strength appears in the weekly plan.
- Sessions include a purpose, exercise selection, sets or duration, and an effort limit.
- The session can be adapted to the equipment in the runner profile.
- Strength load is reduced when run load or fatigue is high.
- Missed strength work is not automatically moved next to a long or hard run.

---

### FR-013: Rest and recovery

**Priority:** Must

The system shall explicitly schedule recovery.

The system shall support:

- Full rest
- Gentle mobility
- Optional easy walking
- Low-impact cross-training where appropriate
- Reduced-load weeks
- Additional recovery after demanding or poorly tolerated sessions

The agent shall not present rest as a training failure.

#### Acceptance criteria

- Every weekly plan includes adequate recovery opportunities.
- A recovery day is not silently converted into a hard session to recover missed mileage.
- Reduced-load decisions include a concise rationale.

---

### FR-014: Adaptive replanning

**Priority:** Must

The system shall replan after events including:

- Missed run
- Shortened run
- Run completed harder or easier than intended
- Poor recovery indicators
- Pain, unusual discomfort or excessive fatigue reported by the user
- Unavailability for a planned day
- Garmin data becoming unavailable
- Unexpected additional exercise

The replanning process shall:

- Protect the priority of recovery
- Avoid stacking demanding sessions
- Avoid attempting to recover all missed distance
- Consider replacing, reducing, moving or removing a session
- Preserve the broader marathon objective where reasonably possible
- Explain what changed and why

#### Acceptance criteria

- A missed session does not automatically increase later sessions.
- The revised week remains internally consistent.
- The previous plan version remains available in history.
- The adjustment records its evidence and rationale.

---

### FR-015: Weekly review

**Priority:** Must

The system shall produce a weekly review containing:

#### Planned versus completed

- Planned sessions
- Completed sessions
- Modified, missed or skipped sessions
- Total recorded running distance and duration, where available
- Long-run completion
- Mobility completion
- Strength completion

#### Objective observations

- Relevant Garmin trends available for the week
- Explicit identification of missing Garmin information

#### Subjective observations

- Summary of post-run feedback
- Summary of the weekly wellbeing check-in
- Recurring soreness, discomfort, fatigue or confidence themes

#### Coaching interpretation

- What supported progress
- What may require attention
- Proposed changes for the next week
- Confidence and limitations of the assessment

#### Acceptance criteria

- Objective data, user feedback and coach interpretation are distinguishable.
- The review does not invent explanations for missing sessions.
- The review informs the next weekly plan.
- Concerning feedback is not buried in a general summary.

---

### FR-016: Completion-readiness assessment

**Priority:** Must

The system shall assess readiness to complete the marathon without requiring a finish-time target.

The assessment shall consider available evidence relating to:

- Training consistency
- Long-run progression
- Ability to recover
- Tolerance of recent training
- Subjective confidence
- Remaining preparation time
- Interruptions or unresolved concerns

The output shall use understandable categories such as:

- On track for completion
- Progressing, with areas to address
- Preparation disrupted or currently uncertain
- Insufficient evidence to assess

The agent shall not guarantee that the user will finish or remain injury free.

#### Acceptance criteria

- The output does not require or invent a target finish time.
- The evidence for the status is listed.
- Limitations and missing evidence are stated.
- The assessment provides practical next priorities rather than only a label.

---

### FR-017: Explanation and traceability

**Priority:** Must

For every material plan change, the system shall record:

- What changed
- The evidence considered
- The reason for the change
- Whether the evidence came from Garmin, the user or the plan state
- Any uncertainty

#### Acceptance criteria

- The user can understand why distance, intensity, strength or recovery changed.
- An agent-generated interpretation is not presented as a Garmin measurement.
- A plan version can be traced to the check-ins and completed activities considered at the time.

---

### FR-018: Manual data entry and correction

**Priority:** Must

The user shall be able to:

- Add an unrecorded run
- Correct incorrectly classified information
- Mark a session completed, modified, skipped or missed
- Add post-run feedback later
- Correct their profile
- Override a proposed plan

Manual changes shall be labelled and retained in an audit history.

#### Acceptance criteria

- Corrections do not silently alter the original Garmin source record.
- The current plan reflects accepted user corrections.
- The user can see the current effective value when Garmin and manual data differ.

---

### FR-019: Commands or supported intents

**Priority:** Should

The agent should recognise natural-language requests and may expose concise commands equivalent to:

- `/create-plan`
- `/this-week`
- `/log-feedback`
- `/adjust-week`
- `/weekly-review`
- `/readiness`
- `/profile`
- `/data-status`

Commands are shortcuts and shall not be required for normal use.

#### Acceptance criteria

- The user can complete core workflows in natural language.
- Command output follows the same safety and evidence rules as conversational output.

---

### FR-020: Data status

**Priority:** Should

The system should provide a clear data-status view showing:

- Garmin connection state
- Most recent successful synchronisation or retrieval, if recorded
- Period covered by retrieved activity data
- Missing expected data types
- Outstanding post-run check-ins
- Date of the latest weekly wellbeing check-in
- Current plan version

#### Acceptance criteria

- The user can tell whether advice is based on current, partial or unavailable Garmin data.
- The view does not expose authentication secrets.

---

## 7. Data Requirements

### 7.1 Proposed persistent entities

#### Runner profile

```yaml
runner:
  id: owner
  marathon_date: null
  goal_type: complete_first_marathon
  target_time: null
  units: metric
  running_experience: first_marathon
  typical_weekly_distance_km: null
  longest_recent_run_km: null
  available_running_days: []
  preferred_long_run_day: null
  mobility_preferences: []
  strength:
    experience: null
    equipment: []
    preferred_sessions_per_week: null
  user_entered_restrictions: []
```

#### Training plan

```yaml
plan:
  id: null
  version: 1
  created_at: null
  marathon_date: null
  goal_type: complete_first_marathon
  current_phase: null
  weeks: []
  evidence_snapshot_id: null
  status: active
```

#### Planned session

```yaml
session:
  id: null
  planned_date: null
  category: run | mobility | strength | recovery | cross_training
  subtype: null
  purpose: null
  planned_distance_km: null
  planned_duration_minutes: null
  effort_guidance: null
  priority: priority | supporting | optional
  status: planned | completed | modified | skipped | missed
  linked_garmin_activity_id: null
```

#### Post-run check-in

```yaml
post_run_check_in:
  id: null
  session_id: null
  garmin_activity_id: null
  recorded_at: null
  perceived_effort: very_easy | easy | moderate | hard | very_hard
  overall_feeling: null
  energy: null
  soreness_or_discomfort: null
  concerning_symptoms_reported: false
  confidence_or_enjoyment: null
  free_text: null
```

#### Weekly wellbeing check-in

```yaml
weekly_check_in:
  week_start: null
  energy: null
  motivation: null
  stress: null
  soreness: null
  perceived_sleep: null
  confidence: null
  free_text: null
```

#### Coaching decision

```yaml
coaching_decision:
  id: null
  recorded_at: null
  plan_version_before: null
  plan_version_after: null
  change_summary: null
  garmin_evidence: []
  user_evidence: []
  plan_evidence: []
  rationale: null
  uncertainty: null
```

### 7.2 Data ownership and sources of truth

- Garmin Connect shall remain the source of truth for Garmin-recorded activities and Garmin-generated metrics.
- The application's persistent state shall be the source of truth for runner preferences, subjective feedback, generated plans and coaching decisions.
- The system shall preserve provenance so that imported, user-entered and agent-generated information can be distinguished.

### 7.3 Data retention

The MVP shall retain:

- The active runner profile
- Training-plan versions
- Session completion state
- Subjective check-ins
- Weekly reviews
- Coaching decisions

The application shall support deletion or reset of locally persisted personal training state.

### 7.4 Data minimisation

The application shall store only data needed for planning, review and traceability. It should avoid making unnecessary local copies of complete Garmin datasets when the required information can be retrieved from Garmin when needed.

---

## 8. Safety Requirements

### SR-001: Not medical advice

The system shall state clearly that it is not a medical professional and does not diagnose injuries or medical conditions.

### SR-002: Concerning symptoms

If the user reports severe, sudden, worsening or otherwise concerning symptoms, the agent shall stop normal performance coaching for the affected session and advise the user to seek appropriate professional or urgent medical support depending on the circumstances.

### SR-003: Pain handling

The system shall not treat pain as a normal metric to train through. It shall avoid prescribing injury rehabilitation and shall recommend appropriate professional assessment when pain persists, worsens or affects normal movement.

### SR-004: Conservative uncertainty handling

Where available evidence is incomplete or conflicting, the agent shall prefer a lower-risk recommendation and identify the uncertainty.

### SR-005: No guarantees

The system shall not guarantee race completion, a result, injury prevention or health outcomes.

### SR-006: User override

The user may reject a recommendation, but the system shall not remove or weaken a relevant safety warning merely because the user asks for more aggressive training.

### SR-007: Sensitive data

Authentication tokens, passwords and other secrets shall not be included in prompts, logs, plan files or conversational output.

---

## 9. Non-Functional Requirements

### NFR-001: Usability

- Core workflows shall work through plain conversational language.
- Weekly plans shall be readable without specialist running terminology.
- Technical metrics shall be explained when they materially affect a decision.
- The most important session and recovery information shall be easy to identify.

### NFR-002: Explainability

- Material recommendations shall include a concise rationale.
- Garmin facts, user comments and agent interpretations shall be distinguishable.
- Missing data shall be disclosed.

### NFR-003: Reliability

- Failure to retrieve Garmin data shall not corrupt the saved plan.
- The system shall not duplicate activities during repeated retrieval.
- Replanning shall create a new plan version rather than silently overwriting history.

### NFR-004: Privacy and security

- Sensitive local files shall use restrictive access permissions where supported.
- Secrets shall be stored separately from training state.
- Logs shall avoid unnecessary health and authentication information.
- The user shall be able to delete local state.

### NFR-005: Performance

- The system should retrieve only the data needed for the current workflow.
- Routine weekly planning should use summaries rather than unnecessarily loading complete raw activity tracks.

### NFR-006: Portability

- Coaching logic should remain separate from the selected Garmin MCP implementation.
- Replacing or upgrading the Garmin connector should not require a rewrite of the training methodology.

### NFR-007: Maintainability

- Planning rules, prompts, data access and persistence should be separate components.
- Requirements and decision rules should be version controlled.
- Changes to safety rules should be reviewable independently of interface changes.

### NFR-008: Auditability

- Every plan shall have a version.
- Material changes shall record their rationale and evidence sources.
- User corrections shall not be silently discarded.

---

## 10. Agent Behaviour Requirements

### 10.1 Tone

The coach shall be:

- Supportive
- Calm
- Practical
- Non-judgemental
- Encouraging without overstating progress

### 10.2 Interaction style

The coach shall:

- Avoid overwhelming the user with raw metrics
- Ask concise, relevant questions
- Avoid repeatedly asking for information already stored
- Clearly identify priority sessions
- Frame rest and run-walk approaches positively
- Avoid guilt-based language after missed sessions

### 10.3 Evidence discipline

The coach shall:

- Use retrieved Garmin values only when available
- State the date range or activities considered
- Avoid interpreting correlation as a medical cause
- Label suggestions as recommendations, not certainties
- Avoid fixed subjective-versus-Garmin percentages unless a validated algorithm is later adopted

### 10.4 Example response structure

```markdown
## Recommendation
Reduce tomorrow's run to an easy, shorter session or take a rest day.

## Why
- Garmin source: recovery information was lower than your recent pattern.
- Your feedback: you reported heavy legs and unusually high effort after the last run.
- Plan context: the priority long run is later this week.

## Updated week
[Revised sessions]

## Check-in
Let me know whether the heaviness improves and whether there is any pain or unusual discomfort.
```

---

## 11. Core User Journeys

### Journey 1: Onboarding

1. User connects Garmin MCP.
2. Agent checks whether required Garmin tools and data are available.
3. Agent creates the single runner profile.
4. Agent retrieves relevant recent running history.
5. Agent asks for material missing context, including marathon date, availability, strength equipment and current condition.
6. Agent presents a baseline for correction.
7. User accepts or updates the baseline.

### Journey 2: Create the first plan

1. Agent uses the accepted baseline and race date.
2. Agent creates a completion-oriented phased plan.
3. Agent includes running, mobility, strength and recovery.
4. Agent explains the immediate phase and first week's priorities.
5. Plan version 1 is persisted.

### Journey 3: Post-run review

1. Garmin records a run or the user reports one manually.
2. Agent retrieves or receives the run details.
3. Agent asks how the run felt and whether there was pain, unusual discomfort or heavy fatigue.
4. User responds.
5. Feedback is linked to the run.
6. Agent provides a short observation or updates a future session if required.

### Journey 4: Missed session

1. User reports a missed or unavailable session.
2. Agent checks the remaining week, fatigue and priority sessions.
3. Agent removes, replaces or moves the session without forcing catch-up mileage.
4. Agent explains the adjustment.
5. A new plan version is persisted.

### Journey 5: Weekly review and next plan

1. Agent retrieves the week's available Garmin data.
2. Agent identifies completed and missed sessions.
3. Agent incorporates post-run and weekly wellbeing feedback.
4. Agent produces the weekly review.
5. Agent creates the next week's plan.
6. User can accept or request changes.

### Journey 6: Readiness check

1. User requests a completion-readiness assessment.
2. Agent examines consistency, long-run progression, recovery, tolerance, confidence and remaining preparation time.
3. Agent provides a status, supporting evidence, limitations and next priorities.
4. Agent does not invent a target time or guarantee completion.

---

## 12. MVP Acceptance Scenarios

### Scenario A: No target finish time

**Given** the user is training for a first marathon and has no target time  
**When** the first plan is created  
**Then** the system provides effort-based training aimed at completion  
**And** it does not require or invent goal-marathon pace.

### Scenario B: Garmin and user feedback conflict

**Given** Garmin recovery information appears acceptable  
**And** the user reports increasing calf pain  
**When** the next session is reviewed  
**Then** the system does not rely on the Garmin metric to dismiss the report  
**And** it recommends a conservative adjustment and appropriate professional support if the issue persists or worsens.

### Scenario C: Missed long run

**Given** the user misses a planned long run  
**When** the week is replanned  
**Then** the system does not add the full missed distance to another run  
**And** it protects recovery and subsequent priority sessions.

### Scenario D: High running load

**Given** the training block reaches a higher running load  
**When** the weekly plan is generated  
**Then** strength training is reduced to an appropriate maintenance level  
**And** mobility and recovery remain visible.

### Scenario E: Garmin unavailable

**Given** Garmin retrieval fails  
**When** the user requests a weekly plan  
**Then** the system labels Garmin data as unavailable  
**And** uses saved plan state and user-provided information conservatively  
**And** does not fabricate activity or recovery metrics.

### Scenario F: Incomplete post-run feedback

**Given** a completed run has no check-in  
**When** the agent next reviews that run  
**Then** it asks a concise post-run question  
**And** allows the user to skip it  
**And** marks subjective evidence as unavailable if skipped.

### Scenario G: Taper period

**Given** the user enters the taper phase  
**When** the weekly plan is generated  
**Then** running load is reduced appropriately  
**And** fatiguing strength work is reduced or removed  
**And** the plan prioritises freshness and confidence.

---

## 13. MVP Priorities

### Must have

- Single-user runner profile
- Garmin MCP connection and data retrieval
- Manual fallback and correction
- First-marathon, completion-oriented plan
- Weekly running plan
- Post-run subjective check-in
- Weekly wellbeing check-in
- Mobility planning
- Supporting strength sessions
- Rest and recovery planning
- Adaptive replanning
- Weekly review
- Completion-readiness assessment
- Persistent plan and feedback history
- Evidence provenance and explanations
- Safety behaviours

### Should have

- Natural-language command shortcuts
- Data-status view
- Plan version comparison
- Optional low-impact cross-training alternatives
- Exportable weekly summary

### Could have

- Structured workouts written back to Garmin
- Charts and trend visualisations
- Voice check-ins
- Race-day checklist
- Shoe and equipment tracking

### Will not have in the MVP

- Multiple users
- Calendar integration
- Social or sharing features
- Competitive goal-time optimisation
- Medical diagnosis
- Rehabilitation programming
- Full nutrition coaching
- Real-time run coaching

---

## 14. Suggested Implementation Components

This section is an implementation suggestion rather than a binding product requirement.

```text
marathon-readiness-coach/
├── SKILL.md
├── references/
│   ├── coaching-principles.md
│   ├── mobility-guidance.md
│   ├── strength-guidance.md
│   ├── safety-rules.md
│   └── output-templates.md
├── state/
│   ├── runner-profile.yaml
│   ├── active-plan.yaml
│   ├── check-ins.jsonl
│   └── coaching-decisions.jsonl
├── scripts/
│   ├── validate_profile.py
│   ├── reconcile_activities.py
│   └── version_plan.py
└── tests/
    ├── acceptance-scenarios.md
    └── safety-scenarios.md
```

Recommended responsibility boundaries:

- `SKILL.md`: workflow, triggers, decision sequence and response format
- `references/`: detailed rules loaded only when relevant
- `state/`: evolving personal plan and feedback
- `scripts/`: deterministic validation, reconciliation and versioning
- Garmin MCP: Garmin data access and permitted Garmin write operations

---

## 15. Decisions Already Made

| Decision | Outcome |
|---|---|
| Number of users | One |
| Marathon experience | First marathon |
| Primary objective | Complete the marathon rather than achieve a target time |
| Target finish time required | No |
| Garmin integration | Yes, through MCP |
| Subjective post-run feedback | Required workflow, but user may skip |
| Weekly wellbeing feedback | Included |
| Mobility | Core part of the plan |
| Strength | Included as supporting training |
| Calendar integration | Not required |
| Garmin as source of truth for activities | Yes |
| Local persistence | Profile, plans, check-ins and coaching decisions |
| Medical diagnosis or rehabilitation | Out of scope |

---

## 16. Open Design Decisions

These decisions do not block the requirements draft but should be resolved during implementation:

1. Which Garmin MCP implementation will be used?
2. Which exact Garmin tools and metrics are available in that implementation?
3. Where will local state be stored and encrypted or otherwise protected?
4. Will the application run only on the user's computer or on a privately hosted service?
5. How will scheduled post-run check-ins be initiated if the agent is not continuously running?
6. Will structured workouts initially remain in the plan only, or also be written to Garmin?
7. What plan-version and backup strategy will be used?
8. What reviewed coaching references will underpin progression, strength, mobility and taper rules?
9. What specific wording and escalation rules will be used for reports of concerning symptoms?
10. What minimum Garmin evidence is required before trend-based conclusions are shown?

---

## 17. Definition of Done for the MVP

The MVP is complete when:

- A single runner profile can be created and persisted.
- The profile supports a first-marathon completion goal without a target time.
- The application can retrieve supported Garmin running data through MCP.
- The application handles unavailable Garmin data without fabrication.
- An initial phased marathon plan can be generated.
- Weekly plans include running, mobility, strength and recovery.
- The user can record how a run felt.
- Subjective feedback can alter future recommendations.
- A missed run can trigger safe replanning without catch-up mileage.
- A weekly review can distinguish Garmin data, user feedback and agent interpretation.
- A completion-readiness assessment can be produced without predicting a finish time.
- Plans, check-ins and material coaching decisions are persisted and versioned.
- Safety scenarios pass, including pain reports and conflicting Garmin data.
- The system clearly states relevant limitations and does not provide medical diagnosis.

---

## 18. Requirement Traceability Summary

The central product objective, preparing safely to complete a first marathon, is supported by:

- Baseline and plan creation: FR-001 to FR-007
- Human feedback: FR-008 to FR-010
- Mobility, strength and recovery: FR-011 to FR-013
- Adaptation and learning: FR-014 to FR-018
- Usability and transparency: FR-019 to FR-020 and NFR-001 to NFR-008
- Safety boundaries: SR-001 to SR-007

---

*End of document.*
