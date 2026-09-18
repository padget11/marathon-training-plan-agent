# Strength Training Guidance (FR-012)

Operationalizes [coaching-principles.md](coaching-principles.md)'s existing "Strength training" section (the
evidence lives there — 2–8% running-economy improvement from heavy/plyometric work, general injury-reduction
evidence transferring from other sports by inference, not runner-specific proof) into concrete session
templates. This file adds no new evidence claims of its own.

Not yet wired into plan generation — see the skill's out-of-scope note. This is the reference library Initial
Marathon Plan Generation will draw from once that hardening happens.

## Hard rules

- Never becomes a hypertrophy or maximal-strength program — the goal is running durability and economy, not
  building muscle or maxing a lift.
- Begin conservatively for anyone new to strength training: bodyweight or light-load patterns first, add
  external load only after 2-3 weeks of clean bodyweight execution.
- Typically 1-2 sessions/week where recovery and running load allow (2-3 is the upper end per the evidence, and
  only for someone already experienced).
- Reduce session volume (fewer sets, lighter effort) whenever running load or fatigue is high; never add a
  strength session on top of an already-demanding week without easing something else.
- Never schedule a demanding lower-body strength session immediately before the priority long run — leave at
  least one easy or rest day of separation.
- Missed strength work is never automatically rescheduled next to a long or hard run just to "make it up."
- Maintenance-only during peak marathon-specific preparation and the taper: hold the same movement patterns at
  reduced volume/effort purely to keep the adaptation, not to build further.

## Pattern rotation (FR-012's required patterns)

Every template rotates through: squat/sit-to-stand, hinge, split-stance/lunge, calf work, single-leg stability,
trunk stability, and an upper-body movement for balanced general strength (not race-relevant, but keeps the
session general-preparedness rather than leg-only).

## Templates by equipment level

Pull `strength.equipment` from the runner profile to pick a tier; `strength.experience` decides where in the
tier to start (a beginner starts at the lowest listed reps/hardest-regression version).

### Bodyweight-only (no equipment, or equipment: [])
- Squat pattern: bodyweight squat or sit-to-stand from a chair, 2-3 sets of 8-12.
- Hinge pattern: single-leg Romanian deadlift (bodyweight) or glute bridge, 2-3 sets of 8-12 per side/rep.
- Lunge pattern: forward or reverse lunge, 2 sets of 8-10 per leg.
- Calf: standing calf raise, 2-3 sets of 12-15.
- Single-leg stability: single-leg balance reach or single-leg stand, 2 sets of 20-30 seconds per side.
- Trunk: front plank or side plank, 2-3 sets of 20-40 seconds.
- Upper body: push-up (or incline push-up) and a bodyweight row if a sturdy edge/table is available, 2 sets of
  6-12.

### Minimal equipment (dumbbells / resistance bands / kettlebell)
- Squat pattern: goblet squat, 3 sets of 6-10.
- Hinge pattern: dumbbell/kettlebell Romanian deadlift or hip thrust, 3 sets of 6-10.
- Lunge pattern: dumbbell reverse lunge or split squat, 2-3 sets of 6-10 per leg.
- Calf: single-leg calf raise, loaded if easy at bodyweight, 2-3 sets of 10-15 per side.
- Single-leg stability: single-leg Romanian deadlift with light load, 2 sets of 6-8 per side.
- Trunk: loaded carry (suitcase or farmer's carry) or plank variation, 2-3 sets.
- Upper body: dumbbell row and push-up or dumbbell press, 2-3 sets of 6-12.

### Full gym access
- Squat pattern: back or front squat, 3 sets of 4-6 (low-rep per the evidence).
- Hinge pattern: trap-bar or conventional deadlift, or barbell hip thrust, 3 sets of 4-6.
- Lunge/split-stance: barbell or dumbbell split squat, 2-3 sets of 6-8 per leg.
- Calf: standing or seated calf raise machine, loaded, 2-3 sets of 10-15.
- Single-leg stability: single-leg press or single-leg RDL, 2-3 sets of 6-8 per side.
- Trunk: weighted plank, cable anti-rotation, or hanging leg raise, 2-3 sets.
- Upper body: any balanced push/pull pair (bench or overhead press with a row or pulldown), 2-3 sets of 6-10.
- Optional plyometric add-on (only once squat/hinge patterns are established, and never in the taper): low-
  volume box step-offs, pogo hops, or bounding drills, 2-3 sets of 4-6 — small volume, this is neuromuscular
  stimulus, not conditioning.

## Phase-based adaptation

- **Base phase:** 1-2 sessions/week, bodyweight or light load, building toward clean technique before adding
  more load or volume.
- **Build phase:** up to 2 (occasionally 3, only if recovery is clearly good) sessions/week, can progress load
  or add the plyometric add-on if applicable; still reduce on weeks with a demanding long run or when the
  running check-ins show high fatigue/soreness.
- **Marathon-specific / peak prep:** shift to maintenance — same patterns, hold or slightly reduce load/volume,
  don't chase progression here.
- **Taper:** reduce to 0-1 short maintenance sessions, light load only, nothing that leaves noticeable soreness;
  remove entirely in the final week.

## Session shape

Every strength session written into a plan should read as: purpose ("supporting running durability, not a
separate strength program"), the pattern selection for that session (drawn from the templates above matched to
profile equipment/experience), a set/rep or duration range, and an explicit effort limit (e.g., "stop 2-3 reps
short of failure on every set" — never train to failure).
