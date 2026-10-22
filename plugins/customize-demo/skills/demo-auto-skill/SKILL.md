---
name: demo-auto-skill
description: Use when the user asks for the "auto skill codeword" or asks you to run the automatic-skill check. Narrow on purpose so you can test whether Devin picks it without an @mention.
---

# demo-auto-skill

Default triggers (`[user, model]`): Devin may load this skill on its own when
the request matches the description, and the user may also load it with
`@skills:demo-auto-skill`.

Steps:
1. Say which trigger loaded you: "loaded automatically" if there was no
   @mention in the prompt, otherwise "loaded by @mention".
2. Answer the codeword: `MANGO`.
3. Do nothing else.
