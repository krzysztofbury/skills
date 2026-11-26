---
name: comment-audit
description: Audit code comments so the code speaks for itself - sort each comment into Tautology, Excuse, Stale or Decision Record, delete the first three (filing an issue for the hack each Excuse covers), keep decisions as a one-line `# Why:` or an ADR, and add a ratchet so comments only fall. Use for a comment audit or cleanup, deleting comments, or a no-comments rule.
---

# Comment Audit

A comment is a claim the compiler never checks. Most repeat the code, go
stale, or excuse a hack that then spreads; the few worth keeping record a
decision the code cannot show.

## Scope

Take the scope from the request: the whole repository or a named section.
Audit `#` comments in Python and the equivalent line and block comments in
other languages (SQL, JavaScript and TypeScript, CSS, HTML and Jinja
templates, shell, YAML, TOML); the ratchet counts every language its
baseline enables.

Out of scope, never counted or touched:

- tool pragmas (`noqa`, `type: ignore`, `pragma:`, `pyright:`, `mypy:`,
  `fmt:`, `isort:`, `ruff:`, `nosec`, `pylint:`, `eslint-disable`, `@ts-`,
  `prettier-ignore`, `stylelint-`, `shellcheck`), a shebang, an encoding line;
- script metadata a tool reads (a PEP 723 `# /// script` block);
- docstrings and any text a program reads at runtime, such as tool or CLI
  descriptions, help text and schema descriptions;
- license headers, and vendored or generated files (mark them
  `linguist-vendored` or `linguist-generated` in `.gitattributes` so the
  ratchet skips them too).

## Categorise every comment

| Category | What it is | Action |
|---|---|---|
| Tautology | repeats what the code already shows: the name, the call, the obvious step | delete |
| Stale | describes code, behavior or a plan that is no longer true, including commented-out code | delete |
| Excuse | lets a hack stand: a TODO, FIXME or HACK, "temporary", "workaround", "for now", "should be", "ideally" | delete and file an issue to fix the code it excuses |
| Decision Record | an important, non-obvious reason the code is this way, which the code cannot show | keep as one line, or move to an ADR |

Decide by what the comment does, not by its wording: a `TODO` that records a
deliberate limit with its reason is a Decision Record; a "Why" that excuses a
shortcut is an Excuse. When it reads as both, it is an Excuse: the issue
keeps the reason, and the code gets fixed.

To tell a Tautology from a Decision Record, ask whether the comment says
**what** the code does or **why** it is this way. Saying what the next lines
do, which the names and calls already show, is a Tautology, however wise it
sounds. Giving a reason the code cannot show (`# Sorted first, so the digest
does not depend on dict order.`) or naming which part matters (`# Only the
last retry counts; earlier ones were expected to fail.`) is a Decision
Record, even when it is short.

- In a test, a comment that states the rule the next assertion checks is a
  Tautology: the test's name and assertion carry the rule (rename the test
  when its name does not).
- In a test, a comment that shows how an expected value or a fixture follows
  from the inputs (`# Counting the salary too: 120% of essential cost.`
  above `== 25`) is a Decision Record: the reader cannot derive it from the
  code.
- A comment explaining a workaround that could be avoided (a `sys.path`
  insert where `python -m` would do, hand-cleaning a shared test database)
  is an Excuse.

Record each comment as `path:line - category - one-line reason`. When you
cannot tell whether the reason is still true, check the code and history;
still unsure, keep it and put it on the owner's list.

For more comments than one context holds, follow the `test-audit` skill's
"Labelling at scale" with `audit_inventory.py comments --roots <roots>
--out <dir> [--languages py sql ...]`; give each labeller the section
above and its batch. Every comment it would delete shows in the diff:
check each one before the change lands, since a test comment that shows
how an expected value follows from its inputs is easily misread as a
Tautology.

## Decision Records

- **Local** (one function or line): rewrite it as a single line starting
  `# Why: ` that states the reason, not the action. The ratchet does not
  count it. A second line means it is not local.
- **Cross-cutting** (several modules, a contract, a rejected alternative):
  move it to an ADR in `docs/adr/` (the `domain-modeling` skill's format
  when installed: context, decision, consequences) and leave at most
  `# Why: see docs/adr/NNNN-<title>.md`.

## Excuses

Group Excuses by module and file **one issue per module**: each excused hack
with its location, what the comment admitted, and the goal of fixing the
code so no excuse is needed. State intent, not steps. In a factory run, file
it as the coordinator's intake would; attended, show the owner the list
first.

## Ratchet

Use the `test-audit` skill's `scripts/audit_ratchet.py` (one script counts
both comments and marked tests); its Ratchet section has the setup. After
the deletions, run `update` so the lower count is locked in, and add
`check` to CI if the project does not run it yet.

Also turn on the standard lint rules that catch the same comments where
they are written, since an audit leaves few or no violations: Ruff's `FIX`
(TODO, FIXME, XXX and HACK comments) and `ERA001` (commented-out code); in
a project that uses ESLint, `no-warning-comments`, with ESLint's bulk
suppressions (`--suppress-rule`) for any backlog.

## Project rule

Add or update a short section in the project's `AGENTS.md`, scoped to what
was audited:

```markdown
## Comments

- Let names and structure carry the meaning. A comment is a tool pragma or
  one line starting `# Why: ` that records a non-obvious reason; a reason
  that spans modules goes in `docs/adr/`.
- Name a shortcut in an issue, not a comment; Ruff's `FIX` and `ERA001`
  rules enforce it.
- `scripts/audit_ratchet.py check` runs in CI; after a change that lowers a
  count, run `update` and commit `.agents/audit-baseline.json`.
```

## Report

- counts per category, and the comment lines deleted;
- the estimate for the rest of the scope: lines that would go if every
  remaining non-Decision comment were deleted (`audit_ratchet.py report`
  gives the counts);
- the issues filed and the ADRs written, one line each;
- the owner's list, each with the question that settles it;
- what is not yet audited, and the exact checks run after the change.
