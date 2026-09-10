# Coaching Principles — Evidence Base

This file gives the coaching skill a set of evidence-backed rules to draw on when writing or adjusting a
plan (initial plan generation, weekly plans, replanning, weekly review, readiness assessment). Each rule below
is paired with the finding behind it and the [feature](../features.md) it's most relevant to, so a rule can be
traced back to its evidence and updated if the evidence changes.

This is a starting synthesis, not a finished, expert-validated ruleset — see **Status and caveats** below
before treating anything here as final.

## Source and scope

Synthesized from [running-knowledge-base](https://github.com/jacquescorbytuech/running-knowledge-base)
(MIT licensed), a community-maintained, evidence-graded wiki on distance running. Every page there carries an
`evidence:` grade (`strong` / `moderate` / `limited` / `weak` / `contested`); **only pages graded `strong` or
`moderate` are represented here** — pages graded `limited`, `weak`, or `contested` were reviewed and excluded
(listed at the bottom, for transparency). That source in turn cites the underlying peer-reviewed literature
(meta-analyses, RCTs, cohort studies); author/year citations below point into its `sources/` directory, which
has the full reference for each.

Deliberately excluded regardless of grade, per this app's scope:
- Nutrition/fuelling/supplement content (out of scope — see [features.md](../features.md) "Won't Have").
- Per-injury diagnosis, rehab, or treatment protocols (out of scope — SR-003 prohibits prescribing rehab). Only
  general overuse-pattern recognition and when-to-refer-out guidance is included.
- Gear reviews, coach biographies, and non-marathon race distances.

## Status and caveats

- This is informational grounding for the coaching skill's rules, not a substitute for review by someone with
  actual exercise-science or coaching credentials — see Open Design Decision #8 in
  [requirements.md](../requirements.md). Treat it as a first draft to be checked, not a finished spec.
  - Anyone reviewing or publishing content derived from this file for external/client use should validate it
    before sharing — this note itself is a reminder, not a substitute for that review.
- Every rule here is a population-level average; [individual variation](#plan-philosophy--prioritisation) is
  itself one of the strong-evidence findings, so the coaching skill should treat every threshold below as a
  starting point to adjust against a specific user's actual response (SR-004: prefer the conservative reading
  when in doubt).
- This is not medical advice (SR-001) and nothing here should be used to diagnose or treat an injury.

---

## Plan philosophy & prioritisation

**Evidence:** The largest share of a beginner-to-intermediate runner's improvement comes from consistency, easy
volume, sleep, and fuelling, in that order — gear, supplements, taper and strength work are real but marginal
gains on top. Identical training programs produce widely different individual outcomes (one classic study saw
20 weeks of the same program change VO2max from about −5% to +48% across participants), so published averages
are a hypothesis to test on a given user, not a guarantee. *(strong; the-basics, individual-variation)*

**Rules for the coach:**
- Default effort to consistency and easy volume over any other lever before optimizing anything marginal.
- Present plan targets as a starting point to adjust, not a promise — never over-commit to a specific outcome.
- Prefer process goals ("three runs this week") over outcome goals ("sub-4:00 marathon") when framing weekly
  priorities to the user; both process goals and implementation-intention prompts ("if it's Tuesday 6pm, I run")
  have solid adherence evidence, while gamification/rewards have small, fading effects. *(moderate;
  motivation-and-adherence)*
- A missed session is normal, not a failure signal — frame it that way in messaging, not as a lapse to feel
  guilty about.

**Informs:** Initial Marathon Plan Generation, Weekly Plan Generation, agent tone/interaction style.

---

## Progression and long-run distance

**Evidence:** Connective tissue (tendon, ligament, bone) takes 3–6 months to meaningfully strengthen, far slower
than cardiovascular fitness (days–weeks) — this mismatch, feeling cardiovascularly ready before tissue is ready,
is the core reason gradual progression matters, and why beginners/returning runners are most injury-prone.
*(strong; physiological-adaptations)*. The traditional "10% per week" rule is a rough guardrail, not a validated
law; the stronger, more actionable signal is that a *single* run more than 10% longer than the runner's longest
run in the past 30 days measurably raises overuse-injury risk, climbing sharply (roughly 2.3x) for a session more
than double that recent long run. *(moderate; training-load-management, running-injuries)*

**Rules for the coach:**
- Never schedule a single long run more than ~10% beyond the runner's longest run in the last 30 days — this
  caps a single session, not just a weekly total.
- Treat "10% per week" as a loose guardrail, not a hard formula; judge actual progression by how the runner is
  absorbing load (recent check-ins, soreness trend), not a fixed percentage.
- Apply this same conservative logic after any gap (illness, missed week) — resume below the pre-gap long-run
  distance rather than picking up where the plan left off (this is also why FR-014 forbids catch-up mileage).

**Informs:** Baseline Assessment, Initial Marathon Plan Generation, Weekly Plan Generation, Adaptive Replanning.

---

## Tapering

**Evidence:** A well-executed ~2-week taper — cutting volume roughly 40–60% progressively while holding both
intensity and running frequency — produces a measured ~2–3% performance gain, one of the best-quantified
practices in endurance training. Duration (~2 weeks) matters most among the taper variables studied. The two
common mistakes are cutting too little (fatigue never clears) and cutting intensity along with volume (fitness
slips just as it should surface). *(strong; tapering)*

**Rules for the coach:**
- In the final ~2 weeks before the marathon, reduce volume by ~40–60% progressively while keeping intensity and
  run frequency close to normal.
- Never add a hard "confidence" session in the taper window — it only adds fatigue.
- Warn against cutting too little volume just as much as cutting too much.

**Informs:** Initial Marathon Plan Generation (taper phase), Weekly Plan Generation.

---

## Strength training

**Evidence:** Heavy resistance and plyometric training improves running economy by roughly 2–8% through
neuromuscular changes, without adding race weight or harming VO2max — it supplements running volume rather than
replacing it. A practical, evidence-supported prescription is 2–3 sessions/week for 8–12 weeks, using low-rep
(3–6) compound lower-body lifts (squat, deadlift, split-squat/lunge, hip thrust, calf raises) plus some
plyometric work, built up gradually. General injury-reduction evidence for strength training is strong, though
the one meta-analysis specific to endurance runners found no significant injury reduction outside supervised
settings — so the injury case transfers from general-sport evidence by inference, not a runner-specific
guarantee. *(strong; strength-training-for-runners)*

**Rules for the coach:**
- Default to 2–3 strength sessions/week, low-rep compound lower-body lifts, introduced gradually — frame it as
  supporting running economy and durability, not as a separate hypertrophy program (this matches FR-012 already).
- State the injury-prevention benefit honestly as inferred from general-sport evidence, not proven specifically
  in runners.

**Informs:** Strength Training Integration.

---

## Warm-up and effort guidance

**Evidence:** A RAMP warm-up (raise temperature, activate/mobilise key muscles/joints, potentiate with short
accelerations) reliably improves performance in subsequent quality/race efforts; a shorter warm-up suffices for
an easy run. *(moderate — the page mixes tiers: warm-up is well-supported, but its own cool-down section is
weak-graded — a post-run jog doesn't meaningfully reduce soreness, speed recovery, or prevent injury, though
it's harmless.)* Separately, age-based max-heart-rate formulas ("220 minus age") are unreliable — individual
measured max heart rates scatter ~9–10 bpm around even better formulas, enough to land a runner in the wrong
zone — and heart rate drifts upward over a long run at constant effort regardless of fitness. *(strong;
training-intensity-zones, heart-rate-and-effort-training)*

**Rules for the coach:**
- Prescribe a RAMP-style warm-up before quality sessions and races; keep it short for easy runs.
- Present cool-down as optional comfort ("do it if it feels good"), never as a recovery necessity.
- Use the talk test and perceived effort (RPE) as the primary effort guidance rather than a single heart-rate
  number or zone — this is already required by FR-001/FR-005 for users without a target pace, and the evidence
  here is why: heart-rate zones aren't precise or comparable across systems/devices.
- Don't read rising heart rate late in a long run as automatically concerning — cardiovascular drift at constant
  effort is a normal, expected pattern.

**Informs:** Running Session Type Library, Weekly Plan Generation, Evidence Conflict Resolution.

---

## Interpreting Garmin and wearable data

**Evidence:** Every watch-derived number is best read as a personal trend over time, not a precise absolute or a
basis for comparing between people — device error is often a stable offset, so relative change is more
trustworthy than the raw figure. Reliability varies sharply by metric: pace/distance (~3–6% error) and
steady-state heart rate (~5% error) are fairly trustworthy; estimated VO2max (~7–8% error), estimated threshold
pace (can overestimate 20%+), calories (~27% median error), and sleep staging are all weak and shouldn't be
treated as precise. Branded composite scores ("Training Readiness," "Body Battery," "Recovery Time") have little
independent validation of their absolute numbers — useful only as a personal trend line. *(strong;
gps-watches-and-metrics)* Separately, HRV is only meaningful as a 7-day rolling trend, never a single daily
reading, and a brief daily subjective check (sleep, fatigue, soreness, mood) is more sensitive to accumulating
load than most wearable readouts — act on a decline only when several signals move together over days, not from
one bad reading. *(moderate; training-monitoring)*

**Rules for the coach:**
- Frame every Garmin metric to the user as a trend, never a precise fact — especially VO2max, threshold pace,
  calories, sleep stages, and any branded readiness/recovery score.
- Never let a single Garmin reading (good or bad) override a subjective report — this directly grounds FR-010's
  "a positive Garmin metric doesn't override a pain report" rule and FR-003's "distinguish Garmin fact from
  interpretation."
- Treat HRV as a weekly trend only; don't react to one day's number.
- Weight the daily/post-run subjective check-in at least as heavily as any single Garmin metric when deciding
  whether to adjust load — look for multiple signals declining together before backing off.

**Informs:** Garmin Data Retrieval, Evidence Conflict Resolution, Data Status View, Post-Run Check-in, Weekly
Wellbeing Check-in.

---

## Pain and injury pattern recognition

*Pattern-recognition and referral guidance only — no diagnosis or rehab, per SR-003.*

**Evidence:** Roughly 40–50% of runners are injured in a given year, and over 70% of those injuries are overuse
(not sudden trauma), most commonly at or below the knee. The clearest identified trigger is a single run
notably longer than the runner's recent longest run — a stronger, more actionable signal than gradual weekly
mileage increases. Of everything marketed as injury prevention, only two levers have solid evidence: sensible
load progression (avoiding oversized single sessions) and strength training (2x/week); pre-run static
stretching, motion-control/pronation-matched shoes, and foam rolling have not been shown to reduce injury risk
in controlled trials. *(moderate; injury-prevention, running-injuries)*

**Rules for the coach:**
- Treat mild discomfort (roughly up to 3/10) that settles by the next morning and doesn't worsen session-to-
  session as a common, tolerable-load marker — not a reason to panic.
- Treat pain that rises during a run, lingers into the next day, or worsens session-over-session as a signal to
  reduce load immediately and recommend the user seek professional assessment — especially if it's sharp/
  localized, present at night, or hasn't improved after 2–3 weeks.
- Never diagnose a specific injury or suggest a treatment/rehab protocol — recognize the pattern, reduce load,
  and refer out. This is the concrete trigger logic behind SR-002/SR-003.
- Don't recommend stretching, foam rolling, or motion-control shoes as injury-prevention measures — the evidence
  doesn't support it; keep mobility guidance (FR-011) framed as preparation/recovery, not injury prevention.

**Informs:** Post-Run Check-in, Safety Guardrails, Evidence Conflict Resolution, Mobility Planning.

---

## Recovery, overtraining, and life load

**Evidence:** Excess training stress runs on a continuum from functional overreaching (a short, intended dip
that rebounds above baseline — the normal goal of a hard block) to non-functional overreaching (a weeks-to-
months decline with eventual but gainless recovery) to overtraining syndrome (months of impairment, a diagnosis
of exclusion). No single biomarker distinguishes these in real time — only a cluster of subjective signals does:
performance stalling despite hard training, persistently heavy legs, disturbed sleep, low mood, unusually high
effort at easy pace, and frequent minor illness. *(moderate; overtraining)* Psychological/life stress engages
the same physiological stress systems as hard training, measurably slowing recovery and raising injury/illness
risk — total load is training load *plus* life load. *(moderate; stress-and-life-load)* Fitness is lost faster
than gained (VO2max down ~4% after up to 30 days off, ~9% after longer), but a short break of a few days costs
very little and is easily regained; holding even reduced volume during an unavoidable busy/injured stretch
preserves substantially more fitness than stopping entirely. *(strong; detraining)*

**Rules for the coach:**
- Look for a cluster of declining signals together over days before concluding overreaching — never act on one
  bad session or one bad night's sleep alone.
- Treat a short intended dip after a hard week as normal and expected, not a problem to fix.
- Ask about and factor in life stress (deadlines, travel, poor sleep) the same way as training load — don't plan
  a hard block on top of a known high-stress week; ease training instead.
- Reassure the user that a short missed-session gap costs little fitness and doesn't need to be "made up" (this
  is also why FR-014 forbids catch-up mileage); for a longer unavoidable gap, prefer reduced volume over
  stopping entirely if any running is possible.

**Informs:** Weekly Wellbeing Check-in, Adaptive Replanning, Rest & Recovery Scheduling, Weekly Review Generation.

---

## Run-walk as a completion strategy

**Evidence:** Planned walk breaks taken from the start of a run (not only once fatigued) give recreational
(~4-hour) marathoners statistically similar finishing times to continuous running, with less self-reported
muscle soreness — though not reduced cardiac stress, and it slightly raises the energy cost of covering a given
distance. Claims that it prevents injury or meaningfully improves time beyond that aren't supported by
controlled evidence. *(moderate; run-walk-method)*

**Rules for the coach:**
- Present run-walk as a legitimate, evidence-backed completion strategy for first-time or slower marathoners —
  not a lesser fallback — matching FR-007's requirement to treat it as a valid strategy.
- Be honest that it's not faster and costs slightly more energy per distance, while noting the soreness benefit.

**Informs:** Running Session Type Library.

---

## Marathon-specific structure

**Evidence:** Marathon training carries the highest easy-volume base of any distance event, distributed
pyramidally (large easy base, a smaller amount of harder work on top). Goal pace should be anchored to the
individual's current fitness rather than a fixed formula, since a slower finisher runs the marathon at a much
lower relative intensity than a fast one. For race strategy, even or slightly negative splits beat "banking
time" early — early overshoot burns disproportionate glycogen and brings on the wall sooner; elite marathoners
vary pace by only ~3% across a race. *(This page has no formal evidence grade — it's a synthesis page whose
author notes the precise training balance is "coaching practice rather than trial-tested"; only its
better-supported, non-nutrition structural claims are included here.)*

**Rules for the coach:**
- Build the marathon-specific block toward a pyramidal volume distribution (mostly easy, some threshold, little
  hard) rather than a mix of intense session types.
- Individualize any pace guidance to the runner's current fitness rather than a fixed "marathon pace should feel
  like X" label.
- If race-day pacing guidance is ever added (currently out of scope — see features.md "Could Have"), default to
  even/slightly-negative splits over an aggressive start.

**Informs:** Initial Marathon Plan Generation (marathon-specific phase), Weekly Plan Generation.

---

## Excluded (evidence graded limited/weak/contested)

Reviewed and deliberately left out of the rules above — not strong/moderate enough to encode as a rule:

- The long run (dedicated page beyond what's captured under Progression/Marathon-specific above) — limited
- Periodisation (as its own model beyond base→marathon-specific→taper phasing already in FR-005) — limited
- Return to running (post-break ramp specifics beyond the general detraining findings above) — limited
- Practical niggles (blisters, chafing, black toenails, side stitch) — limited
- Deload and rest (in-training deload weeks, as distinct from tapering) — limited

---

## Sources

Author/year citations above trace into
[running-knowledge-base/sources/](https://github.com/jacquescorbytuech/running-knowledge-base/tree/main/sources),
which has the full reference for each. Selected anchors: Bosquet et al. 2007 (taper meta-analysis); Mujika 2010,
Mujika & Padilla 2000 (taper, detraining); Nielsen et al. 2014, Frandsen et al. 2025 (long-run jump size and
injury risk); Correia et al. 2024 (overuse injury review); Blagrove, Howatson & Hayes 2018, Llanos-Lagos et al.
2024 (strength training for runners); Tanaka et al. 2001 (max-HR formula error); Saw, Main & Gastin 2016 (subjective
monitoring vs. objective markers); Bouchard et al., HERITAGE Family Study (individual training-response
variation); Meeusen et al. 2013 (overtraining continuum); Stults-Kolehmainen & Bartholomew 2012 (life stress and
recovery); Hottenrott et al. 2016, Nolan & Moore 2021 (run-walk method); Coyle et al. 1984, Zheng et al. 2022
(detraining rates).
