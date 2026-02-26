# project-bootstrap

One-time setup for consistent quality gates across your projects.

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin from the [not-my-job](https://github.com/drewburchfield/not-my-job) marketplace.

## Features

- Auto-detects language (TypeScript, Python, Go)
- Installs and configures linting, formatting, and type checking
- Configures issue tracker integration (Linear, Jira, GitHub Issues, or standalone)
- Stop hook enforces quality gates on every Claude session
- `/quality-gate` runs comprehensive PR review cycle with agent reviews, Devin.ai integration, and merge workflow

**Languages:** TypeScript (ESLint + Prettier), Python (ruff + pyright), Go (built-in tooling)

## Install

```
claude plugins install project-bootstrap@not-my-job
```

## License

MIT
