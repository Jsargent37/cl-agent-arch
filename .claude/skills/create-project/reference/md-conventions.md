---
tags: [reference]
---

# Markdown conventions (Obsidian ↔ VSCode)

Apply to every `.md` written into a project so files work in BOTH VSCode preview and Obsidian.

1. **Frontmatter tags.** Start each doc/note `.md` with YAML frontmatter containing `tags:`. Taxonomy: `episode`, `onboarding`, `index`, `standards`, `backlog`, `review`, `readme`, `guidelines`, plus freeform `area/*`. **Exception:** `SKILL.md` files are exempt (Agent Skills frontmatter schema, `name:`/`description:` only) and the four `docs/memory/*.yaml` registries are exempt (they are data files with their own schema, not vault notes — see the registry schema instead of this tag taxonomy).
2. **Links — point to a file you can open.** This is the rule most often broken; follow every clause.
   - Use a standard relative Markdown link to a **specific, openable file**: `[text](relative/path.md)`. The target must open on click (a `.md`, `.pdf`, image, etc.).
   - **Never link a bare folder.** `[docs](docs/)` opens nothing in VSCode preview or Obsidian. Link a real file inside it (usually its `README.md` or `INDEX.md`); if nothing there is worth opening, don't make it a link at all — write the path as inline code (`` `docs/` ``).
   - **Never use `[[wikilinks]]`** in body text — they don't render in VSCode preview.
   - **Resolve the path from the file the link lives in.** A file in `docs/` links a sibling as `NAME.md`, its parent's file as `../README.md`, a child as `sub/NAME.md`. Do not repeat the current folder's own name — a `docs/` file linking `docs/NAME.md` resolves to `docs/docs/NAME.md` and is broken.
   - **The one place `[[ ]]` is allowed:** the `related:` YAML frontmatter property (Obsidian's link-property syntax; a Markdown link there is a dead string).
   - After writing or moving a doc, verify every link opens its target (VSCode: Ctrl-click; Obsidian: hover-preview).
3. **Obsidian one-time setup** (tell the user): Settings → Files & Links → "Use [[Wikilinks]]" OFF; "New link format" = Relative path. Open the folder that contains your projects as the Obsidian vault so the cross-project graph works.

Token substitution: replace `{{PROJECT_NAME}}`, `{{SLUG}}`, `{{DATE}}`, and `{{PROJECT_ABS_PATH}}` in every copied file.
