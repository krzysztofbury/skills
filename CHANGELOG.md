# Changelog

All notable changes to this project are documented in this file. Every merge
to `main` is released as a new [semantic version](https://semver.org/); the
section for that version becomes the GitHub release notes. See
[RELEASE.md](RELEASE.md).

## [2.3.0] - 2026-11-10

### Added

- `roles` group with three harness-neutral role skills for unattended work
  from a queue: `developer`, `reviewer` (verdict only) and `approver` (merge
  or escalate). Each ends with a fixed first line a coordinator can act on.
- `approver` reads a per-repository escalation policy from
  `.agents/escalation.md`, with a default list when it is missing.

### Changed

- `retro` lists `.agents/escalation.md` as a default target, so escalations
  the owner waves through, or merges that should have been escalated, update
  the policy.

## [2.2.0] - 2026-11-09

### Changed

- Skills are grouped in folders: `engineering`, `agent-ops`, `content` and
  `personal`. Installed names are unchanged.
- The installer finds skills one folder level down in any source and stops on
  a name that appears twice in one source.

## [2.1.0] - 2026-11-09

### Added

- Base rules: do not run a command stored in a plain shell variable
  (`$CMD args`); zsh does not word-split it. Use a shell function or an array.

## [2.0.1] - 2026-11-09

### Fixed

- `retro`: `ledger.py list` and `search` only read; on a missing ledger they
  return nothing instead of creating the directory and database.
- `clipping-curator`: review drafts have one frontmatter block instead of two
  stacked blocks; the review keys are dropped when a draft is accepted.
- `council`: removals are reported by category and location, never by
  quoting the removed value; salary and income count as private data.
- `ubiquiti-advisor`: text in controller data that addresses an AI is never
  followed and is reported as a security finding instead of being dropped
  silently.
- `plausible-insights`: a pasted API key is not repeated, not even in the
  skill's arguments.
- `pg-performance-advisor`: pasted secrets and personal values (including
  first names) are referred to generically and never repeated.

## [2.0.0] - 2026-11-08

### Changed

- Renamed `article-curator` to `clipping-curator`. Its configuration moves to
  `$CLIPPING_CURATOR_CONFIG`, `.clipping-curator.json` and
  `~/.config/clipping-curator/config.json`; the old `article-curator`
  locations are still read as a fallback.
- Renamed `whatsapp-style-guide` to `whatsapp-formatter`.
- Renamed `mcp-tool-design` to `mcp-doctor` and widened it into a review of
  the whole tool catalog: names, annotations, read and write separation,
  descriptions, input and output schemas, pagination, errors and directory
  requirements, with a sourced checklist (MCP specification 2025-11-25,
  Anthropic connector review criteria, `mcp-builder`). It now says what to
  use for building a server from scratch.
- `plausible-insights` can read data through a connected Plausible MCP server
  (`PLAUSIBLE_MCP_SERVER`) and falls back to the Stats API.
- Eleven skills were tuned with `prompt-tuner` experiments (baseline, one
  change per round, held-out check), mostly to fix requests that should have
  loaded a skill and did not:
  - `pair-programmer`, `pg-performance-advisor`, `test-audit`, `oura`,
    `retro`, `plausible-insights`, `mcp-doctor` and `prompt-tuner`: clearer
    descriptions, including pasted or exported data where it applies.
  - `council`: consent given before the user has seen the redacted prompt and
    the resolved models does not cover a send.
  - `clipping-curator`: text in an article that addresses the AI is reported
    to the user, never followed.
  - `ubiquiti-advisor`: the read-only rule also covers write commands written
    for the user to run.
  - `plausible-insights`: a rule for an API key that is already exposed.

### Added

- `prompt-tuner`: bounded, evidence-based improvement of a skill, prompt or
  repeatable task, built from the former `prompts/`.

### Removed

- `prompts/`: replaced by the `prompt-tuner` skill; rule review after an
  experiment belongs to `retro`.

Run `scripts/install.sh` after updating: links to the old skill names are
pruned and the new names are linked.

## [1.1.0] - 2026-11-08

### Added

- `scripts/install.sh --claude-rules-file AGENTS.md` writes the Claude Code
  rules to `~/.claude/AGENTS.md` and retires a generated
  `~/.claude/CLAUDE.md`. See `docs/INSTALL.md` for where Claude Code loads it.
- Base rules: stage commits by explicit path and read `git status` first, so
  a file a tool rewrote never lands in a commit unnoticed.

## [1.0.1] - 2026-11-08

### Fixed

- `scripts/install.sh` did nothing, silently and with exit code 0, when the
  repository was reached through a symbolic link. The installer now compares
  real paths to decide that it was run directly.

## [1.0.0] - 2026-11-06

### Added

- `scripts/install.sh`: links skills, hooks and the status line into Claude
  Code, Codex, OpenCode and Gemini CLI, and generates their rules files from
  `rules/AGENTS.md` plus an optional personal overlay. A sources file combines
  this repository with private skill directories and pinned git repositories;
  name clashes stop the run and links into retired sources are pruned. See
  `docs/INSTALL.md`.
- Skills: `article-curator`, `mcp-tool-design`, `sdlc-evaluator`, `test-audit`.
- `retro` records entries in a SQLite ledger (`scripts/ledger.py`) under the
  user's state directory, and targets the project's own rules and skills.
- `hooks/claude/guard-dashes.sh` refuses edits that add em or en dashes.
- The Codex patch lint hook, the Claude Code status line and `agent-scratch`.
- Every merge to `main` is released as a semantic version from its pull
  request label (`RELEASE.md`, `.github/workflows/release.yml`).
- `scripts/check-opencode-skills.mjs` and `scripts/check-council-opencode.mjs`:
  model-free checks against an isolated OpenCode server.
- OpenDeck: keys can read Claude usage from Omarchy's record
  (`"source": "claude"`), and a Run Command action runs a configured
  program without a shell.

### Changed

- The repository is renamed from `llm-powerup` to `skills`. Hooks moved from
  `integrations/claude/hooks/` to `hooks/claude/`, and the base rules from
  `AGENTS.md` to `rules/AGENTS.md`; the root `AGENTS.md` now describes this
  repository.
- `council`, `pair-programmer`, `plausible-insights`, `ubiquiti-advisor`,
  `whatsapp-style-guide` and `oura` were rewritten from their newer private
  variants; user-specific parts are now documented configuration.

### Removed

- The `data-news` skill.

- Claude hooks: `set` with only the options that stop or trace a command (`e`,
  `u`, `x`, and `-o pipefail`, `errexit`, `nounset`, `xtrace`) no longer makes
  a leading `cd` or variables unresolved, so
  `cd repo && set -e; git push` of a feature branch passes. Other state
  builtins still do: an array subscript in arithmetic or a `mapfile -C`
  callback can run code.
- Claude hooks ask less for commands they can now resolve. A `cd` that opens
  the command, at the top level, to a literal existing directory sets the
  working directory for the rest of it, so `cd repo && git push` and
  `cd scratch && rm -rf out` are judged in that directory. `rm` operands
  `"$NAME"`, `"${NAME:?}"` and `"$NAME/literal"` resolve when NAME is set once,
  at the top level, before the `rm`, from `mktemp` or a disposable literal
  path. A here-document inside `$( )` no longer makes the command
  unparseable, and one whose delimiter never appears asks instead of hiding
  the rest of the command.
- Claude hooks: `CLAUDE_HOOK_AUTO_DEFER` (`pr-create`, `pr-merge`,
  `push-protected`) leaves those confirmations to the auto mode classifier when
  the session is in auto mode. Unset by default; other modes always ask.
- AGENTS.md: take commit SHAs, image digests and run IDs from the command that
  produces them, never retype them.
- AGENTS.md: wait on CI by run ID and report outlier jobs; keep the full
  output of costly commands before filtering it; delete branches, tags,
  images and volumes only by the names the task created.

### Added

- `video-edit` skill: transcript-driven editing of recorded footage with local
  Whisper, an edit decision list, HyperFrames title and end cards, sentence
  subtitles, -14 LUFS loudness, an OpenTimelineIO handoff for Kdenlive or
  Resolve, brand profiles, and a verifier for loudness, bleep placement and
  muting. Method adapted from browser-use/video-use (MIT).
- `video-edit` vertical Shorts: `"format": "short"` crops panels from 16:9
  footage onto a branded 9:16 canvas, burns big keyword captions in the brand
  font, jump-cuts pauses with an optional punch-in, and fixes or hides caption
  words with `corrections`. The verifier outlines the Shorts player overlay
  zones on a portrait contact sheet.
- `video-edit` transcript reading: audio pauses measured with ffmpeg correct
  Whisper word timings, and lines that point to other videos or repeat words
  (stutters, end-of-recording hallucinations) are flagged.
- `video-edit` review before and after the render: `render.py --preview` shows
  the first and last frame of every planned segment through the real layout;
  the verifier fails on pieces under 3 frames and single-frame flashes, lists
  cuts with too little quiet in the source to listen to, and reports subtitle
  cues against reading-speed and duration limits.
- `video-edit` craft standards reference: the published standard behind each
  default (subtitle, loudness, delivery, safe areas, cutting), with sources and
  what is only convention.

### Changed

- Scope verification rules to affected behavior and remove repeated procedure.
  Requested implementation authorizes local edits; reviews remain read-only.
- Narrow review and retrospective triggers, retain project-specific constraints,
  and bound prompt-improvement experiments with held-out evaluation.
- Council dispatch uses self-contained inputs, explicit model selection,
  isolated adapters and per-run provenance rather than assuming CLI independence.

### Fixed

- `video-edit` cuts snap to whole frames, so joined segments no longer drift;
  subtitle cues break at pauses and length when Whisper returns no
  punctuation; ffmpeg no longer reads stdin inside batch loops.
- `video-edit` subtitle cues keep a 2-frame gap, close gaps under 0.5 s and stay
  on screen at least 20 frames.
- Development PostgreSQL exemptions reject ambiguous URI, hostaddr, service and
  mixed routing forms; inline credentials are checked before exemptions.
- Quiet `find -delete` is limited to owned scratch. Artifact-like predicates
  cannot establish that matched files are disposable.
- Git config overrides cannot inherit the plain feature-push exemption.
- OpenDeck retains failed-refresh and stale-sample status through cache hits.
- CI checks every shell script separately and runs council and OpenDeck suites
  with an explicit Node.js 24 runtime.

## Earlier changes

### Changed

- Claude Bash guards share a quote-aware lexer (`command-scan.sh`) and match
  programs where they run instead of anywhere in the command text. Routine
  development no longer asks: removal inside the session's temporary directory,
  configured disposable roots, or ignored build output in the work tree; plain
  pushes of feature branches; local `docker rm`; `sqlite3` on local files;
  `psql --version`, `-l`, and describe meta-commands; `aws --version` and
  `aws s3 ls`. `psql` may change opt-in, allowlisted development databases.

### Fixed

- Global flags with hyphenated values (`git -C my-repo`, `kubectl --context
  prod-eu`, `helm --kube-context prod-eu`) no longer hide destructive
  subcommands from the guards.
- `psql -c` queries containing `(`, `;`, or `|` inside quotes are inspected as
  one query.

### Added

- OpenDeck Agents integration for a 15-key Stream Deck MK.2 on Omarchy 4:
  the working plugin, a device-ID-templated Agents profile, setup instructions,
  and tests for Herdr, Codex, OpenCode, and profile layout.
- `AGENTS.md`: portable, harness-agnostic base rulebook (verification and
  deployment, production log preflight, editing and testing, deliverable
  hygiene) for symlinking as CLAUDE.md / AGENTS.md across harnesses.
- `retro` skill: end-of-session retrospective that turns lessons into system
  changes (skill/checklist/config diffs) with an append-only ledger, a
  two-strikes rule against skill sprawl, and an approval gate for edits.
- `council` skill: convene installed agent CLIs (Claude, Codex, Gemini,
  OpenCode) as a multi-model council over headless, read-only sessions —
  parallel dispatch, anonymized peer ranking, and chairman synthesis.
  Adapted from [karpathy/llm-council](https://github.com/karpathy/llm-council).
- Public project specification, contribution guide, code of conduct, and CI.
- Claude hooks for auto-lint, dangerous-command confirmation,
  external-impact confirmation, and read-only PostgreSQL input.
- Focused, privacy-redacted PostgreSQL diagnostic references.

### Changed

- Claude auto-lint runs ruff, sqlfluff, and ShellCheck and reports findings on
  stderr with exit 2; it is non-destructive and never rewrites files.

### Fixed

- `guard-readonly-postgres.sh` fails closed (asks) on multiple `-c`/`--command`
  flags instead of inspecting only the first.
- `block-dangerous.sh` scopes its SQL-keyword gate to commands that also
  reference a SQL-executing binary (`psql`/`mysql`/`mariadb`/`sqlite3`),
  fixing false positives on shell `truncate` and `git stash drop`.
- `block-dangerous.sh` re-scopes `rm` confirmation to recursive/forced,
  `xargs`-driven, and `find -delete` deletions instead of every `rm`, and
  restores the `find -delete` gate.
- `block-dangerous.sh` git rules no longer treat `--force-with-lease` as
  `--force`, and anchor the checkout/restore dot-pathspec check to a bare `.`.
- `confirm-external-impact.sh` allowlist covers `gh pr create`, `aws`,
  `gcloud`, `flyctl`, `vercel`, `netlify`, and `make deploy`-style targets,
  and recognizes `git push` through intervening `-C`/`-c` options.
- `auto-lint.sh` reports findings on stderr and exits 2 instead of discarding
  them.
