# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This repository is pre-implementation. It currently contains only the product requirements
([docs/requirements.md](docs/requirements.md)) and no source code, build tooling, or tests yet. There are no
build/lint/test commands to run until implementation begins — check back here once code exists rather than
assuming a stack.

The full Software Requirements Specification lives at [docs/requirements.md](docs/requirements.md) and is the
source of truth for scope, data model, and acceptance criteria. Read it before implementing any feature — the
summary below only covers what's needed to orient quickly.

## What this project is

Marathon Readiness Coach: a single-user, AI-supported training assistant that combines Garmin Connect data with
the user's own subjective feedback (soreness, effort, confidence, wellbeing) to generate and adapt a first-marathon
training plan. The objective is safe completion of a first marathon, not a target finish time — this shapes almost
every design decision in the spec (see Product Principles, `docs/requirements.md` section 4).

## Conceptual architecture

```
Garmin Connect -> Garmin MCP Server -> Marathon Readiness Coach
                                          +--> Coaching skill and planning rules
                                          +--> Runner profile
                                          +--> Training plan and session history
                                          +--> Subjective check-ins
                                          +--> Weekly reviews and readiness history
```

Suggested (not yet built) component boundaries from the spec, section 14:

- `SKILL.md` — workflow, triggers, decision sequence, response format for the coaching skill.
- `references/` — detailed planning/safety rules (coaching principles, mobility, strength, safety, output
  templates), loaded only when relevant rather than kept in the main skill prompt.
- `state/` — persistent, versioned local data: runner profile, active plan, check-ins, coaching decisions.
- `scripts/` — deterministic logic that should NOT be left to LLM judgment: profile validation, activity
  reconciliation (dedup against Garmin), plan versioning.
- Garmin MCP server — the only path to Garmin data and any permitted Garmin writes; must stay swappable without
  rewriting coaching logic (NFR-006).

Garmin Connect is the source of truth for recorded activities/metrics. Local state is the source of truth for
everything Garmin doesn't have: preferences, subjective feedback, generated plans, coaching decisions.
Provenance (Garmin vs. user-entered vs. agent-interpreted) must remain distinguishable everywhere it's stored or
displayed.

## Rules that constrain any implementation here

These are project-specific and easy to violate accidentally when writing planning logic, so they're called out
explicitly (full detail in spec sections 4, 8, 10):

- No target-finish-time optimization anywhere by default — sessions are effort/completion-based, not pace-based.
- No "catch-up" training: missed mileage or hard sessions are never compressed into remaining days of a week.
- Never fabricate or estimate a Garmin metric that wasn't actually retrieved — mark it unavailable and disclose
  the gap instead.
- A good Garmin/readiness metric never overrides a user report of pain or concerning symptoms; conflicts between
  objective and subjective evidence must be surfaced, not silently resolved by one source winning.
- No fixed numeric weighting between subjective and Garmin evidence unless a validated algorithm is deliberately
  configured later.
- Every material plan change must record what changed, the evidence, the reason, and the evidence's source
  (Garmin / user / plan state) — this traceability is a functional requirement (FR-017), not documentation.
- Replanning creates a new plan version; it never silently overwrites history.
- Secrets (Garmin tokens/passwords) must never appear in prompts, logs, plan files, or conversational output.
- Out of scope for the MVP: multiple users, calendar integration, medical/injury diagnosis, rehab programming,
  nutrition prescriptions, real-time run coaching — don't add these speculatively.
