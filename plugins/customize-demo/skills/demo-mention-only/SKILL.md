---
name: demo-mention-only
description: Use when the user asks for the "mention-only skill codeword". Automatic use is disabled (triggers = [user]) so Devin must never pick this on its own.
triggers:
  - user
---

# demo-mention-only

`triggers: [user]` is what the Customize editor writes when you turn off
"automatic use". This skill should load only from `@skills:demo-mention-only`.

Steps:
1. Say: "demo-mention-only loaded by @mention".
2. Answer the codeword: `DURIAN`.
