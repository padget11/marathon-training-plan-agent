# Running Session Type Library (FR-007)

The catalog of supported running session types. Every session in a plan must use one of these `subtype` values
(paired with `category: run`, except cross-training which is its own category) and must state a purpose and
effort guidance drawn from here. Nothing in this catalog requires a goal-marathon pace — none of these
runners have a target time, so every effort description is relative (perceived exertion, breathing, ability to
talk) rather than pace-based.

This is the library only; it is not yet wired into plan generation (Initial Marathon Plan Generation's own
hardening, including full session-type variety, is later work — see `docs/roadmap.md`).

| Subtype | Purpose | Effort guidance | Default priority |
|---|---|---|---|
| `easy` | Build aerobic volume and consistency with minimal fatigue cost. | Conversational pace — you should be able to talk in full sentences throughout. | supporting |
| `long` | Extend time on feet and build the specific endurance a marathon requires. | Conversational pace throughout; walk breaks are fine and don't undermine the session's purpose. | priority |
| `recovery` | Active recovery between harder efforts, or after a demanding week. | Noticeably easier than an easy run — if in doubt, go slower. Skippable in favor of full rest without any downside. | supporting |
| `steady` | A moderate, sustained effort that's harder than easy but still comfortably controlled. | Comfortably hard — able to speak in short phrases, not full sentences. Used sparingly and only once an aerobic base is established. | supporting |
| `run-walk` | A valid, deliberate strategy for building duration on feet, not a fallback for when a runner "can't" run continuously. | Alternate running and walking segments on a set or felt schedule; effort during the running portions stays conversational. | priority or supporting, matching whatever run it replaces |
| `technique_strides` | Short bursts of quicker, relaxed running to develop turnover and running economy — not a fitness test. | Comfortably brisk, never a sprint; full recovery between reps; stop if form breaks down. | optional |
| `controlled_quality` | Conservative introduction of structured harder running once a base exists. | Clearly harder than steady but still controlled — should feel demanding, not maximal; always followed by easy days. | optional early on; may become supporting later in a plan |
| `cross_training` (category `cross_training`, not `run`) | Low-impact aerobic alternative to a running session when appropriate. | Easy-to-moderate effort, no impact-related strain; examples include cycling, swimming, or an elliptical session. | optional |

Notes:

- Easy and long runs are the foundation for this completion-oriented MVP; the other types are introduced
  conservatively and only as a plan's base develops.
- `optional` sessions must be presented as clearly skippable without consequence; `priority` sessions are the
  ones a reduced-load week should protect first.
- Run-walk is never framed as a failure or a lesser version of "real" running — it's listed as `priority` or
  `supporting` to match whatever session it stands in for, never demoted just for being run-walk.
