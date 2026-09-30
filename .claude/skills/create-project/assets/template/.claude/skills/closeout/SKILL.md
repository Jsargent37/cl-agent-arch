---
name: closeout
description: Finalize the current task — complete the episode, run the promotion pass to propose registry updates, sync INDEX/README if structure changed, and tidy up. Use at the end of a task or work session.
---

# closeout

## 1. Review gate
If the active episode has no `## Agent review` record, offer to run `agent-code-review` first.

## 2. Finalize the episode
Fill `## What was completed`, `## What worked well`, `## What didn't work well`, `## Learnings`. Populate `related:` links + tags. Set `status: closed`. After closeout the episode is append-only history.

## 3. Promotion pass (finalize → draft → review → confirm)
1. **Finalize the episode first** (step 2 above must be done). Before hunting for small
   extractable bullets, ask: is the whole episode itself one multi-step procedure? If so, that is
   the single candidate — its content belongs in one `docs/memory/promotion-drafts/<slug>.md` file,
   not several atomized entries.
2. **Draft the update.** For each candidate (guardrail, procedure, lesson, or term), either:
   - match an existing entry by id/summary similarity and propose appending this episode to its
     `episodes` list, incrementing `promotion_count`, and extending `content`/`draft_ref`; or
   - propose a new `status: draft` entry with best-guess `applicability` tags (existing
     `SEMANTICS.yaml` ids preferred; a genuinely new tag is marked provisional, not silently added).
   Long procedure content goes in a new/extended `docs/memory/promotion-drafts/<slug>.md` file via
   `draft_ref`, never inlined at length in `content`.
3. **Present the proposal to the user; apply only on confirmation.** Group it (Add to GUARDRAILS /
   PROCEDURES / LESSONS / SEMANTICS / Refine existing). On approval, write the registry YAML changes
   and any new/updated `promotion-drafts/` files; each new/updated entry links back to its source
   episode; mark the episode's candidates resolved.
4. Do NOT edit `CODE_STANDARDS.md` during closeout — it is the project's universal engineering
   baseline and should only be updated deliberately, not as a side-effect of a task.

## 4. Sync structure
If files/folders changed materially, propose updates to `docs/INDEX.md` and `README.md`. Confirm any deferred items are recorded in `docs/BACKLOG.md`.

## 5. Doc hygiene
Fix any obviously broken markdown links or `[[wikilinks]]` in files this task touched (see `docs/ONBOARDING.md`'s markdown-conventions section). A rule specific to one dependency/subsystem belongs in a scoped note next to that subsystem, never in `PROCEDURES.yaml`/`GUARDRAILS.yaml`.

## 6. Tidy
Remove scratch/temp files (deletion prompts per settings). If Python, verify `pyproject.toml`/`.venv` are consistent. Sweep leftover `TODO:` markers and resolve or note them.
