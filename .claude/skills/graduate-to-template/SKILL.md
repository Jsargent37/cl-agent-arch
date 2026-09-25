---
name: graduate-to-template
description: Promote project-proven skills/tools/agents into the shared create-project template, with the same anti-duplication discipline distill applies at the project level. Run on demand only.
---

# graduate-to-template

Use this skill to promote an artifact that has proven itself across
multiple projects into the shared `create-project` template, so every new
project inherits it.

## When to use

- The user explicitly asks to graduate, promote, or upstream a skill/tool
  into the shared template
- **Never** run this automatically or on a schedule

## What it does

1. Run the scan script from anywhere in the repo tree:

Run from your projects workspace root:

   ```bash
   bash .claude/skills/graduate-to-template/scripts/scan-skills.sh
   ```
   This reports, for every project-level skill: how many projects have it,
   which projects, and whether any project's copy has drifted from the
   template original (for skills that are already in the template).
2. **Promotion gate — both required, not just recurrence:**
   - The same pattern independently proves out in **≥2 projects**.
   - It generalizes cleanly: no project-specific paths, names, or
     assumptions baked in that would need per-project editing after
     copying. A skill that recurs in 2 projects but hardcodes one
     project's directory layout does not pass this gate until it's
     rewritten to be generic.
3. **Template-side anti-duplication/staleness pass, before promoting
   anything new:** read every skill already in
   `.claude/skills/create-project/template/top-level-repo/.claude/skills/`
   (and its `.agents/skills` mirror) and check the candidate against them
   for overlap. Separately, audit the template's existing skills against
   each other for drift or redundancy — same Keep/Improve/Update/Retire/
   Merge verdicts as `/drift-check`, applied to the template. This
   keeps the template from accumulating near-duplicate skills as more
   projects graduate similar patterns over time.
4. Handle drift reports from the scan: when a project's copy of a template
   skill has diverged (a `DIFF:` line), propose merging the improvement
   upstream into the template rather than leaving the fork.
5. Handle global guardrail promotion: episode `signals` tagged
   `scope: global`, or the same guardrail `id` appearing in ≥2 projects'
   `Guardrails.md`, are candidates for the template's `CLAUDE.md` guardrail
   section (if `judgment` tier), `code-review` checklist (if `review`
   tier), or a shared hook (if `script` tier).
6. **Present a report of every proposed promotion, merge, and drift fix.
   Write nothing without explicit user confirmation.**
7. On approval, write directly into the template tree at
   `.claude/skills/create-project/template/top-level-repo/...` — this is
   the shared source that `bootstrap-top-level-repo.sh` copies into every
   new project. Never write shared skills at top-level
   `projects/.claude/skills/` outside the template.

## Notes

- This skill lives at the projects root, beside `create-project` — it is
  not copied into individual projects by the bootstrap script.
