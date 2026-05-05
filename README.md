<div align="center">

<img src="https://ghrb.waren.build/banner?header=project-bootstrap%20%F0%9F%8F%97%EF%B8%8F&subheader=Quality%20tooling%20and%20PR%20gates%20in%20one%20command&bg=0a1628&secondaryBg=1e3a5f&color=e8f0fe&subheaderColor=7eb8da&headerFont=Inter&subheaderFont=Inter&support=false" alt="project-bootstrap" width="100%">

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin from the [not-my-job](https://github.com/drewburchfield/not-my-job) marketplace.

![License](https://img.shields.io/badge/license-MIT-blue)

</div>

## What it does

Auto-detects your project language, installs and configures linting, formatting, and type checking, then enforces quality gates on every Claude session.

For PR work: `/quality-gate` runs a thorough local review pass with agent reviews, Devin.ai integration, and remediation cycles, with optional merge after explicit approval. `/ship-loop` is the "yes, ship this" driver that wraps quality-gate's review with CI watching, `--greenlit`-gated merge, deploy verification, and issue closeout.

For team work: `/supervision-loop` consolidates a teammate's Slack, GitHub, and Linear activity into a current feedback and delegation brief. It drafts replies in your voice and never auto-sends. If a repo has a private `.claude/supervision-loop/default.md`, `/supervision-loop` uses it automatically.

## Commands

| Command | What it does |
|---------|-------------|
| `/bootstrap` | Auto-detect project language, install quality tooling, set up stop hooks, and pick complementary plugins |
| `/quality-gate` | Thorough PR review cycle with agent reviews, Devin.ai integration, and remediation, with optional merge after approval |
| `/ship-loop` | Shipping driver: wraps quality-gate with CI watching, remediation, `--greenlit`-gated merge, deploy verification, and closeout |
| `/supervision-loop` | Developer supervision loop: open and merged PR review, draft feedback in your voice, suggest next assignments |

## Features

- Auto-detects language (TypeScript, Python, Go)
- Installs and configures linting, formatting, and type checking
- Issue tracker integration (Linear, Jira, GitHub Issues, or standalone)
- Stop hook enforces quality gates on every Claude session
- Shipping loop for PR babysitting and greenlit merge workflows
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

## License

MIT
