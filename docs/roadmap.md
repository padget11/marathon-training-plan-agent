# Marathon Readiness Coach — Build Roadmap

This is a build order for the features in [features.md](features.md), derived directly from each feature's
`Depends on` line. It's a sequencing document, not a new source of scope — if a feature's dependencies or
priority change in `features.md`, this file should be re-derived from that, not edited independently.

## Recommended approach: a thin slice before full breadth

Strict dependency order (below) doesn't produce anything end-to-end runnable until Milestone 5 — everything
before that is plumbing with nothing to try against real data. The one truly unpredictable dependency in this
whole project is the Garmin MCP server (which implementation, which fields it actually returns — SRS Open
Design Decisions #1–2 are still unresolved). That's the thing most likely to surprise you, so it should be
proven first, not last.

**Recommendation: build Milestone 0 before working through Milestones 1–6 in full.** Milestone 0 is a minimal,
deliberately shallow cut through every layer — real Garmin connection, real profile, a plan simple enough to be
wrong in obvious ways — that turns into a working (if thin) product almost immediately. Milestones 1–6 then fill
in depth and correctness behind that already-working skeleton, rather than being the only thing that exists
until everything is done.

---

## Milestone 0 — Walking skeleton

A minimal, end-to-end path through the system: connect to Garmin, hold a profile, fetch real data, produce a
plan a human could actually follow (even a rough one), and record one check-in against it. Nothing here needs to
be complete — it needs to prove the integration and the data flow work.

- Minimal **Garmin Connection & Auth Handling** — connect, detect failure, nothing else yet.
- Minimal **Garmin Data Retrieval** — fetch a runner's recent activities; skip HRV/training-load/sleep for now.
- Minimal **Persistent State Model** — just enough schema to hold one profile and one plan file.
- Minimal **Runner Profile Management** — the required fields only, no editing flow yet.
- Minimal **Baseline Assessment** — whatever Garmin returns plus the profile, no gap-filling questions yet.
- Minimal **Initial Marathon Plan Generation** — a plausible phased plan; mobility/strength can be a single
  placeholder line per week rather than fully designed sessions.
- Minimal **Post-Run Check-in** — the two-question minimum check-in from FR-008, nothing adaptive yet.

**Exit criterion:** a real Garmin account, a real profile, and a real (if rough) plan exist end-to-end, and one
completed run has a check-in attached to it. If the Garmin MCP server doesn't expose something assumed here,
that's found out now, not in Milestone 4.

---

## Milestone 1 — Foundations

No dependencies on other Must-have features; build in parallel.

- Persistent State Model (harden to the full schema from `technical-specification.md` section 2.5)
- Safety Guardrails
- Garmin Connection & Auth Handling (harden: manual-mode fallback, clear failure reporting)
- Running Session Type Library

## Milestone 2 — First layer on top

- Runner Profile Management (harden: amend without losing history)
- Garmin Data Retrieval (harden: full metric set, dedup, provenance tagging)
- Rest & Recovery Scheduling
- Weekly Wellbeing Check-in
- Decision Traceability & Explanation Log

## Milestone 3 — Data collection & individual planning pieces

- Mobility Planning
- Strength Training Integration
- Post-Run Check-in (harden: full question set, skip handling, linking to activities)
- Manual Data Entry & Correction
- Baseline Assessment (harden: explicit gap-filling questions, uncertainty disclosure)

## Milestone 4 — First plan can now be generated properly

- Initial Marathon Plan Generation (harden: full phase structure, real mobility/strength integration, taper)
- Evidence Conflict Resolution
- Completion-Readiness Assessment

## Milestone 5 — Weekly operating loop

- Weekly Plan Generation

## Milestone 6 — Adaptation and review close the loop

- Adaptive Replanning
- Weekly Review Generation

All 20 Must-have features are covered by the end of Milestone 6.

---

## Should Have — insertion points

Should-haves don't need to wait for Milestone 6; each becomes buildable as soon as its own dependencies clear:

| Feature | Ready after |
|---|---|
| Data Status View | Milestone 2 |
| Plan Version Comparison | Milestone 2 |
| Low-Impact Cross-Training Alternatives | Milestone 5 |
| Exportable Weekly Summary | Milestone 6 |
| Natural-Language Commands | Milestone 6 + Data Status View (its widest-reaching dependency) |

## Could Have — after the MVP

Build only once all Must-haves (and whichever Should-haves are wanted) are done — these extend the design
without changing it (`technical-specification.md` section 6), so there's no structural reason to pull any of
them earlier:

Structured Workouts Written Back to Garmin · Charts and Trend Visualisations · Voice-Based Check-ins ·
Race-Day Checklist · Shoe and Equipment Tracking
