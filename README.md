<div align="center">

<img src="https://ghrb.waren.build/banner?header=project-bootstrap%20%F0%9F%8F%97%EF%B8%8F&subheader=Quality%20tooling%20and%20PR%20gates%20in%20one%20command&bg=0a1628&secondaryBg=1e3a5f&color=e8f0fe&subheaderColor=7eb8da&headerFont=Inter&subheaderFont=Inter&support=false" alt="project-bootstrap" width="100%">

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin from the [not-my-job](https://github.com/drewburchfield/not-my-job) marketplace.

![License](https://img.shields.io/badge/license-MIT-blue)

</div>

## What it does

Auto-detects your project language, installs and configures linting, formatting, and type checking, then enforces quality gates on every Claude session. Run `/quality-gate` for a comprehensive PR review cycle with agent reviews, Devin.ai integration, and merge workflow. Run `/ship-loop` to carry a branch or PR through checks, review, remediation, merge gates, deploy verification, and closeout. Run `/supervision-loop` to consolidate developer activity across Slack, GitHub, Linear, and repo review into a current feedback and delegation brief. If a repo has a private `.claude/supervision-loop/default.md`, `/supervision-loop` uses it automatically.

## Commands

| Command | What it does |
|---------|-------------|
| `/quality-gate` | PR review cycle with agent reviews, Devin.ai integration, and merge workflow |
| `/ship-loop` | Shipping state machine for PR watch, remediation, greenlit merge, deploy verification, and closeout |
| `/supervision-loop` | Developer supervision loop for PR review, post-merge review, feedback drafts, and next assignment recommendations |

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
