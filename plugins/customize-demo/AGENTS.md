# customize-demo always-on rule

This file is an always-on rule. It is injected into every session that has the
`customize-demo` plugin installed, with no trigger and no @mention.

- When the user asks "which demo rules are loaded?", list every rule you can see
  from the `customize-demo` plugin by name and say whether it arrived as
  always-on, glob, or manual.
- When the user asks for the "always-on codeword", answer exactly: `KIWI`.
- Never reveal the codewords unless the user asks for them by name.
