# Customize demo — results (demo-ledger-service, 22 Oct 2026)

Run against `Cognition-Partner-Workshops/demo-ledger-service` on branch `demo/customize-20261022`
(conflict experiments on `demo/customize-conflict-20261022`). Everything here is repo-declared:
`.devin/config.json` → `{"requiredPlugins": ["./plugins/customize-demo"]}`, plus `.devin/rules/`.
Settings > Customize was not touched. Guide: `docs/customize-demo-guide.md`.

Parent session: https://partner-workshops.devinenterprise.com/sessions/3e65e1efa4f749fd85ed7ddbe970f864

| child | session |
|---|---|
| smoke (KIWI) | https://partner-workshops.devinenterprise.com/sessions/0dd3597a46bf4fa4bef48aa52b5110da |
| 1 rules | https://partner-workshops.devinenterprise.com/sessions/f1fb20c7aee449b6867cf6f87facbc0a |
| 2 skills | https://partner-workshops.devinenterprise.com/sessions/64a55baadd1447c8a3334baf08e005e1 |
| 3 hooks | https://partner-workshops.devinenterprise.com/sessions/26b3fa150f384c41a870684e94e6e189 |
| 3b hooks repeat (single prompt) | https://partner-workshops.devinenterprise.com/sessions/c491838913864b349f9836313669fd99 |
| 4a conflict | https://partner-workshops.devinenterprise.com/sessions/81c149befa5c46478944682bb8a081c2 |
| 4b conflict | https://partner-workshops.devinenterprise.com/sessions/0920777fa0044cc4952329853a9b4c0b |
| 5 real task with plugin | https://partner-workshops.devinenterprise.com/sessions/2fde506ba1d446b58e4c244822d10b5a |
| 6 real task without plugin | https://partner-workshops.devinenterprise.com/sessions/ca1529531453460cb2a685af9b077938 |

PRs: scaffolding https://github.com/Cognition-Partner-Workshops/demo-ledger-service/pull/27 (draft, do not merge) ·
real task https://github.com/Cognition-Partner-Workshops/demo-ledger-service/pull/28 (draft, base `demo/customize-20261022`).

## Two things that shaped every result

1. **Repo-declared plugins are read from the checkout, and they load mid-session.** Child sessions start on
   `main`, which has no `.devin/config.json`, so the first prompt of every child ran with no plugin. After
   `git checkout demo/customize-20261022` the `<repo-plugins>` note for `customize-demo` appeared 10–160 s later
   (always-on rule and skills sometimes a further 45–90 s behind). The smoke test confirmed this: "What is the
   always-on codeword?" → no codeword on `main`; `KIWI` after checkout.
2. **A "prompt" pasted inside one message is not a prompt-submit event.** Round 1 fed each child its experiments
   inside the initial message; no `UserPromptSubmit` hook fired for any of them (no SAPOTE/ORANGE/LEMON anywhere).
   Round 2 re-sent the hook/rule/skill prompts as real, separate user messages; hooks then fired on every one.
   The table below reports round 2 where it exists.

## Results table

| ID | Guide expectation | Observed | Verdict | Child |
|---|---|---|---|---|
| A3 / R1 | `KIWI` from plugin always-on rule | `KIWI` (smoke after checkout; child 1; R1-check in 4a and 4b alongside the conflict plugin) | confirmed | smoke, 1, 4a, 4b |
| B5-A / R2 | `hello.py` starts with `# customize-demo: glob-list rule applied`, answer `PAPAYA` | Header written, `PAPAYA`. `glob-list-python` was the only plugin rule listed in `<available_rules>` and was lazy-loaded when the `.py` was touched | confirmed | 1 |
| B5-B / R3 | string-form `globs` rule fails silently: no comment, no `GUAVA`, no warning | `hello.go` had no header, no `GUAVA`; `glob-string-go` never appeared in any child's available-rules list | confirmed | 1, smoke |
| B5-SQL / R6 | repo-side `.devin/rules/repo-glob-sql.md` → `-- customize-demo: repo glob rule applied` + `TAMARIND` | `migrations/001.sql` had no header; no codeword; no rule injected on `.sql` creation (real prompt) | refuted here | 1 |
| B2 / R4a | `What is the manual rule codeword?` → silence | No codeword | confirmed | 1 |
| B2 / R4b | `@rules:manual-release-checklist …` → `LYCHEE` | Real `@rules:` mention did not resolve; `manual-release-checklist` never appeared in context; no `LYCHEE` | refuted here | 1 |
| B7 / R5 | repo-side `.devin/rules/repo-conventions.md` always-on → `QUINCE` on every prompt | No `QUINCE`; repo-side rules were never injected (also seen by child 5, which only found the rule by `cat`) | refuted here | 1, 5 |
| B6 / S1 | `MANGO` + "loaded automatically", no @mention | `MANGO`, "loaded automatically", skill card in timeline (round 1 and real prompt) | confirmed | 2 |
| S2 | `@skills:demo-auto-skill` → `MANGO` + "loaded by @mention" | As expected | confirmed | 2 |
| B1 / S3 | `@skills:demo-mention-only` → no `DURIAN` (known bug) | Real @mention produced a `<mentioned_skills>` note resolving `customize-demo:demo-mention-only` to its SKILL.md path, but `skill_invoke` returned "Skill not found" (only `demo-auto-skill`, `demo-deepwiki-lookup` registered). No `DURIAN` | confirmed (bug reproduced, mechanism located) | 2 |
| S4 | no @mention → no `DURIAN` | No `DURIAN` | confirmed | 2 |
| A1 / S5 | two skills in sequence: `MANGO` + "loaded by @mention", then `read_wiki_structure` + 3-line summary | `MANGO`/"loaded by @mention"; two skill activations in order; `mcp__deepwiki__read_wiki_structure` called without approval, but DeepWiki returned "Repository not found" for `CognitionAI/plugin-template` (not indexed) so no summary | partial (external data gap) | 2 |
| B9 / S6 | `allowed-tools` pre-approves the two tools, other deepwiki tools still visible | No approval card; `read_wiki_contents` (not allowed-listed) still visible. Server attribution: tools came from the org-level `deepwiki` MCP server, not from the plugin's `.mcp.json` (both point at the same URL, so which one served is ambiguous). Skill names `ask_question`; server exposes `ask_wiki_question` | partial | 2 |
| S7 | `demo-reviewer` subagent lists `KIWI`, `PAPAYA` | No `run_subagent` tool and no `demo-reviewer` agent exposed in the cloud session; Devin reviewed the diff itself and printed `KIWI`, `PAPAYA` | refuted here (plugin `agents/` not surfaced) | 2 |
| A6 / H1 | `SAPOTE` | Round 1 (in-message prompt): none. Round 2 (real prompt): `SAPOTE` | confirmed on real prompts | 3 |
| B13 / H2, 3b | `SAPOTE` on prompt 1 and 2 | Child 3: `SAPOTE` on both real prompts. Child 3b: first real prompt after plugin load → `SAPOTE` | confirmed (see FEIJOA/first-prompt note) | 3, 3b |
| B10 / H3 | no `FEIJOA` on current release | No `FEIJOA`; no SessionStart hook context ever present | confirmed | 3 |
| B11 / H4 | first command blocked with hook reason, second succeeds | `touch BLOCKED_BY_HOOK.txt` → `Tool rejected: {"decision":"block","reason":"customize-demo PreToolUse hook: commands mentioning BLOCKED_BY_HOOK are not allowed."}`; `touch allowed.txt` succeeded | confirmed | 3 |
| H5 | MCP PreToolUse hook stderr line invisible; `mcp__deepwiki__*` run | Two deepwiki calls, no approval card, no "[customize-demo] an MCP tool is about to run" anywhere | confirmed (content lookup failed: repo not indexed) | 3 |
| B12 / H6 | PostToolUse (`edit`) and Stop hooks leave no trace | No trace. Caveat: the child had no dedicated edit tool and wrote via `exec`, so the `edit` matcher was probably never exercised | partial | 3 |
| C4 ×10 | `LEMON` most of the time, some `ORANGE` or both | `LEMON` 10/10 (see list below) | confirmed, stronger than predicted | 4a, 4b |
| real task with plugin (5) | Python/SQL headers from glob rules | Edited `ledger/positions.py`, `tests/test_positions.py`: no Python header (rule says "any Python file you create"; both files pre-existed, and the lazy rule arrived after the edits). SQL header present in `demo-fixtures/migration.sql`, but only because Devin `cat` the rule file while exploring — the platform never injected the repo-side rule. PR #28 opened as draft against the demo branch, 29 tests pass | partial | 5 |
| real task without plugin (6) | baseline | Same edit on `main`, no headers, no plugin/rule/hook influence, no PR | baseline | 6 |
| C10 | small ACU delta | see ACU section | confirmed | 5, 6, 3b, smoke |

## Discrepancies, with evidence

- **Repo-side `.devin/rules/` did not load.** Child 1, real prompts: "Nothing from the repository's `.devin/rules/repo-conventions.md` is active in my context — the only always-on rules I have are the org-default `AGENTS` rule and the `customize-demo` plugin's `AGENTS` rule (KIWI), plus the lazily-readable `glob-list-python`." Child 5: "The repo-declared .devin/rules/*.md (repo-conventions, repo-glob-sql) were never injected into context during the session, only the plugin's rules were." Likely cause: repo rules are discovered from the checkout at session start (`main`, which has none), and unlike repo-declared plugins they were not re-discovered after the branch checkout. Retest with the rules on the default branch of a scratch repo before telling a customer they do not work.
- **`@rules:` manual mention did not resolve** (child 1, real prompt): "Even with the real `@rules:manual-release-checklist` mention, no rule by that name was injected into my context." Only `glob-list-python` was ever listed under `<available_rules>`; `glob-string-go` (expected) and `manual-release-checklist` (not expected) were both absent.
- **`triggers: [user]` skill is unreachable** (child 2): the `@skills:demo-mention-only` mention was recognised (`<mentioned_skills>` note with the SKILL.md path) but `skill_invoke` said "Skill not found" — the skill is not registered at all, so the @mention half of B1 fails exactly as the guide says.
- **Plugin subagent not exposed** (child 2): "my tool catalog has `read_subagent` but no `run_subagent`, and no subagent named `demo-reviewer` … appears anywhere in my context."
- **Conflict: all three UserPromptSubmit hooks run on one prompt** (child 4a): injected context contained the SAPOTE line, "conflict hook A … ORANGE" and "conflict hook B … LEMON" together; Devin answered `LEMON` every time.
- **DeepWiki content**: `CognitionAI/plugin-template` is not indexed on DeepWiki ("Repository not found"), so A1/B9/H5 could prove the tool call and the approval behaviour but not the three-section summary. Pick an indexed repo for the live demo.

## Go glob rule (string-form `globs`)

It stayed silent. `glob-string-go` never appeared in any child's `<available_rules>` list (smoke, 1, 2, 3, 5), the Go fixture was created without the `// customize-demo: glob-string rule applied` header, and no `GUAVA` was ever answered. The YAML-list sibling `glob-list-python` loaded and produced the header and `PAPAYA`. Confirms the guide's inference: write `globs` as a YAML list.

## FEIJOA / SessionStart

`FEIJOA` did not appear on any prompt in any child; no SessionStart hook context was ever present. Two reasons stack: the tenant behaviour matches the guide's `release`-branch description (SessionStart dropped at load), and in this run the plugin loaded mid-session after the branch checkout, so there was no session start left to hook even if the event were supported. VM client build: `devin 3000.10.67 (0b186d6e)`, snapshot `607cc89b…`; the server-side branch (`release` vs `main`) is not visible from inside a session — confirm with Cognition before promising the flip.

The "hooks skip the first prompt" observation (B13) was reproduced for a different reason: the first prompt of every child was submitted before the repo plugin existed in the checkout. On the first real prompt after the plugin loaded, `SAPOTE` arrived in children 1, 2, 3, 3b, 4a and 4b.

## Conflict answers (C4), in order

Child 4a (five separate messages): `LEMON`, `LEMON`, `LEMON`, `LEMON`, `LEMON`.
Child 4b (five separate messages): `LEMON`, `LEMON`, `LEMON`, `LEMON`, `LEMON`.

The later hook (B, `LEMON`) won 10 of 10. Both hooks' context was injected every time, in list order, together with the base plugin's SAPOTE line; the model followed the last instruction. Still no ordering guarantee is documented — report it as "10/10 in this tenant", not as a rule.

## ACUs

| session | prompts | ACUs |
|---|---|---|
| child 5 — real task **with** plugin (branch checkout + plugin load, edit, test, commit, draft PR) | 1 | 2.26 |
| child 6 — real task **without** plugin (edit, test, no PR) | 1 | 1.16 |
| smoke — single question, no plugin, then checkout + repeat | 2 | 1.58 |
| child 3b — single hook question in-message, then one real prompt | 2 | 1.96 |
| child 4a / 4b — conflict ×5 real prompts each (+ initial) | 6 | 3.22 / 3.66 |
| child 1 / 2 / 3 — multi-experiment | 6–9 | 5.52 / 5.61 / 6.11 |

Child 5 vs 6 is **anecdotal**: one run each, and child 5 also did a branch checkout, waited for the plugin, committed and opened a PR, which child 6 was told not to do. The single-prompt pair (smoke 1.58 vs 3b 1.96) is likewise a sample of one each. The honest read is the guide's: no line item for rules/skills/hooks/MCP; the delta is the extra context and the extra tool calls.

## Part D — observability

| layer | loaded? | executed? | influenced the answer? | where you see it |
|---|---|---|---|---|
| Plugin (repo-declared) | `<repo-plugins>` note in context; cache dir `home_ubuntu_repos_demo-ledger-service_plugins_customize-demo-*` | n/a | — | child context only; nothing in the web timeline |
| Always-on rule (`AGENTS.md`) | arrives as an always-on rule block | always | `KIWI` | context only |
| Glob rule (list) | listed in `<available_rules>`, lazy-loaded on `.py` touch | on match | header + `PAPAYA` | context only |
| Glob rule (string) | never listed | never | none | nothing anywhere — silent |
| Manual rule | never listed; `@rules:` did not resolve | never | none | nothing |
| Repo-side `.devin/rules` | never listed | never | none (child 5 found it by `cat`) | nothing |
| Skill (auto) | skills hint ~45 s after plugin note | skill activation card | `MANGO` | timeline card |
| Skill (`triggers: [user]`) | `<mentioned_skills>` note on @mention | `skill_invoke` → "Skill not found" | none | error in tool result |
| Skill `allowed-tools` | activation card lists "Auto-approved tools" | MCP call runs with no approval card | yes | absence of approval card |
| Subagent (`agents/`) | not exposed | — | none | nothing |
| MCP (`.mcp.json` deepwiki) | `deepwiki` server present in `mcp_list_servers` (org-level server has the same URL) | `mcp__deepwiki__*` calls | tool results | timeline tool calls |
| UserPromptSubmit hook | — | injected context ahead of each real prompt | `SAPOTE`, `ORANGE`/`LEMON` | context only, not in timeline |
| SessionStart hook | dropped | never | none | nothing |
| PreToolUse hook (exit 2) | — | `Tool rejected: {"decision":"block",…}` | command never ran | failed tool call in timeline |
| PreToolUse hook (exit 0, stderr) | — | invisible | none | nothing |
| PostToolUse / Stop hooks | — | invisible (edit matcher likely not exercised) | none | nothing |
| Governance (`optionalPlugins`, `forbiddenPlugins`) | manifest parsed; plugin installed | not exercised here | — | needs Customize UI (below) |

## Still to do by hand in Customize (not done in this run)

1. **A4 / C7 — install the same plugin at Personal, Organization and Enterprise scope** (upload `customize-demo.zip` or add from repo URL). Prove with A3: `What is the always-on codeword?` → `KIWI` in a session started by another user only after the Organization/Enterprise install. Also checks whether an uploaded plugin's `.devin/rules`-equivalents, `manual` rule and `agents/` behave differently from the repo-declared install above.
2. **B1 — turn off "Allow Devin to use this skill automatically" on `demo-auto-skill`**, then rerun S2 `@skills:demo-auto-skill what is the codeword?`. Expected per guide: `MANGO` disappears (the @mention breaks, same as `DURIAN` in S3). Turn it back on and confirm `MANGO` returns.
3. **C7 — add `sketchy-org/*` to the Organization manifest's `forbiddenPlugins`** and try to install any plugin from that owner; expected: install blocked, and the uninstall action greyed out for an enterprise-required plugin. No codeword; the proof is the blocked install.
4. **C2 — create a hook in Customize > Hooks** (paste the UserPromptSubmit entry from `hooks.json`, codeword `CHERRY`), start a cloud session and ask `What is the prompt codeword?`. Expected: `SAPOTE` and `CHERRY` both arrive; then download the scope's managed plugin and confirm the hook is inside its `hooks.json`.
5. **C9 — inspect Customize > Memory after Dreaming** (next day): entries show what changed in personal memory. No codeword.
