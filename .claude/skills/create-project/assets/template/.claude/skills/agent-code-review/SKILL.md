---
name: agent-code-review
description: Thorough, multi-agent review of the current task's changes AND their fit in the larger project, with a triage-and-fix loop that repeats until no important issues remain. Use before closeout for substantial changes. Fixes bugs and small/medium improvements; defers big improvements to the backlog.
---

# agent-code-review

## 1. Resolve the change set + load context
Resolve changes (git diff → episode `## Files touched` → ask). Load `docs/INDEX.md`, `docs/memory/PROCEDURES.md`, `docs/memory/GUARDRAILS.md`, `docs/memory/LESSONS.md`, `docs/memory/SEMANTICS.md`, and `docs/CODE_STANDARDS.md`.

## 2. Dispatch 6 lens subagents (in parallel)
Dispatch each lens subagent with `model: haiku` unless this task explicitly calls for deeper
judgment on a given lens (state why, then use the default/unspecified tier for that lens only).
Each reviews the change set through ONE lens and reports findings (`file:line` + issue + suggested fix):
1. **Design/complexity** — DRY/SOLID/KISS/OOP, helper functions, ≤50 LoC.
2. **Readability** — naming, comments (≤2 lines, only when needed), docstrings (public only, accurate/current).
3. **Redundancy/dead code** — orphaned code, duplication, consolidation under uniform classes/helpers.
4. **Robustness** — logging verbosity/levels, error handling/types, consistency.
5. **Testing** — appropriate unit/integration/e2e coverage.
6. **Fit & docs** — architecture-fit vs INDEX, cross-cutting impact, documentation currency.

## 3. Triage (main agent)
For each finding decide:
- **Bug → fix now**, no matter how big.
- **Improvement:** small/medium → fix now; **big** genuine improvement (NOT a bug in disguise) → **defer**: add an entry to `docs/BACKLOG.md` (what · why deferred · source).

## 4. Fix
Spin up agents (one per fix, or sensibly grouped) to implement the fix-now items. Verify each fix.

## 5. Re-review
Repeat from step 2 on the updated change set until no more bugs or small/medium improvements come back.

## 6. Record
In the active episode's `## Agent review`, log each round: lens findings summary, triage decisions, fixes applied, items deferred to BACKLOG.
