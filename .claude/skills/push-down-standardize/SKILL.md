---
name: push-down-standardize
description: Propagate a change already applied to the deployed projects-level standard out to every sibling project (including project-skill's own operational .claude/skills/), using a sync manifest and three-way merge so a sibling's local customizations and the deployed standard's real changes never clobber each other. Invoked by graduate-to-template and push-updates; not invoked directly by a user.
---

# push-down-standardize

Implements the standardize-down half of
`docs/superpowers/specs/2026-09-24-cross-project-lesson-sync-v4-design.md`. Given a change already
written to the deployed standard (`Documents/projects/.claude/skills/create-project/assets/
template/`, or a registry entry in its `docs/memory/*.md`), apply the same change to every
sibling project listed in `Documents/projects/PROJECTS.md`, **including `project-skill` itself** —
project-skill is an ordinary sibling for this purpose; only its own `pull-updates`/`push-updates`
skills and `projects-template/` output are out of scope here (those aren't part of the deployed
template, so nothing here ever touches them).

## 1. Enumerate targets

Read `PROJECTS.md` for the sibling list. For each sibling, ensure a manifest file exists at
`sync-state/<sibling>.yaml` (relative to this skill's own folder) — create an empty one
(`{}`) if this is the sibling's first sync.

## 2. Deletions (once per sibling, before the per-item loop)

For each sibling, before iterating per tracked item: read this sibling's manifest file's
full `tracked:` key set, and separately determine the deployed standard's full current key
set for everything section 3 scopes it to cover (every file under the template tree, every
registry entry across its `docs/memory/*.md` files). Call
`sync_diff.find_deleted_paths(tracked_keys, current_deployed_keys)` **once** for this
sibling, over these two full sets -- never per individual item (per
`diff-against-sync-manifest/SKILL.md` section 4's granularity rule: folding this into the
per-item loop below would make every other tracked item look deleted, since it would never
appear in that single item's own comparison).

For each key this returns: if the sibling's current content for that key still equals its
own recorded `last_synced_content_ref` (no local customization), delete it from the sibling
and remove its manifest entry. If the sibling has locally customized that exact item since
the last sync, this is a contradiction -- add it to step 4's true-contradictions list instead
of deleting anything.

## 3. Per sibling, per tracked item: diff-against-sync-manifest

For every file under the deployed standard's template tree, and every entry across its
`docs/memory/*.md` registries: invoke `diff-against-sync-manifest` with the deployed standard's
template tree as source, this sibling's corresponding path as target, and this sibling's manifest
file. Excludes build/cache artifacts automatically (that sub-skill's own rule).

For a target file that uses `{{PROJECT_NAME}}`/`{{DATE}}`/`{{PROJECT_ABS_PATH}}` tokens (the seven
root/doc files every scaffolded project has: `AGENTS.md`, `README.md`, `docs/INDEX.md`,
`docs/BACKLOG.md`, `docs/CODE_STANDARDS.md`, `docs/ONBOARDING.md`, `.claude/settings.local.json`):
first invoke `substitute-template-placeholders` with this sibling's stored variables against the
deployed standard's *current* content, and pass that substituted text as the source's "theirs"
side instead of the raw template bytes.

For a registry entry with a `draft_ref`, also propagate the referenced
`docs/memory/promotion-drafts/<slug>.md` file the same way (source = deployed standard's copy,
target = the sibling's copy, same manifest-tracked mechanism).

## 4. Collect and report true contradictions

Per the confirm-on-concern rule: every clean and successfully-reconciled change from step 3 has
already been applied directly (that's what `diff-against-sync-manifest` does). Collect only the
true contradictions it returns, across every sibling, into one list. If the list is empty, report
that every sibling standardized cleanly — this is the expected common case, not something to
apologize for. If non-empty, present it to the user for an explicit decision per contradiction
(showing base/ours/theirs); apply whichever side the user picks and update that item's manifest
entry to match the **source's** (post-transform, if this item is placeholder-bearing) content.

## 5. Report

Summarize what was applied to which sibling (files added/updated/deleted, registry entries
added/updated/deleted), and list every true contradiction that was resolved in step 4 and how.
