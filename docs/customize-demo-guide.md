# Devin Customize demo guide

One runnable experiment for every point in Infosys's email on Skills, Rules, MCPs, Plugins, Hooks and the Knowledge migration. Each section quotes the email, gives the exact prompt to type, the result the docs and code predict, and the sentence to say once the result appears. **Inferred** flags each prediction that rests on reading code alone.

## Kit contents

| File | Purpose |
|---|---|
| `customize-demo.zip` | The main plugin: rules, skills, a subagent, hooks, an MCP server and governance fields. |
| `customize-demo-conflict.zip` | Two UserPromptSubmit hooks that contradict each other, for the conflict test. |
| `repo-side/.devin/rules/` | Two rule files to drop into any repository, for the pinned-Knowledge replacement test. |
| `customize-demo-guide.md` | This guide. |

Every rule, skill and hook answers with its own fruit codeword, so a single question shows which layer fired and which stayed silent.

| Codeword | Comes from | Layer |
|---|---|---|
| KIWI | `customize-demo/AGENTS.md` | always-on rule in a plugin |
| PAPAYA | `rules/glob-list-python.md` | glob rule, `globs` written as a YAML list |
| GUAVA | `rules/glob-string-go.md` | glob rule, `globs` written as one string |
| LYCHEE | `rules/manual-release-checklist.md` | manual rule, @mention only |
| MANGO | `skills/demo-auto-skill` | skill with default triggers |
| DURIAN | `skills/demo-mention-only` | skill with `triggers: [user]` |
| SAPOTE | `hooks.json` UserPromptSubmit | hook ran on this prompt |
| FEIJOA | `hooks.json` SessionStart | hook ran at session start |
| ORANGE / LEMON | conflict plugin, hooks A and B | which contradicting hook won |
| QUINCE | `repo-side/.devin/rules/repo-conventions.md` | always-on rule in the repository |
| TAMARIND | `repo-side/.devin/rules/repo-glob-sql.md` | glob rule in the repository |
| (blocked command) | `hooks.json` PreToolUse `^exec$` | exit code 2 blocked a tool call |

## Setup

You need: an org where you are admin (for Organization scope and governance), enterprise admin rights if you want the Enterprise step, one scratch GitHub repository Devin can access, and optionally the Devin CLI for the comparison steps.

1. Settings > Customize. Choose **Personal** scope.
2. Plugins > Add > **Upload zip** > `customize-demo.zip`. The preview should list 4 rules (1 always-on, 2 glob, 1 manual), 3 skills, 1 subagent, hooks on 5 events and the `deepwiki` MCP server. Approve the MCP server when asked; it needs no credentials.
3. Push the `customize-demo/` folder to your scratch repository as well, so you can later add it with **From repository** using `https://github.com/<you>/<repo>.git#customize-demo`. That is the path used for the scope-promotion steps.
4. Copy `repo-side/.devin/rules/` into the root of the scratch repository and push.
5. Start a new cloud session on the scratch repository. Every experiment below starts a fresh session unless it says otherwise.

CLI or Desktop comparison: `devin plugins install ./customize-demo`, then `/hooks`, `/skills` and `devin rules list` show what loaded. Cloud has no equivalent view today; that difference is itself one of the demo points.

## Part A. Confirm what Infosys said works

### A1. Skills by @mention, in sequence
Prompt: `@skills:demo-auto-skill @skills:demo-deepwiki-lookup first give me the codeword, then look up CognitionAI/plugin-template on DeepWiki via the demo plugin.`
Expected: Devin reports `MANGO` and "loaded by @mention", then calls `mcp__deepwiki__read_wiki_structure` and summarises three sections. The timeline shows two skill activation cards in order.

### A2. Skill update and approval workflow
Prompt: `Update the demo-auto-skill so its codeword is MANGO-2. Save the change.`
Expected: Devin proposes the skill edit and the session shows an approval card; nothing changes until you approve. After approval, Customize > Skills shows the new version. Then revert by re-uploading the zip, or approve a second edit back to `MANGO`.

### A3. Always-on rules apply on every session
Prompt: `What is the always-on codeword?`
Expected: `KIWI` on the first prompt, on the fifth prompt, and in a second session started an hour later.

### A4. Personal and Organization scopes stay isolated
Install the zip under **Personal** only. Ask a colleague in the same org to start a session and ask for the always-on codeword.
Expected: they get no answer; the plugin is yours alone. Install it under **Organization** and repeat: now they get `KIWI`.

### A5. MCP servers work from cloud sessions
Prompt: `Look up CognitionAI/plugin-template on DeepWiki via the demo plugin.`
Expected: tool calls named `mcp__deepwiki__*` in the timeline, with the plugin's MCP approval card the first time.

### A6. UserPromptSubmit hooks run
Prompt: `What is the prompt codeword?`
Expected: `SAPOTE`.

### A7. Many hooks on one event
Covered in C4 below with the conflict plugin.

## Part B. The observations

### B1. Turning off automatic use also breaks @mention
Email: "Disabling 'Allow Devin to use this skill automatically' appears to make the skill unavailable even through manual @mention."
Prompt: `@skills:demo-mention-only what is the codeword?`
Expected today in cloud: Devin says it has no such skill or answers without `DURIAN`, even though Customize lists the skill. The editor stores that checkbox as `triggers: [user]` in the skill frontmatter, and the cloud @mention loader only offers skills that allow model triggers, so the skill is unreachable. This is the confirmed gap in the reply.
Also prompt: `What is the mention-only skill codeword?` with no @mention.
Expected: Devin never says `DURIAN`. The restriction half of the feature works; the @mention half is the bug.
Say: "Leave automatic use on and narrow the description until the fix ships."

### B2. Skills and Rules have deletion as the only off switch
Email: "Skills and Rules currently do not appear to have an enable/disable option."
Demo: open any skill in Customize and look for a toggle; there is only the automatic-use checkbox and delete.
Prompt: `What is the manual rule codeword?` then `@rules:manual-release-checklist what is the manual rule codeword?`
Expected: silence on the first, `LYCHEE` on the second. `trigger: manual` on a rule and `triggers: [user]` on a skill (once B1 is fixed) are the closest thing to "installed but inactive". Uninstalling a plugin, or listing it in `forbiddenPlugins`, switches off a whole set at once.

### B3. Promoting between scopes means re-adding
Email: "Promoting assets between scopes appears to require recreation."
Demo: with the Personal install in place, open Organization scope and add the same plugin **From repository** using your scratch repo URL. Then remove the Personal copy.
Expected: the plugin sheet offers install, download and uninstall. Re-adding at the higher scope is the promotion, and the repository install makes that a two-click re-add with every file intact. For an uploaded plugin, the sheet's download action gives you the zip to upload at the next scope. Both installed at once: the session dedups by plugin name, so you see a single `KIWI`.

### B4. Skill suggestions appear inconsistently
Email: "Skill auto-suggestions did not consistently appear after repeatable workflows."
Demo A: run the same three-step prompt (`create hello.py, run it, show the output`) in two sessions.
Expected: a suggestion card is not guaranteed. Devin offers a skill at specific moments, such as after it tests an app end to end or works out a setup step, so a routine workflow often produces none.
Demo B: `Save what you just did as a skill called run-hello.`
Expected: an approval card every time. Say: "Ask for the skill explicitly; suggestions are a bonus."

### B5. Glob rules fail silently
Email: "Glob Rules can silently fail in Cloud environments."
Prompt A: `Create hello.py that prints hi. Then tell me the python glob codeword.`
Expected: the file starts with `# customize-demo: glob-list rule applied` and Devin says `PAPAYA`.
Prompt B: `Create hello.go that prints hi. Then tell me the go glob codeword.`
Expected (**inferred** from the parser): the file has no comment, Devin has no `GUAVA`, and Customize shows no warning. The native rule parser reads `globs` as `Option<Vec<String>>`; a comma-separated string fails to parse and the rule is dropped. The official `plugin-template` repo's `team-conventions` rule uses the string form, so this test also checks the template.
Fix to show: edit `rules/glob-string-go.md` to a two-item list, re-upload, rerun B, and `GUAVA` appears.
Repo-side variant: `Create migrations/001.sql with one CREATE TABLE. Then tell me the sql glob codeword.`
Expected: `TAMARIND` and the SQL header comment, from the rule inside the repository.

### B6. Descriptions are optional in the form but decide matching
Email: "Descriptions are labeled as optional but appear to play an important role in matching and triggering behavior."
Prompt (no @mention): `What is the auto skill codeword?`
Expected: `MANGO` and "loaded automatically", because the description says exactly when to use the skill.
Then edit the skill in Customize, blank the description, save, start a new session and ask again.
Expected: Devin misses the skill most of the time. The description is what Devin reads at session start to decide whether to load it. Say: "Treat the description as required for anything that should trigger on its own, and write it as 'use when the user asks X'."

### B7. Pinned Knowledge became description-driven skills
Email: "After migration, the repository association is retained as metadata, but the resulting Skill appears to remain description-driven."
Demo: open Customize > Skills and find a migrated skill that used to be pinned to a repository; its sheet shows the repository as metadata only. Start a session on that repository with a prompt unrelated to the skill's description.
Expected: the skill stays unloaded. Then, in the same repository, prompt: `What is the repo rule codeword?`
Expected: `QUINCE` from `repo-side/.devin/rules/repo-conventions.md`, on every prompt, with no description match needed. This is the replacement for pinned Knowledge: an always-on rule in the repository's `.devin/rules/` (or its `AGENTS.md`). Devin includes up to 16 KiB of each always-on rule, so keep them short.

### B8. Knowledge uploads changed
Email: "Knowledge does not appear to support uploads in the same way as before."
Demo: Settings > Knowledge now opens Customize. Walk through each way to add guidance: Customize > Skills > New; Plugins > Add > From repository; Plugins > Add > Upload zip (the kit zip is the example).
Expected: the old free-text Knowledge form is gone; everything is a skill, a rule or a plugin.

### B9. MCP permissions stop at the server
Email: "There does not appear to be a mechanism for granting permissions at the individual tool level within an MCP server."
Demo: open Customize > MCPs > deepwiki. The sheet offers connect/disconnect and approval, with no per-tool list.
Prompt: `@skills:demo-deepwiki-lookup look up CognitionAI/plugin-template on DeepWiki via the demo plugin, then list every deepwiki tool you can see.`
Expected: Devin uses the two tools named in the skill's `allowed-tools` without an approval prompt and still lists the server's other tools. `allowed-tools` pre-approves; it hides nothing. Say: "Scope the credential you connect (read-only token or service account) until per-tool permissions exist."

### B10. SessionStart hooks in cloud
Email: "SessionStart hooks could not be validated in Cloud sessions."
Prompt: `What is the session-start codeword?`
Expected on the current release: Devin lacks `FEIJOA`. The cloud hook loader drops `session_start` and `session_end` (`UNSUPPORTED_CLOUD_EVENTS` on the `release` branch). On `main` since 20 Oct, `session_start` runs for uploaded plugins' hooks marked `blocking` before the first prompt, so rerun this after the next release and expect the answer to flip.

### B11. PreToolUse runs invisibly until it blocks
Email: "PreToolUse hooks appeared to be loaded, but no observable effect was seen."
Prompt: `Run this exact shell command: touch BLOCKED_BY_HOOK.txt. Then run: touch allowed.txt. Report what happened to each.`
Expected: the first command fails with the hook's reason text ("commands mentioning BLOCKED_BY_HOOK are not allowed"), because the hook exited with code 2; the second succeeds. Say: "A PreToolUse hook that exits 0 and prints nothing has done its job invisibly. Make it block a known command to prove it runs. The matcher is a regex on the tool name (`^exec$`), so a matcher written like a permission glob matches nothing."

### B12. Loaded, executed, skipped or ignored
Email: "It was often difficult to determine whether a hook had been loaded, executed, skipped, or had influenced the final response."
Demo: after B11, open the timeline. The blocked `exec` shows as a failed tool call; the `PostToolUse` hook that fired on the `edit` in B5 and the `Stop` hook at the end show nothing at all.
Expected: three hook runs, one visible trace. Hooks are best effort and fail open: an unsupported event is dropped at load, an exit code other than 0 or 2 is logged and ignored, and a successful hook that adds nothing leaves no card. Cloud has no `/hooks` list. Say: "Today, prove a hook with a side effect you can see: a block, an added codeword, or a file it writes."

### B13. Hooks skip the first prompt
Email: "In some scenarios, hooks appeared not to take effect on the initial prompt but did appear to work in subsequent interactions."
Prompt 1 of a brand-new session: `What is the prompt codeword?`
Prompt 2: the same question.
Expected: `SAPOTE` both times. If prompt 1 misses it, keep the session URL: Devin can begin the first message before the session machine that runs hooks is ready, so hooks apply once the machine is up. Repeat five times and note the ratio.

### B14. Plugin creation lacks reference examples
Email: "The plugin creation experience can be challenging for first-time users due to the limited availability of reference examples."
Demo: open https://github.com/CognitionAI/plugin-template (`hello-world`, `team-conventions`, `kitchen-sink`, with `node scripts/validate-plugins.mjs`), https://github.com/CognitionAI/team-marketplace-template (a repo holding several plugins with CI) and https://github.com/CognitionAI/devin-marketplace (the catalog that Customize > Plugins browses). Then open the kit's `customize-demo/` folder next to them: same layout, `.devin-plugin/plugin.json`, `AGENTS.md`, `rules/`, `skills/<name>/SKILL.md`, `agents/`, `hooks.json`, `.mcp.json`.

## Part C. The clarifications requested

### C1. Which hook events run in Enterprise Cloud
Demo: the kit's `hooks.json` has UserPromptSubmit, SessionStart, PreToolUse, PostToolUse and Stop. Run A6 (SAPOTE), B11 (block), B10 (FEIJOA).
Expected: SAPOTE yes, block yes, FEIJOA no. Answer to give: command-type hooks run in cloud for PreToolUse, PostToolUse, PermissionRequest, UserPromptSubmit, Stop and PostCompaction. SessionStart and SessionEnd are dropped on the current release (SessionStart is on its way). Prompt-type hooks, where a model evaluates the hook, run only in CLI and Desktop.

### C2. Do Customize hooks depend on plugins or the CLI
Demo: Customize > Hooks > New, paste the UserPromptSubmit entry from `hooks.json` (change the codeword to `CHERRY`). Start a cloud session and ask for the prompt codeword.
Expected: both `SAPOTE` (plugin) and `CHERRY` (Customize hook) arrive, with no CLI involved. Answer: a hook created in Customize is saved into that scope's managed plugin, so it is already packaged and runs in cloud on its own.

### C3. Telling unsupported from failed from silent
Demo: B10 (unsupported, dropped at load), B12 (silent success), and one failure: add a hook whose command is `exit 1`.
Expected: all three look identical in the timeline. Answer: hooks fail open; exit code 2 is the only outcome that surfaces, as a blocked action. Until the timeline shows every hook run, design hooks with a visible side effect.

### C4. Is "the later hook wins" deterministic
Demo: install `customize-demo-conflict.zip` (Personal). New session.
Prompt: `What is the conflict codeword?` Repeat in five new sessions.
Expected: `LEMON` most of the time (hook B is listed second), with `ORANGE` or both words on some runs. Both hooks run; their context is appended in list order and the model decides. Answer: no ordering guarantee is documented, so put the combined logic in one hook per event, or use exit 2 so the hook blocks the action instead of persuading the model.

### C5. Packaging existing Customize assets into an organizational plugin
Demo: Customize > Plugins shows the managed plugin that holds everything created in the UI at that scope. Open its sheet and use the download action to get a zip; unzip it next to the kit and compare the layout.
Expected: the same `skills/`, `rules/` and `hooks.json` shapes. Answer: nothing needs recreating. Download the zip, commit the files to a plugin repository, and install that repository at the target scope.

### C6. Sample plugins and reference implementations
Covered in B14. Add that the kit itself validates with `node scripts/validate-plugins.mjs` when placed under `plugins/` in a `plugin-template` clone.

### C7. Progressing from Personal to Organization to Enterprise
Demo: the path, live. (1) Personal upload of the zip, iterate. (2) Push to the scratch repo; install **From repository** at Organization, mark it required. (3) At Enterprise, add it to the manifest as required or optional, and watch the org's Customize page show it as inherited and locked.
Expected: the plugin appears once per scope; the uninstall action is greyed out at Organization for an enterprise-required plugin; the `forbiddenPlugins` entry (`sketchy-org/*`) blocks any plugin from that owner at lower scopes. Answer: build in Personal, stabilise in Organization as required, lift to Enterprise when every org needs it; keep the source in git so each step is a plain install.

### C8. Plans for cross-scope promotion
Answer, stated plainly: no promote action exists today and we have logged the request. The repository install is the present workaround and makes promotion a re-install. Avoid dates.

### C9. Dreaming
Demo: Customize > Memory. Point at the list of Dreaming runs and open one.
Expected: each entry shows what changed in your personal memory. Answer: Dreaming runs roughly once a day in the background for an active user, reviews that user's recent sessions and tidies personal memory notes. It leaves skills, rules and plugins untouched, affects no other user, and the Memory page is the place to judge its value. It records zero ACU usage today.

### C10. ACU consumption
Demo: run A3 (one prompt, `KIWI`) in a session with the plugin installed and in another without it, then open each session's usage figure.
Expected: a small delta, from the extra context (always-on rules and skill descriptions at session start) and any extra tool calls (the hook commands). Answer: ACUs measure the work Devin does; skills, rules, hooks and MCPs have no line items of their own. Prefer skills (loaded on demand) over long always-on rules, keep rules under the 16 KiB cap, and connect only the MCP servers a team uses.

## Part D. Observability checklist for the closing

Where each layer shows itself today, so the asker can see the gap and the workarounds in one place.

| Layer | Visible in the session | Visible in Customize | Workaround |
|---|---|---|---|
| Always-on rule | nothing | plugin sheet lists it | codeword question |
| Glob rule | nothing | plugin sheet lists it, parse failures silent | codeword plus file header |
| Skill (auto or @mention) | activation card | skill sheet | ask Devin which trigger loaded it |
| Hook, adds context | nothing | hook listed | codeword question |
| Hook, blocks (exit 2) | failed tool call with reason | hook listed | this is the only visible path |
| Hook, unsupported event | nothing | hook listed | know the supported list (C1) |
| MCP tool call | tool call card, approval card | MCP sheet | PreToolUse `^mcp__.*` matcher to log |
| Plugin install | approval card first time | plugin sheet, indexing issues | reindex |
| Dreaming | its own session in Memory | Memory page | read the diff |

CLI and Desktop have `/hooks`, `/skills` and `devin rules list`; cloud lacks all three today, which is the request already filed with the product team.

## Appendix. Findings while building the kit
- `globs` must be a YAML list in the Devin-native rule parser (`WindsurfRuleFrontmatter`, `apps/chisel/config-importers`); `plugin-template`'s own `team-conventions` plugin uses a string. B5 confirms or clears it.
- Cloud `SessionStart` support changed on `main` on 20 Oct 2026 (runs for uploaded plugins' `blocking` hooks); the `release` branch still drops it. Check which branch the tenant runs before promising either behaviour.
- Hook visibility in the timeline is driven by an internal `show_output` flag on the native hook format. It is absent from the public docs and from the `hooks.json` schema, so leave it out of customer answers.
- Hooks in `hooks.json` run as shell commands on the session machine with the event JSON on stdin; the kit's commands use only `printf`, `grep` and `cat` so they need no extra tooling.
