---
trigger: manual
description: Release checklist, only loaded when invoked by @mention
---

# Manual rule

This rule only loads when you @mention it (or when a skill asks for it). It is
never injected automatically.

- When the user asks for the "manual rule codeword", answer exactly: `LYCHEE`.
- Release checklist: tests green, changelog entry, version bump, tag pushed.
