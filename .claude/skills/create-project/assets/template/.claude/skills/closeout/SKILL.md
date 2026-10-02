---
name: closeout
description: Finalize the current task after explicit user approval — complete the episode, run the promotion pass to propose registry updates, sync INDEX/README if structure changed, and tidy up. Use at the end of a task or work session.
---

# closeout

## 1. Review gate
If the active episode has no `## Agent review` record, offer to run `agent-code-review` first.
Run `code-review` if it has not already passed for this task's changes; do not proceed past a
FAIL.

## 2. User Approval Gate
Summarize the changes made on this task: what was changed and why, any deviations from the
original plan and the reason for each, and the review/test results. If the active episode's
`branch:` frontmatter field is set and this is a git repo, explicitly disclose the pending branch
operation too: which branch will be merged into which (the episode's `branch:` value, into the
detected default branch), and that the branch will then be deleted — step 8 below carries this out
automatically once approved here, with no separate confirmation of its own. Ask the user
explicitly: "Do you approve these changes?" This is a hard gate — do not proceed to step 3 without
an explicit yes, and it covers the branch merge/delete as well as the file changes. If the user
requests changes, make them, re-run `code-review`, and repeat this step.

## 3. Finalize the episode
Fill `## What was completed`, `## What worked well`, `## What didn't work well`, `## Learnings`.
Populate `related:` links + tags. Set `status: closed`. After closeout the episode is
append-only history.

## 4. Promotion pass (finalize → draft → review → confirm)
1. **Finalize the episode first** (step 3 above must be done). Before hunting for small
   extractable bullets, ask: is the whole episode itself one multi-step procedure? If so, that is
   the single candidate — its content belongs in one `docs/memory/promotion-drafts/<slug>.md`
   file, not several atomized entries.
2. **Draft the update.** For each candidate (guardrail, procedure, lesson, or term), either:
   - match an existing entry by id/summary similarity and propose appending this episode to its
     `episodes` list, incrementing `promotion_count`, and extending `content`/`draft_ref`; or
   - propose a new `status: draft` entry with best-guess `applicability` tags (existing
     `SEMANTICS.md` ids preferred; a genuinely new tag is marked provisional, not silently added).
   Long procedure content goes in a new/extended `docs/memory/promotion-drafts/<slug>.md` file via
   `draft_ref`, never inlined at length in `content`.
3. **Present the proposal to the user; apply only on confirmation.** Group it (Add to GUARDRAILS /
   PROCEDURES / LESSONS / SEMANTICS / Refine existing). On approval, write the registry changes
   and any new/updated `promotion-drafts/` files; each new/updated entry links back to its source
   episode; mark the episode's candidates resolved.
4. Do NOT edit `CODE_STANDARDS.md` — it is universal and reserved for the projects-level skill.

## 5. Sync structure
If files/folders changed materially, propose updates to `docs/INDEX.md` and `README.md`. Confirm
any deferred items are recorded in `docs/BACKLOG.md`.

## 6. Doc hygiene
Fix any obviously broken markdown links or `[[wikilinks]]` in files this task touched (see
`docs/ONBOARDING.md`'s markdown-conventions section). A rule specific to one dependency/subsystem
belongs in a scoped note next to that subsystem, never in `PROCEDURES.md`/`GUARDRAILS.md`.

## 7. Tidy
Remove scratch/temp files (deletion prompts per settings). If Python, verify `pyproject.toml`/
`.venv` are consistent. Sweep leftover `TODO:` markers and resolve or note them.

## 8. Branch cleanup (conditional)
Read the active episode's `branch:` frontmatter field, then run
`.claude/skills/closeout/scripts/merge-if-git.sh "<that value>"` (pass it empty/omit it if the field
is `null`; add `--no-delete` if the user wants the task branch kept after merging instead of
deleted). It reports one of: `not-a-git-repo` or `already-on-default-branch` (both normal no-ops
— nothing else to do), `no-recorded-branch-skip-merge` (the episode has no `branch:` value — nothing
to merge), `current-branch-mismatch-skip-merge` (the checked-out branch isn't the one the episode
recorded — refuses rather than merging/deleting the wrong branch), `detached-head-skip-merge`
(HEAD is detached — refuses rather than attempting a nonsensical merge), `merged-and-deleted`
(the recorded task branch is merged into the default branch and removed), or `merged-and-kept`
(merged but the branch was left in place, with `--no-delete`). Before merging it also warns (to
stderr, non-fatal) if the episode file for this branch is missing, not yet `status: closed`, or
still has unresolved `TODO:` markers — treat any of these as a sign steps 3/7 were skipped and go
back to them. Step 2's approval gate already covers this merge+delete, so no further confirmation
happens here. Never run `git init` yourself to force this step to apply.
