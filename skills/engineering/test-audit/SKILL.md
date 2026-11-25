---
name: test-audit
description: Audit a project's tests so each one earns its place - sort every test into Business, Stale, Coverage Assert or Failsafe, delete the stale ones, mark the rest for replacement with an issue, and add a ratchet so marked tests only fall. Also the bar for a good Python or SQL test. Use for a test audit or pruning, categorising tests, or writing, changing or reviewing a test.
---

# Test Audit

A test earns its place when a plausible wrong change makes it fail for the
reason it exists. Writing a test and keeping one meet the same bar:
[test proof](references/test-proof.md) holds the authoring gate, the
low-value patterns and the Python and SQL proof choices. When you are only
writing or reviewing a test, that file is all you need; the rest of this
skill is the audit.

## Scope

Take the scope from the request: the whole repository or a named section
(a package, a module, a test directory). Read the repository's `AGENTS.md`
(or `CLAUDE.md`), its test configuration (`testpaths`, markers, CI test
commands) and the production code each test exercises. A test outside the
configured test paths that never runs is Stale by definition.

## Categorise every test

Answer three questions for each test, in order; the first "no" decides.

1. **Does the behavior it names still exist and matter?** No: **Stale**. It
   references removed code, a retired rule, or a seam kept alive only by
   tests.
2. **Can you name a plausible wrong change, beyond a typo the linter or type
   checker already catches, that makes it fail for its intended reason?** No:
   **Coverage Assert**. It restates code that is obvious on reading it: a
   default, a constant, a getter, a mirror of the implementation.
3. **Is the asserted outcome produced by the real code path?** No:
   **Failsafe**. It reassures the owner or an agent that the work runs
   without checking the result: no assertion or only "no exception", a mock
   that supplies the asserted value, expected output built by the code under
   test, a self-comparison.

Otherwise it is a **Business Test**: it guards an important, non-obvious
decision or contract at an owning boundary (an API, CLI or tool result,
persisted rows, a migration, a security or platform rule).

Record each test as `path::name - category - one-line reason`, the reason
naming the wrong change it catches or why none exists. When two categories
fit, or you cannot name the contract, mark it **uncertain**, keep it, and put
it on the owner's list: a wrong keep costs one more look, a wrong delete
loses proof.

## Act on each category

| Category | Action |
|---|---|
| Stale | delete it, with any production seam only it used, in this change |
| Coverage Assert, Failsafe | mark it `@pytest.mark.to_delete(issue=N)` and file the issue below |
| Business Test | keep it unchanged |

A failing Stale candidate may be a product bug: investigate before deleting.
Group marked tests by the production module they exercise and file **one
issue per module**: which tests, their category and reason, and the goal,
which is to make the code clear enough not to need them or to cover the real
behavior at the owning boundary, then delete the marked tests and lower the
baseline. State intent, not steps. In a factory run, file it as the
coordinator's intake would; attended, show the owner the list first.

Register the marker so strict marker checks pass, for example in
`pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = ["to_delete(issue): marked by a test audit for replacement; see the issue"]
```

Marked tests keep running until their issue replaces them.

## Ratchet

Not every test is audited in one change, so lock in progress instead of
finishing it. [`scripts/audit_ratchet.py`](scripts/audit_ratchet.py) counts
`to_delete` markers (and comments, for `comment-audit`) per file against a
committed baseline; both counts may only fall.

1. Copy it to the project as `scripts/audit_ratchet.py`. If the project
   already has it, compare it with this copy and take the newer one.
2. Run `python scripts/audit_ratchet.py init --roots <source and test roots>`
   once; afterwards `update` after every change that lowers a count.
3. Add `python scripts/audit_ratchet.py check` to CI next to the tests. It
   fails when a count rises, or falls without the baseline lowered.

## Project rule

Add or update a short section in the project's `AGENTS.md`, scoped to what
was audited:

```markdown
## Tests

- A test earns its place when a plausible wrong change makes it fail for the
  reason it exists; follow the `test-audit` skill's test proof.
- Write Business Tests at the owning boundary. Never add a `to_delete`
  marker; a marked test goes when its issue is done.
- `scripts/audit_ratchet.py check` runs in CI; after a change that lowers a
  count, run `update` and commit `.agents/audit-baseline.json`.
```

## Report

- counts per category, with tests and lines for each;
- lines deleted now (Stale) and lines that go when the issues close (marked);
- the issues filed, one line each;
- the uncertain list for the owner, each with the question that settles it;
- what is not yet audited, so the next run starts there;
- the exact test command run after the deletions, and its result.
