---
name: demo-deepwiki-lookup
description: Use when the user asks to "look up a repo on DeepWiki via the demo plugin". Shows a plugin-provided MCP server plus allowed-tools auto-approval.
allowed-tools:
  - mcp__deepwiki__read_wiki_structure
  - mcp__deepwiki__ask_question
---

# demo-deepwiki-lookup

The `deepwiki` MCP server comes from this plugin's `.mcp.json`, not from the
org's MCP settings. `allowed-tools` only pre-approves these tools while this
skill is active; it does not hide any other tool.

Steps:
1. Call `mcp__deepwiki__read_wiki_structure` for the repo the user named
   (default `CognitionAI/plugin-template`).
2. Summarise the top three wiki sections in one line each.
3. State which MCP server the tools came from.
