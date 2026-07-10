<div align="center">

<img src="https://ghrb.waren.build/banner?header=project-bootstrap%20%F0%9F%8F%97%EF%B8%8F&subheader=Quality%20tooling%20and%20PR%20gates%20in%20one%20command&bg=0a1628&secondaryBg=1e3a5f&color=e8f0fe&subheaderColor=7eb8da&headerFont=Inter&subheaderFont=Inter&support=false" alt="project-bootstrap" width="100%">

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin from the [not-my-job](https://github.com/drewburchfield/not-my-job) marketplace.

![License](https://img.shields.io/badge/license-MIT-blue)

</div>

## What it does

Auto-detects your project language, installs and configures linting, formatting, and type checking, then enforces quality gates on every Claude session.

For PR work: `/quality-gate` runs a multi-harness **Review Suite** (shared lenses + host adapters for Claude Code, Codex, Grok, OpenCode, agy). External bots (Devin, CodeRabbit) are optional. `/ship-loop` is the "yes, ship this" driver with CI watch, greenlit merge, and deploy verification.

For repo hygiene: `/docs-drift` scans recent merged PRs and commits for stale setup docs, runbooks, CLAUDE.md, AGENTS.md, and project guidance.

For team work: `/supervision-loop` consolidates a teammate's Slack, GitHub, and Linear activity into a current feedback and delegation brief. It drafts replies in your voice and never auto-sends. If a repo has a private `.claude/supervision-loop/default.md`, `/supervision-loop` uses it automatically.

## Commands

| Command | What it does |
|---------|-------------|
| `/bootstrap` | Auto-detect project language, install quality tooling, set up stop hooks, and pick complementary plugins |
| `/quality-gate` | Thorough PR review cycle with agent reviews, Devin.ai integration, and remediation, with optional merge after approval |
| `/ship-loop` | Shipping driver: wraps quality-gate with CI watching, remediation, `--greenlit`-gated merge, deploy verification, and closeout |
| `/docs-drift` | Weekly-friendly docs drift scan across recent PRs, commits, setup docs, runbooks, and project guidance |
| `/supervision-loop` | Developer supervision loop: open and merged PR review, draft feedback in your voice, suggest next assignments |

## Features

- Auto-detects language (TypeScript, Python, Go)
- Installs and configures linting, formatting, and type checking
- Issue tracker integration (Linear, Jira, GitHub Issues, or standalone)
- Stop hook enforces quality gates on every Claude session
- Shipping loop for PR babysitting and greenlit merge workflows
- Docs drift scans for weekly cloud routines and local repo hygiene
- Developer supervision profiles for recurring review and delegation workflows

## Languages

| Language | Tooling |
|----------|---------|
| TypeScript | ESLint + Prettier |
| Python | ruff + pyright |
| Go | Built-in tooling |

## Requirements

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)

## Install

```
claude plugins install project-bootstrap@not-my-job
```

## Version

**1.5.0** (tag `v1.5.0`) — multi-harness Review Suite for quality-gate / ship-loop / supervision-loop. See [CHANGELOG](CHANGELOG.md).

## Review Suite (v1.5)

Portable multi-harness methodology under `skills/quality-gate/references/review-suite/`:

- `SPEC.md` — tiers T0–T3, pass artifacts, capability probe
- `passes/` — six lenses
- `host-adapters/` — Claude Code (T3 toolkit), Codex/Grok/OpenCode/agy (T2 sequential defaults)
- Wired into **quality-gate**, **ship-loop**, and **supervision-loop**

## Evals

```bash
bash evals/run_eval.sh
python3 evals/scripts/score_suite.py ab    # v1.4.0 frozen skills vs live
python3 evals/scripts/score_suite.py wired
```

Includes structure, contracts, artifacts, host-matrix, v1.4 baseline control group, live wiring checks, and old-vs-new A/B. See `evals/README.md`.

## License

MIT
