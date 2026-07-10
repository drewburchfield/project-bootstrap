# Fixture: qg-live-mode-plan (live dogfood)

You are an agent about to run **quality-gate**. Use **only** the SKILL TEXT and REVIEW SUITE text in this package (not prior training about other plugins).

## Task

For **each scenario**, output a short **execution plan** (bullets or YAML). State:

- `tier` you will claim (T0|T1|T2|T3|Incomplete)
- `adapter` / tools you will invoke
- `bot_wait`: yes|no and why
- `passes`: list of Review Suite pass ids you will run (or none)
- `gate_status` you expect if review is clean

### Scenario A — Host is Claude Code; pr-review-toolkit available; no external bots configured

User: `/quality-gate --local`

### Scenario B — Host is Codex; Clawpatch installed; no pr-review-toolkit; bots empty

User: run quality gate on local diff

### Scenario C — Host is Grok; only single general `/review` style subagent available; bots empty

User: quality gate local

### Scenario D — Host is OpenCode; bots empty; typed TypeScript PR exists

User: full quality-gate (not --local) after push

### Scenario E — Host is Claude Code; project-meta has `externalBots: ["devin"]`, botWaitSeconds 60; just pushed remediation

User: continue quality-gate after push

### Scenario F — Host is agy; nothing like pr-review-toolkit; user asks quality gate

## Hard constraints (from skill if present)

- Do not invent Claude-only tools on non-Claude hosts.
- Do not unconditional-wait for Devin if bots are not configured.
- T1 cannot claim suite Pass.

## Output format

```
### A
tier: ...
adapter: ...
bot_wait: yes|no — reason
passes: [...]
gate_if_clean: Pass|Incomplete|Blocked
notes: ...

### B
...
```

End with **GROUNDED** if plans only follow the package skill text, else **NOT GROUNDED**.
