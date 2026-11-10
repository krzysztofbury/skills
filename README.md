# Skills

Portable, production-minded Agent Skills, the hooks and base rules that go
with them, and an installer that links them into Claude Code, Codex, OpenCode,
and Gemini CLI.

## Contents

- `skills/`: portable [Agent Skills](https://agentskills.io/).
- `hooks/`: optional Claude Code guard and lint hooks, and the Codex patch lint
  hook. See [hooks/README.md](hooks/README.md).
- `rules/AGENTS.md`: harness-agnostic base rules for coding agents, installed
  as `CLAUDE.md` / `AGENTS.md` for each harness.
- `integrations/`: the Claude Code status line and the
  [OpenDeck Agents control surface](integrations/opendeck/README.md).
- `scripts/`: the installer, `agent-scratch`, a disposable scratch-directory
  helper for agents ([docs/AGENT-SCRATCH.md](docs/AGENT-SCRATCH.md)), and
  model-free OpenCode checks for council isolation and skill discovery.

## Available Skills

Skills are grouped in folders under `skills/`. The installer links each one by
its own name, so the group does not change how a skill is invoked.

| Group | Skill | Purpose |
| --- | --- | --- |
| `engineering` | `mcp-doctor` | Review, score and fix an existing MCP server's tool catalog against the specification and directory requirements. To build a server, use `mcp-builder`. |
| `engineering` | `pair-programmer` | Evidence-based code review, design trade-offs, and debugging, with proof before completion claims. |
| `engineering` | `pg-performance-advisor` | Diagnose PostgreSQL performance with read-only, redacted queries. |
| `engineering` | `sdlc-evaluator` | Audit a repository against an agentic software development lifecycle. |
| `engineering` | `sentry-observability` | Design and review Sentry observability with privacy controls. |
| `engineering` | `test-audit` | Check whether Python and SQL tests protect real behavior. |
| `agent-ops` | `council` | Convene installed agent CLIs as a multi-model council with anonymized peer review and a redaction gate. |
| `agent-ops` | `prompt-tuner` | Improve a skill, prompt or repeatable task by bounded experiment: diagnosis, frozen rubric, held-out cases, budget and round caps. |
| `agent-ops` | `retro` | Run a session retrospective that improves the project's rules and skills, with a ledger kept in the repository (`.agents/retro.jsonl`) or in SQLite; unattended runs propose changes as pull requests. |
| `roles` | `chief-of-staff` | Coordinate one project's GitHub board: intent-shaped issues, card moves, role runs with model and effort, and a short owner digest. |
| `roles` | `developer` | Implement one queued issue on its own branch, with its edge cases and evidence, and report `STATUS: READY` or `BLOCKED`. |
| `roles` | `reviewer` | Review one pull request against its issue and evidence and give `VERDICT: PASS` or `CHANGES`; never merges. |
| `roles` | `architect` | Split a large or open-ended issue into a decision record and intent-shaped child issues with `Blocked by` edges: `PLAN: READY` or `BLOCKED`. |
| `roles` | `devops` | CI, infrastructure and release changes as pull requests, and production deploys only after the owner approves the exact commit: `DEPLOY: DONE` or `BLOCKED`. |
| `roles` | `security-auditor` | Security review of a pull request with an exploit scenario per finding and hypotheses kept separate: `VERDICT: PASS` or `CHANGES`. |
| `roles` | `designer` | Design review of a UI pull request, checked in a real browser when possible and saying so when not: `VERDICT: PASS` or `CHANGES`. |
| `roles` | `approver` | Final gate for a reviewed pull request: squash-merge it, or escalate to the owner by the repository's escalation policy. |
| `content` | `clipping-curator` | Turn clipped web articles into concise, reusable notes in a configurable folder and format. |
| `content` | `plausible-insights` | Analyze Plausible Analytics traffic, content, and SEO for a configured site, through the Stats API or a Plausible MCP server. |
| `content` | `video-edit` | Edit recorded footage from a word-level transcript: cuts, cards, subtitles, loudness, vertical Shorts, verified renders. |
| `content` | `whatsapp-formatter` | Format concise, mobile-first WhatsApp messages. |
| `personal` | `oura` | Summarize sleep, readiness, and activity from the Oura API or an Oura MCP server. |
| `personal` | `ubiquiti-advisor` | Review a UniFi network through a configured, read-only controller connection. |

Skills that need user-specific details, such as a site, a device, a brand, or a
data source, read them from documented configuration. Each skill's `SKILL.md`
has a Configuration section where that applies.

## Install

```bash
scripts/install.sh            # every harness
scripts/install.sh --claude   # Claude Code only
scripts/install.sh --dry-run  # show what would change
```

Skills are symlinked, never copied. A sources file can add your own private
skills and pinned skills from other repositories next to these ones, without
forking or copying them. See [docs/INSTALL.md](docs/INSTALL.md).

Review a skill and its dependencies before linking it: some require an
authorized analytics, health-data, database, or network connection.
`video-edit` needs ffmpeg, Node, and local Whisper; see its Requirements
section.

## Safety And Privacy

- Never commit secrets, local permission files, network snapshots, or telemetry
  payloads.
- Skills default to analysis and recommendations. Actions with external impact
  require explicit user confirmation.
- Product APIs and SDKs change. Check the linked official documentation before
  applying integration examples to production.

## Scope

This is an independent community project, not affiliated with the services or
products named in individual skills.

## Project Docs

- [Specification](SPEC.md)
- [Installing](docs/INSTALL.md)
- [Releasing](RELEASE.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)
