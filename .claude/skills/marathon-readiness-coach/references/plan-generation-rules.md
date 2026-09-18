# Plan generation: phase structure (FR-005)

Working backward from race week. Loaded by [SKILL.md](../SKILL.md) "Create first plan" step 4, alongside
`coaching-principles.md`, `session-types.md`, `mobility-guidance.md`, and `strength-guidance.md`.

- **Taper** — the last 2 weeks. Cut volume ~40-60% progressively; hold intensity and run frequency close to
  normal (`coaching-principles.md`'s tapering rule).
- **Marathon-specific prep** — the 2 weeks before that (3 if `W >= 16`). The peak long run happens in the first
  of these weeks; step back in the week(s) after it heading into taper. Strength drops to maintenance here (see
  SKILL.md "Create first plan" step 6).
- **Everything before that is the build block.** If `longest_recent_run_km < 8`, the first
  `max(1, round(build_block_weeks / 4))` weeks are a **consistency** phase: hold the long run at its current
  distance, focus on frequency and easy volume, no progression yet. The remaining build-block weeks are
  **aerobic volume / long-run development**: grow the long run week-to-week under the existing cap (never more
  than ~10% beyond the runner's longest run in the last 30 days), except every 4th week **counting from the
  start of this aerobic sub-phase** (not the consistency weeks before it, which have nothing to reduce from) is
  a **reduced-load week** — cut that week's long run and overall volume ~25% from the prior week, hold
  frequency; the week after a reduced-load week resumes progression from the last *non-reduced* week's distance,
  not from the cutback. (Reduced-load weeks are conservative, widely-taught practice, not something
  `coaching-principles.md` treats as strongly evidenced — it's explicitly excluded from that file's graded
  rules. Don't present it to the user as more settled than it is.) **Easy-day distances progress too, not just
  the long run** — grow them at the same conservative rate as the long run (same ~10% cap, same reduced-load
  cutback weeks), starting from their own baseline. Don't force a fixed long-run percentage of weekly volume —
  with only a few running days/week, hitting a generic ratio target (e.g. "long run ≤ 35% of the week") requires
  inflating the easy days to an unrealistic size of their own. Growing both at the same rate keeps the week's
  overall shape stable and realistic while fixing the actual defect: easy days never staying flat for months
  while only the long run grows.
- **Review points:** set `review_point: true` on the last week of the consistency phase (if present), the last
  week of the build block, and the last week of marathon-specific prep — three forward-looking markers for later
  replanning milestones, not new logic here.
- **Rest & Recovery Scheduling hard constraint (unchanged):** every week must include at least one
  `category: recovery` day for every day not in `available_running_days`, and must never schedule a hard/long
  run on every available day with no lower-intensity day between them.
