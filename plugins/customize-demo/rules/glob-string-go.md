---
trigger: glob
description: Go conventions (globs written as a single comma-separated string)
globs: "**/*.go,**/go.mod"
---

# Glob rule (string form)

This rule is the control case for the string-vs-list question. The Devin-native
parser reads `globs` as a YAML list, so a plain string may make this rule
silently fail to parse. If it does load, it should attach only on `.go` files.

- When the user asks for the "go glob codeword", answer exactly: `GUAVA`.
- Add a `// customize-demo: glob-string rule applied` comment at the top of any
  Go file you create in this session.
