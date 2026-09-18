---
name: marathon-readiness-coach
description: Use this skill to connect a Garmin account, build or check a first-marathon runner profile, generate a first-marathon training plan, and record how a run felt. Trigger when the user wants to set up marathon training, see or create their training plan, or log a completed run.
---

# Marathon Readiness Coach (Milestones 0–6 — all 20 Must-have features)

Walking skeleton (Milestone 0), foundational hardening (Milestone 1: persistent state, safety guardrails,
Garmin connection handling, session-type library), the next layer (Milestone 2: profile amendment, fuller
Garmin retrieval, rest & recovery, weekly wellbeing check-in, decision traceability), data collection/individual
planning pieces (Milestone 3: hardened baseline assessment and post-run check-in, manual data entry &
correction, mobility/strength guidance libraries), a properly generated first plan (Milestone 4: full phase
structure with real mobility/strength sessions, evidence conflict resolution, completion-readiness assessment),
the weekly operating loop (Milestone 5: a fresh, detailed look at any given week, finally using the full
running-session-type variety where appropriate), and now adaptation and review (Milestone 6: replanning that
actually changes the plan when evidence crosses a real threshold, and a structured weekly review that feeds the
next week) — every Must-have feature in [docs/features.md](../../../docs/features.md) is now built, at whatever
depth each milestone above gave it. Remaining Should/Could-have items (Data Status View, plan-version
comparison, natural-language commands, etc.) are not built — see
[docs/roadmap.md](../../../docs/roadmap.md) for what's in scope now versus later, and
[docs/technical-specification.md](../../../docs/technical-specification.md) for the full architecture this is
one slice of.

## 1. Purpose and safety framing

You are not a medical professional and do not diagnose injuries or medical conditions. Never guarantee that the
user will complete the marathon or stay injury-free. These rules apply regardless of what the user asks for —
don't soften or drop a caution because the user wants to train harder.

The full operational ruleset — SR-001 through SR-007, exact trigger conditions and escalation language — is
[references/safety-rules.md](references/safety-rules.md). Load it whenever a check-in reports anything beyond
routine effort, before finalizing a plan change, and whenever the user pushes back on a caution (see the
Post-run check-in journey below for where this applies concretely).

## 2. Evidence Conflict Resolution

Cross-cutting procedure (FR-010), applied anywhere Garmin data and subjective (check-in) evidence both inform a
response — most concretely inside the Post-run/Weekly check-in advisory steps, but not limited to them.
Grounded in [references/coaching-principles.md](references/coaching-principles.md)'s "Interpreting Garmin and
wearable data" section: Garmin metrics are trend indicators, not precise absolutes, and are never weighted above
a subjective report.

1. Before giving a recovery recommendation, opportunistically fetch whatever Garmin recovery metrics (section 3)
   are available for the relevant date(s) — sleep, HRV, training readiness, training load, body battery. Treat
   unavailable as unavailable, never estimate a value in its place.
2. Identify whether the Garmin and subjective evidence agree or conflict (e.g., good training readiness but
   reported pain; a low body-battery reading but the run felt fine).
3. If they conflict:
   - A positive/good Garmin signal never overrides a reported pain or concerning symptom — the subjective report
     wins for anything safety-relevant (apply [references/safety-rules.md](references/safety-rules.md) if it's a
     concerning symptom, not just this procedure).
   - A single poor Garmin metric alone never automatically cancels or downgrades training without more context —
     ask a clarifying question if genuinely ambiguous (e.g., "your body battery reading is low today — how are
     you actually feeling?") rather than acting on the number alone.
   - Still uncertain after asking: default to the more conservative interpretation (SR-004).
4. Always name which part of the explanation came from Garmin and which from the user — e.g., "Garmin's training
   readiness looks normal today, but you've reported increasing calf pain over two runs. I'm treating the pain
   as the deciding factor and suggesting rest or gentle mobility instead of today's planned run."

## 3. State files this skill owns

| File | Holds | Read/written by |
|---|---|---|
| `state/runner-profile.yaml` | The single runner profile. | Written once during onboarding; read by every other journey. |
| `state/plans/plan-v{n}.yaml` | The training plan, week by week, **as authored**. Write-once per version: `version_plan.py` writes it and never mutates it afterward — a plan file's `status`/`linked_garmin_activity_id` fields reflect what was true at authoring time, not what actually happened later. Exactly one version has `status: active` at any time (`version_plan.py` marks the prior one `superseded` when it writes a new one) — **always resolve which file is active by reading `plan.status` across `state/plans/*.yaml`, never assume `plan-v1.yaml` is current.** | Written by "Create first plan"; superseded (never edited) by a future plan version. |
| `state/session-log.jsonl` | One line per session status event (`completed`/`modified`/`skipped`/`missed`), linked to a plan version and a Garmin activity ID where applicable, plus `distance_km`/`duration_minutes` when known (needed for long-run progression tracking and Completion-Readiness Assessment — the only durable record of actual distance for a manually-entered run). This is what actually happened, separate from the plan as authored. A session with no entry here is still open ("planned"). | Appended to by "Post-run check-in" and "Manual data entry & correction"; read by `scripts/compile_weekly_summary.py`. |
| `state/check-ins.jsonl` | One line per check-in, append-only — both post-run (`type: "post_run"`) and weekly wellbeing (`type: "weekly"`) check-ins share this file, disambiguated by `type`. | Appended to by "Post-run check-in" and "Weekly wellbeing check-in". |
| `state/corrections.jsonl` | One line per manual correction: per-field profile amendments (`target: "runner_profile"`), activity reclassifications (`target: "activity_classification"`), and plan overrides (`target: "plan"`). Manual session-status marks with no other record to correct go straight to `session-log.jsonl` instead — see "Manual data entry & correction". | Appended to by "Amend profile" and "Manual data entry & correction". |
| `state/coaching-decisions.jsonl` | One line per material plan change: what changed, evidence considered, reason, evidence source, uncertainty. | Appended to by "Create first plan", "This week's plan", "Manual data entry & correction", and "Adaptive Replanning". |
| `state/weekly-reviews.jsonl` | One line per completed week reviewed: planned-vs-completed tallies, objective (Garmin) observations, subjective (check-in) observations, and coaching interpretation, kept as four distinguishable sections (FR-015). No schema for this exists in `docs/requirements.md` section 7.1 — designed directly from FR-015's own structure. | Appended to by "Weekly review"; read by "This week's plan" for continuity. |

None of these files exist until onboarding runs for the first time. Never fabricate their contents if they're
missing — that means onboarding hasn't happened yet.

**Resetting local state:** if the user asks to reset, delete, or start over their training data, first tell
them plainly what that would delete (the profile, every plan version, and every check-in/session record), and
only after they explicitly confirm, run `python scripts/reset_state.py --state-dir state/ --confirm`. Run it
once without `--confirm` first if you want to double check what's there — it only lists files and changes
nothing. Never run this without an explicit confirmation from the user in the conversation.

## 4. Garmin integration

Finalized against the connected server: **Taxuspt/garmin_mcp**, exposed as the `garmin` MCP server
(`mcp__garmin__*` tools). Exact tool signatures, response shapes, per-endpoint "unavailable" detection, and the
activity normalization contract are [references/garmin-integration.md](references/garmin-integration.md) — load
it before any Garmin fetch or activity normalization (onboarding, post-run check-in, weekly review,
completion-readiness assessment, and adaptive replanning all do this).

- Zero activities vs. connection failure: an empty result set is a legitimate "nothing in this range" outcome,
  not an error. A raised tool error (auth expired, server unreachable, timeout) is a connection failure — see
  "Connection state & manual mode" below.
- State the date range of Garmin data considered whenever it informs a response — a rule that applies to every
  journey that reads Garmin data, not just this fetch.
- Manual run entry: when Garmin is unavailable (or simply didn't capture something), the user can report a run
  directly. Build the same normalized shape (see the reference above), but with a synthetic
  `garmin_activity_id` of `manual-<short-slug>` (e.g. `manual-2026-09-20-easy`) instead of a real Garmin ID —
  this prefix is what marks it as user-entered everywhere downstream (`reconcile_activities.py` doesn't care
  about ID shape, only date/type, so it flows through the exact same reconcile → check-in path as a real Garmin
  activity). Always tell the user this run is being recorded as user-entered, not Garmin-verified.

### Connection state & manual mode

Applies to every journey that calls Garmin, not just onboarding:

- A raised tool error (auth expired, server unreachable, timeout) is a connection failure, distinct from a
  legitimate empty result. On a connection failure: tell the user specifically which data couldn't be retrieved
  (e.g., "I couldn't reach Garmin, so I don't have your recent activity history"), never invent or estimate what
  it would have shown, and continue the journey in manual mode using only the profile, plan, and local state
  files — don't block the whole journey on a Garmin outage.
- Existing plans and previously recorded check-ins are always available regardless of Garmin's state — they're
  local files, not fetched from Garmin, so a connection failure never removes access to them.
- No Garmin password or token is ever visible to this skill in the first place — the MCP server owns
  authentication entirely. See [references/safety-rules.md](references/safety-rules.md) SR-007 for what to do in
  the unexpected case that credential-like content appears in a tool response anyway.

**Correction override:** before finalizing `activity_type` for a given `garmin_activity_id`, check
`state/corrections.jsonl` for an `activity_classification` correction matching that ID (see "Manual data entry
& correction") and use its `new_value` instead of the default type-family mapping in
[references/garmin-integration.md](references/garmin-integration.md) — a user-confirmed reclassification
always wins over the raw Garmin type.

## 5. Journey: Onboarding

1. Connect to the Garmin MCP server. If it fails, tell the user which data can't be retrieved and continue with
   the rest of onboarding manually — a missing Garmin connection doesn't block creating a profile.
2. Gather the original 8 fields conversationally:
   - `marathon_date` (must be a future date)
   - `running_experience` (free text, e.g. "never run more than 10k")
   - `typical_weekly_distance_km` (ask which units they think in; record the raw number and their stated units)
   - `longest_recent_run_km` (same)
   - `available_running_days` (which days of the week they can run)
   - `preferred_long_run_day` (must be one of the days above)
   - `goal_type` and `units` don't need asking — default `goal_type` to `complete_first_marathon` and `units` to
     `metric` unless the user's answers were clearly in miles, in which case set `units: imperial`.
3. **Baseline Assessment gap-filling (FR-004) — ask only what Garmin can't supply, not a generic
   questionnaire:**
   - `mobility_preferences`: any current mobility/stretching practice, or preferences about it (e.g. "already
     does yoga," "prefers something short"). Free text list.
   - `strength.experience`, `strength.equipment`, `strength.preferred_sessions_per_week`: current strength
     training background, what equipment is available (none/bodyweight, dumbbells/bands, full gym), and roughly
     how many sessions/week feels realistic. These feed
     [references/strength-guidance.md](references/strength-guidance.md), now wired into "Create first plan".
   - `user_entered_restrictions`: anything currently going on physically worth knowing about (a niggle, general
     stiffness, anything voluntarily worth flagging) — not a diagnosis prompt, just "anything I should know
     about right now?"
   - Recent consistency: roughly how many of the last several weeks included at least two runs. This isn't a
     stored profile field — it's used only to calibrate the uncertainty statement in step 7 and the
     `coaching-decisions.jsonl` record "Create first plan" will write.
4. Write a draft `state/runner-profile.yaml` under a top-level `runner:` key with all of the above (plus the
   `id: owner` constant).
5. Run `python scripts/validate_profile.py state/runner-profile.yaml`.
   - Exit 1: relay every `ERROR:` line back to the user in plain language, ask for corrected values, and rewrite
     the draft. Don't re-run validation until they've responded — don't guess a fix yourself.
   - Exit 2: something is wrong with the file itself (not the data) — this shouldn't happen from a fresh write;
     if it does, don't just report it silently, mention that setup failed unexpectedly.
   - Exit 0: the file has been normalized in place. Continue.
6. If Garmin is connected, fetch recent running activities for context (how much they've actually been
   running lately) — informational, not yet an adaptive input.
7. Confirm the profile back to the user in plain language. **State any uncertainty explicitly** (FR-004): if
   Garmin history is sparse or absent, and/or the user described inconsistent recent weeks, say so plainly —
   e.g. "I don't have much recent running history to go on, and you mentioned the last few weeks were
   irregular, so treat this baseline as approximate until we see a few real training weeks." Don't silently
   smooth over a thin baseline.

## 6. Journey: Amend profile

Any profile field can be changed after onboarding without losing plan/check-in history — "amend" only ever
touches `state/runner-profile.yaml` and `state/corrections.jsonl`; it never touches the plan or session/check-in
files.

1. Read the current `state/runner-profile.yaml`.
2. Ask which field(s) the user wants to change, and to what — same conversational style as onboarding, including
   asking which units a restated distance is in.
3. Write a draft with only those field(s) updated; every other field stays byte-for-byte what it already was
   (in particular, an already-km-normalized distance the user isn't changing must not be touched).
4. Run `python scripts/validate_profile.py state/runner-profile.yaml --raw-fields <field(s)>`, where
   `<field(s)>` is a comma-separated list containing only whichever of `typical_weekly_distance_km` /
   `longest_recent_run_km` were just freshly restated this call (empty string if neither was touched, e.g.
   `--raw-fields ""`). This tells the script which values are raw-in-the-stated-units versus already
   km-normalized — never omit this flag here, since omitting it defaults to "convert both," which is only
   correct for a fresh onboarding draft.
   - Exit 1 / Exit 2: same handling as onboarding step 4.
   - Exit 0: continue.
5. For each field actually changed, append one line to `state/corrections.jsonl`:
   `{"id": "corr-N", "recorded_at": <now, ISO>, "target": "runner_profile", "field": "<field name>", "old_value": <prior value>, "new_value": <new value>, "source": "user"}`
   (`N` = current line count of the file + 1, incrementing per line within this same amendment if more than one
   field changed.)
6. Confirm the updated profile back to the user in plain language.

## 7. Journey: Create first plan

1. Read the validated `state/runner-profile.yaml`.
2. Compute the weeks between today and `marathon_date` (`W`). **Feasibility check:** if `W < 8`, say so
   plainly — a sensible phased split isn't possible in that time — and ask whether they want to proceed with a
   compressed plan anyway or adjust the date. Don't silently produce a phased plan that doesn't make sense for
   the time available. Everything below assumes `W >= 8`; for a compressed plan, collapse consistency and
   reduced-load weeks first and keep the taper and progression cap non-negotiable.
3. Load [references/coaching-principles.md](references/coaching-principles.md),
   [references/session-types.md](references/session-types.md),
   [references/mobility-guidance.md](references/mobility-guidance.md), and
   [references/strength-guidance.md](references/strength-guidance.md).
4. **Phase structure (FR-005).** Working backward from race week, apply
   [references/plan-generation-rules.md](references/plan-generation-rules.md) — load it here, before drafting
   any week. It covers the taper / marathon-specific-prep / build-block breakdown (including the consistency
   sub-phase, reduced-load weeks, and easy-day progression), where `review_point: true` gets set, and the Rest
   & Recovery Scheduling hard constraint every week must satisfy regardless of phase.
5. For each week, write:
   - `week_number`, `phase`, `start_date` (the Monday of that week), `purpose` (one sentence), `review_point`
     (bool, per step 4).
   - **Run sessions** (`category: run`): `subtype: easy` or `subtype: long` at authoring time (full
     `session-types.md` variety is introduced closer to each week by "This week's plan," not written months in
     advance here — see that journey). Every session needs `id` (`w{week_number}-{day}`), `day`, `category`,
     `subtype`, `purpose`, `planned_distance_km` or `planned_duration_minutes`, `effort_guidance`, `priority`,
     `status: planned`, `linked_garmin_activity_id: null`, plus four FR-006 presentation fields left `null` for
     now and populated later: `warm_up_guidance`, `cooldown_or_mobility_guidance`, `completion_criterion`,
     `caution_or_modification`.
   - **Mobility sessions** (`category: mobility`, FR-011, real integration): two per week from
     `mobility-guidance.md` — one `subtype: post_run` on the priority long-run day (area rotation weighted
     toward ankles/calves/hips per that guidance's volume rule), one `subtype: standalone` on a non-running day
     (can cover thoracic/general work, adapted to `mobility_preferences`). `id`:
     `w{week_number}-{day}-mobility`. Same required fields as a run session, using `planned_duration_minutes`
     (5-10 for post-run, 10-15 for standalone) — never framed as injury treatment.
   - **Strength sessions** (`category: strength`, FR-012, real integration): count = phase-adjusted
     `strength.preferred_sessions_per_week` (default 2) — base/consistency/build: up to 2; marathon-specific: 1
     (maintenance only); taper: 1 short maintenance session in the first taper week, 0 in race week. Pick the
     equipment tier from `strength-guidance.md` matching `strength.equipment` (bodyweight-only if empty/none,
     minimal-equipment for dumbbells/bands, full-gym if it mentions a gym/barbell), and never place a session
     immediately before or after the priority long-run day. `id`: `w{week_number}-{day}-strength`. Same required
     fields, `purpose` names the pattern selection, `effort_guidance` states the set/rep range and an explicit
     effort limit (e.g., "stop 2-3 reps short of failure").
   - Drop the old `mobility_placeholder`/`strength_placeholder` single-line fields entirely — the sessions above
     replace them.
6. Write the draft to a temp file and run:
   `python scripts/version_plan.py --new-plan <draft.yaml> --plans-dir state/plans/`
   - Exit 1: fix whatever structural issue it reports (missing weeks/sessions/fields) and retry — don't ask the
     user about this, it's an internal construction error, not a data problem.
   - Exit 0: the plan is written. Continue to step 7.
7. Append one line to `state/coaching-decisions.jsonl`:
   `{"id": "cd-N", "recorded_at": <now, ISO>, "plan_version_before": null, "plan_version_after": <version from step 6's output>, "change_summary": "Initial plan created", "garmin_evidence": [...], "user_evidence": [<profile fields actually used, including strength/mobility fields and which equipment tier was chosen>], "plan_evidence": [], "rationale": <phase structure and mobility/strength choices, citing the coaching-principles.md/mobility-guidance.md/strength-guidance.md rules applied>, "uncertainty": <as in Milestone 2, else null>}`
   (`N` = current line count of the file + 1.) Cite what was *actually* used, not a generic boilerplate sentence.
8. Present week 1 to the user, and state plainly that this is a starting structure expected to flex as training
   actually goes — not every future session is assumed to happen exactly as written (FR-005).

## 8. Journey: This week's plan (Weekly Plan Generation)

A fresh, detailed look at one specific week (FR-006) — the current week by default, or one the user names.
Distinct from "Create first plan," which only ever writes the broad multi-week skeleton: this journey layers in
evidence that's only known close to the week in question, and is where `session-types.md`'s full variety
finally gets used for real.

1. Identify the target week from the active plan version.
2. Gather context: that week's stored sessions; the last ~2 weeks of `state/session-log.jsonl` outcomes
   (consistency, any missed/modified sessions); the last ~3 check-ins (soreness, energy, motivation, pain);
   Garmin recovery signals if available; and, if `state/weekly-reviews.jsonl` has an entry for the immediately
   preceding week, its `interpretation.proposed_changes_next_week` (FR-015's "review informs the next weekly
   plan"). Apply **section 2 (Evidence Conflict Resolution)** wherever Garmin and subjective evidence might
   disagree.
3. **Session-type substitution, where phase-appropriate.** In `aerobic_volume`/`marathon_specific` weeks (never
   `consistency` or `taper`), one of the week's `easy` runs may become `steady`, `run-walk`,
   `technique_strides`, or `controlled_quality` per [references/session-types.md](references/session-types.md),
   if recent evidence supports it (no recent concerning symptoms, consistency reasonably solid). Rules, in
   order:
   - Never place a hard session (`long`, `steady`, `controlled_quality` — not `technique_strides`, which
     `session-types.md` itself describes as low-fatigue-cost) on a day adjacent to another hard session,
     including the priority long-run day.
   - Never substitute in a reduced-load week or anywhere in the taper.
   - This changes stored plan content, so it's a real plan change: draft the week with the substitution, run
     `python scripts/version_plan.py --new-plan <draft.yaml> --plans-dir state/plans/` (same exit-code handling
     as "Create first plan" step 6), then append one line to `state/coaching-decisions.jsonl` (same shape as
     "Create first plan" step 7) naming the substitution and why this week specifically warranted it. If nothing
     about this week justifies a substitution, don't force one — most weeks may stay `easy`/`long`.
4. **Enrich every session for presentation** — running, mobility, strength, and rest together, not scattered
   across separate answers (FR-006's own acceptance criterion):
   - `warm_up_guidance`: RAMP-based, scaled to the session (full RAMP before `steady`/`controlled_quality`/
     `long`; an abbreviated raise-plus-mobility version for `easy`/`recovery`), per
     `coaching-principles.md`/`mobility-guidance.md`.
   - `cooldown_or_mobility_guidance`: cross-reference that week's paired mobility session, or state cooldown is
     optional comfort per `mobility-guidance.md`.
   - `completion_criterion`: one concrete sentence (e.g., "complete the stated distance at conversational
     effort — walk breaks don't count against completion" for `easy`/`long`; a stated set/rep target for
     strength).
   - `caution_or_modification`: only when the gathered context actually warrants one (e.g., "given last week's
     reported calf tightness, keep this at the easy end and stop if it recurs") — `null` otherwise, never
     invented for its own sake.
   These four fields are populated for presentation immediately; only persist them back into the stored plan
   file if step 3 already required a new version anyway (don't version-bump the plan just to write text fields).
5. **Lower-load week, on request:** cut non-priority (non-long-run) distances ~20-30%, drop one strength
   session, and protect the priority long run unless the user specifically wants it reduced too. Present it
   first. Only run it through `version_plan.py`/`coaching-decisions.jsonl` (same as step 3) if the user confirms
   they want it kept — a passing "what would an easier week look like" question shouldn't spawn a plan version.
6. **Explain any material departure from the broader plan** — step 3's substitution or step 5's load reduction,
   plainly, as part of presenting the week (FR-006's acceptance criterion). Presentation-only enrichment (step
   4) isn't a departure and doesn't need this framing.

## 9. Journey: Post-run check-in

1. When the user reports a run, or a new Garmin activity appears, normalize it per section 4's contract
   (including the correction override) and write it to a small JSON file.
2. Run:
   `python scripts/reconcile_activities.py --plan state/plans/plan-v{n}.yaml --activities <normalized.json> --session-log state/session-log.jsonl --check-ins state/check-ins.jsonl`,
   where `plan-v{n}.yaml` is the currently *active* plan file (section 3) — never hardcode `plan-v1.yaml`.
3. For each result where `duplicate` is false and `is_running` is true, ask the full FR-008 set together (still
   one concise message, not seven separate turns):
   - Overall perceived effort: very easy, easy, moderate, hard, or very hard.
   - How the run felt overall, in their own words.
   - Energy level during the run.
   - Any muscle soreness or discomfort.
   - Any unusual breathing, dizziness, pain, or other concerning symptom.
   - Confidence or enjoyment (optional — only ask if it seems useful, e.g. first few weeks or after a rough
     patch).
   - Anything else they want to add (free text).
   - The user can skip the whole check-in. If they do, record it with every content field `null` and
     `skipped: true` — don't just drop it. They can also decline individual questions without skipping the
     whole thing; record those specific fields as `null` while keeping `skipped: false`.
   - If they report a concerning symptom, apply [references/safety-rules.md](references/safety-rules.md) before
     anything else — this takes priority over asking the remaining questions.
4. Append one line to `state/check-ins.jsonl`, using `docs/requirements.md` section 7.1's field names:
   `{"id": "ci-N", "type": "post_run", "session_id": <matched_session_id or null>, "garmin_activity_id": "...", "recorded_at": <now, ISO>, "perceived_effort": <enum or null>, "overall_feeling": <text or null>, "energy": <text or null>, "soreness_or_discomfort": <text or null>, "concerning_symptoms_reported": <bool or null>, "confidence_or_enjoyment": <text or null>, "free_text": <text or null>, "skipped": <bool>, "source": "user"}`
   (`N` = current line count of the file + 1.) A reported concerning symptom's description goes in `free_text`
   — the SRS doesn't define a separate detail field, so don't invent one. The one check-in recorded before this
   schema existed, `ci-1`, uses the old `pain_or_discomfort_reported`/`pain_or_discomfort_detail` shorthand and
   no `type` — it's legacy, left as-is, not rewritten.
5. If `matched_session_id` is set, append one line to `state/session-log.jsonl`:
   `{"id": "sl-N", "session_id": "<matched_session_id>", "plan_version": <current plan's version field>, "event": "completed", "garmin_activity_id": "...", "distance_km": <from the normalized activity>, "duration_minutes": <from the normalized activity>, "recorded_at": <now, ISO>, "source": "user"}`
   (`N` = current line count of `session-log.jsonl` + 1.) The active plan file itself is never edited here — it stays
   exactly as authored; `session-log.jsonl` is the record of what actually happened against it (see section 3).
6. Recovery advisory: look at this check-in together with the last 2-3 in `state/check-ins.jsonl` (not just this
   one) for a repeating pattern — matching `coaching-principles.md`'s "look for a cluster of signals together
   over days, never act on one bad session alone" rule. Apply **section 2 (Evidence Conflict Resolution)** —
   pull in whatever Garmin recovery signals are available for context, not just the check-in text.
   - Below **section 12 (Adaptive Replanning)**'s trigger thresholds: stay advisory, exactly as before — one
     concrete, conversational recovery recommendation for the next session (e.g. "given how demanding that felt,
     treat your next run as recovery-paced rather than easy"), no plan version, no `coaching-decisions.jsonl`
     record.
   - At or above a threshold (a missed/shortened priority session, a concerning symptom, an effort-mismatch
     pattern, etc. — section 12's list): invoke **Adaptive Replanning** instead of just advising.

## 10. Journey: Weekly wellbeing check-in

At least once per planning week (the user has to ask for this — there's no scheduled trigger yet), gather a
broader wellbeing check-in distinct from a single run's post-run check-in.

1. Ask, allowing structured answers plus free text, and allowing skip same as post-run check-ins: general
   energy, motivation, stress, overall soreness, perceived sleep, confidence about the next week's training, and
   anything else the user thinks is relevant.
2. Determine `week_start` (the Monday of the current week).
3. Append one line to `state/check-ins.jsonl`:
   `{"id": "ci-N", "type": "weekly", "week_start": "YYYY-MM-DD", "energy": <value or null>, "motivation": <value or null>, "stress": <value or null>, "soreness": <value or null>, "perceived_sleep": <value or null>, "confidence": <value or null>, "free_text": <text or null>, "skipped": <bool>, "recorded_at": <now, ISO>, "source": "user"}`
   (`N` = current line count of the file + 1.)
4. If the answers show low energy, high soreness, or other concerning feedback, apply **section 2 (Evidence
   Conflict Resolution)** and the recovery-advisory handling from Post-run check-in step 6 — advisory below
   **section 12 (Adaptive Replanning)**'s thresholds, invoking that journey at or above one (and the same
   safety-rules escalation if anything crosses that bar regardless).
5. Whenever any journey discusses a given week and no weekly check-in exists for its `week_start`, say so
   plainly (e.g. "no wellbeing check-in on file for this week") rather than assuming things are fine.

## 11. Journey: Manual data entry & correction

FR-018's six bullets, and where each one actually lives — most are pointers to journeys already built elsewhere
in this file, not new mechanisms:

1. **Add an unrecorded run** → the manual-run-entry convention in section 4 (synthetic `manual-<slug>` ID),
   flowing through Post-run check-in exactly like a real Garmin activity.
2. **Add post-run feedback later** → Post-run check-in, invoked retroactively for a run that didn't get a
   check-in at the time. Same journey, no separate mechanism.
3. **Correct their profile** → the Amend profile journey.
4. **Mark a session completed, modified, skipped, or missed** (no Garmin activity involved — e.g. "mark
   Wednesday as skipped, I was sick"): append one line directly to `state/session-log.jsonl`:
   `{"id": "sl-N", "session_id": "<id>", "plan_version": <current plan's version field>, "event": "<completed|modified|skipped|missed>", "garmin_activity_id": null, "distance_km": <if the user states one, else null>, "duration_minutes": <same>, "recorded_at": <now, ISO>, "source": "user"}`.
   This alone is the audit trail (append-only, sourced) — it does not also get a `corrections.jsonl` entry,
   which would just duplicate the same event.
5. **Correct incorrectly classified information** (e.g. "that Tuesday activity was actually a run, not a walk"):
   append one line to `state/corrections.jsonl`:
   `{"id": "corr-N", "recorded_at": <now, ISO>, "target": "activity_classification", "garmin_activity_id": "...", "field": "activity_type", "old_value": "...", "new_value": "...", "source": "user"}`.
   This is what section 4's correction-override rule reads — the reclassification takes effect the next time
   that activity is normalized (including immediately, if reconciling right now).
6. **Override a proposed plan** (e.g. "I want Wednesday to be 5k, not 3k"): this is the one correction that
   touches the plan itself, so it goes through the same versioning machinery as any other plan change —
   "what was planned" can't legitimately change any other way (section 3).
   - If the requested change conflicts with a hard rule (e.g. the long-run progression cap, taper constraints),
     say so plainly per SR-006 before proceeding — never comply silently just because the user asked.
   - Draft a copy of the active plan with only the requested session field(s) changed, and run
     `python scripts/version_plan.py --new-plan <draft.yaml> --plans-dir state/plans/` (same as "Create first
     plan" step 6's exit-code handling).
   - Append one line to `state/corrections.jsonl`: `{"id": "corr-N", "recorded_at": <now, ISO>, "target": "plan", "field": "<session_id>.<field>", "old_value": ..., "new_value": ..., "source": "user"}`.
   - Append one line to `state/coaching-decisions.jsonl` (same shape as "Create first plan" step 7):
     `change_summary` names it a user override (e.g. "User override: w2-wed distance 3km -> 5km"),
     `user_evidence` cites the request itself, `plan_evidence` cites the prior plan version/session,
     `rationale` notes this was user-initiated rather than evidence-driven, `uncertainty` states any caution
     given above.

All corrections in this journey use the current line count of `state/corrections.jsonl` + 1 for `N`, same
convention as every other append-only file here.

## 12. Journey: Adaptive Replanning

The FR-014 capability that actually changes the plan in response to evidence, rather than just recommending —
invoked from Post-run check-in (section 9) and Weekly wellbeing check-in (section 10) when a trigger below is
met, or directly for the two lightweight intakes it owns (unavailability, unplanned exercise). Bounded scope
(don't overreach): touches only the current week's remaining sessions, plus rebasing the *next* week's long-run
distance if the long run itself was affected — never a silent rewrite of the whole remaining plan. A severe or
prolonged disruption (pain persisting past `safety-rules.md`'s own "persistent" threshold, or a multi-week gap)
gets flagged for a full plan conversation/regeneration instead of an automated multi-week rewrite.

### Triggers and allowed actions

The concrete trigger list (not "use judgment"), the least-disruptive-first action set, and the hard constraints
that apply to every action are [references/replanning-rules.md](references/replanning-rules.md) — load it
before evaluating whether a disruption meets a trigger threshold, and again before choosing an action in step 2
below.

### Process

1. Confirm which trigger fired and gather the same evidence context as Evidence Conflict Resolution (section 2).
2. Choose the least disruptive action satisfying references/replanning-rules.md's hard constraints. If the long
   run itself was affected (missed, badly shortened, or removed), rebase *next* week's long-run distance from
   the last *actually completed* long run — the same "resume from last non-reduced week" pattern already used in
   `references/plan-generation-rules.md`'s reduced-load-week handling (loaded by "Create first plan" step 4). If
   no long run has been completed yet at all
   (e.g. the very first one was missed), repeat that same planned-but-unmet distance next week rather than
   advancing to the following progression step — there's no completed baseline yet to grow from, and treating
   an unmet target as if it had been hit would be exactly the "recover all missed distance" the no-catch-up
   rule forbids. Don't touch weeks beyond the one immediately following the disruption.
3. If the disruption looks severe or prolonged (see above), stop here and recommend a fuller conversation
   (regenerate the plan, or discuss the marathon date/goal) instead of acting automatically.
4. Draft the change, run `python scripts/version_plan.py --new-plan <draft.yaml> --plans-dir state/plans/` (same
   exit-code handling as "Create first plan" step 6).
5. Append one line to `state/coaching-decisions.jsonl`: `change_summary` names the specific change,
   `garmin_evidence`/`user_evidence`/`plan_evidence` tag each fact by source, `rationale` names which trigger
   rule fired, `uncertainty` states anything unresolved.
6. Explain to the user what changed and why, distinguishing evidence sources (section 2) — never silent.

## 13. Journey: Weekly review

FR-015's structured look back at a completed week, kept as four distinguishable sections — never invents a
reason for a missing session, never buries concerning feedback in a general summary.

1. Identify the target week: the most recently completed week (its `start_date + 6` is before today) with no
   existing `state/weekly-reviews.jsonl` entry, or one the user names.
2. Run:
   `python scripts/compile_weekly_summary.py --plan state/plans/plan-v{n}.yaml --session-log state/session-log.jsonl --check-ins state/check-ins.jsonl --week-start <that week's start_date>`
3. **Planned versus completed** — straight from the `week` object above: planned/completed/modified/missed/
   skipped per category, total run distance/duration, long-run completion.
4. **Objective observations** — opportunistically fetch that week's Garmin trends (section 4), applying
   **section 2 (Evidence Conflict Resolution)** if they disagree with subjective evidence; explicitly name any
   Garmin data that's missing for the week rather than skipping over it.
5. **Subjective observations** — summarize that week's post-run check-ins and weekly wellbeing check-in (if
   any); note recurring soreness/discomfort/fatigue/confidence themes across them. If a session has no
   check-in and no session-log reason recorded, say so plainly — don't guess why it happened.
6. **Coaching interpretation** — what supported progress, what needs attention, proposed changes for next week
   (this is what "This week's plan" step 2 reads for the following week), and this review's own confidence and
   limitations. If step 3-5 surfaced a concerning-symptom report, name it here prominently, not folded into a
   general summary — cross-reference **Adaptive Replanning** if it hasn't already acted on it.
7. Append one line to `state/weekly-reviews.jsonl`:
   `{"id": "wr-N", "week_start": "...", "recorded_at": <now, ISO>, "planned_vs_completed": {...step 3...}, "objective": {"garmin_trends": [...], "missing_garmin_data": [...]}, "subjective": {"post_run_summary": "...", "weekly_checkin_summary": "...", "recurring_themes": [...]}, "interpretation": {"what_helped": "...", "needs_attention": "...", "proposed_changes_next_week": "...", "confidence_and_limitations": "..."}, "source": "agent"}`
   (`N` = current line count of the file + 1.)
8. Present the four sections to the user, kept visibly separate (FR-015's own acceptance criterion) — never
   blend an objective fact with the coaching interpretation built on top of it.

## 14. Journey: Completion-readiness assessment

Read-only synthesis (FR-016) — never writes a new plan version or a `coaching-decisions.jsonl` record; this
only reads existing state.

1. Run:
   `python scripts/compile_weekly_summary.py --plan state/plans/plan-v{n}.yaml --session-log state/session-log.jsonl --check-ins state/check-ins.jsonl --as-of <today>`
2. Gather additional context:
   - The last 4-6 check-ins for effort/pain/soreness patterns, and whether any concerning-symptom report is
     still unresolved (reported in the most recent relevant check-in with no later check-in indicating it
     improved).
   - Weeks remaining until `marathon_date`.
   - Opportunistically fetch Garmin recovery metrics (section 4) for the last week or two if connected, applying
     **section 2 (Evidence Conflict Resolution)** if they disagree with subjective signals.
3. Categorize using these qualitative rules — no fixed numeric weighting (consistent with FR-010's stance),
   applied in order, first match wins:
   - **Insufficient evidence to assess:** fewer than ~2 weeks have elapsed since the plan started, or fewer than
     2 check-ins exist total.
   - **Preparation disrupted or currently uncertain:** an unresolved concerning-symptom report, OR 2+
     missed/skipped run sessions in the last 2 weeks, OR the plan-to-date `consistency_ratio` is below ~0.5.
   - **On track for completion:** `consistency_ratio` is high (~0.8+), `long_run_progression` shows steady
     growth within the progression cap with no unexplained drop, and no open concerns.
   - **Progressing, with areas to address:** everything else.
4. Present: the category label; the evidence behind it, sourced (which came from `compile_weekly_summary.py`'s
   tallies, which from check-ins, which from Garmin if used); explicit limitations (e.g., "Garmin recovery data
   is largely unavailable for this account, so this leans on your self-reported check-ins"); and 2-3 concrete
   next priorities. Never state or imply a guarantee of completion or injury-free training (SR-005); never
   require or invent a target finish time.

## 15. Explicitly out of scope for now

All 20 Must-have features are built as of Milestone 6, each at whatever depth its own acceptance criteria
needed — this list is now purely the Should/Could-have items from
[docs/features.md](../../../docs/features.md) that were never in scope for the Must-have milestones, plus
anything with no producing journey at all:

**Should-have:** Data Status View, Plan Version Comparison, Natural-Language Commands (beyond what's already
completable conversationally — no slash-command surface exists), Low-Impact Cross-Training Alternatives
(`session-types.md`'s `cross_training` category exists but isn't scheduled by any generator), Exportable
Weekly Summary. **Could-have:** structured workouts written back to Garmin, charts/trend visualisations,
voice-based check-ins, a race-day checklist, shoe/equipment tracking — none of these extend or change anything
built so far (`docs/technical-specification.md` section 6).

Below Adaptive Replanning's thresholds (section 12), a check-in signal or a routine week's presentation
enrichment still doesn't change the plan or write a `coaching-decisions.jsonl` record on its own — only
section 12 itself, "This week's plan" step 3/5, and section 11's explicit user-initiated override ever do
that.
