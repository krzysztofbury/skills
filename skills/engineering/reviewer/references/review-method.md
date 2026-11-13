# Review method

How the reviewer judges correctness. Prioritize Safety > Performance >
Developer Experience, using the project's actual requirements and
conventions.

## Proof gate

Refuse to call work "done", "fixed", "verified" or "ready to merge" without a
named artifact that exercises the changed path: a command and its scope, a CI
run URL, a deploy probe, an MCP or API call, or a browser check that shows the
acceptance criterion. None of the following is evidence when treated as proof:

- coverage percentage or test count alone
- source greps for a symbol, import or SQL string
- "tests passed" without naming the command and scope
- a green liveness check while readiness is red (for example `/livez` vs `/healthz`)
- an MCP or API call that never hit the changed path
- a screenshot that does not show the acceptance criterion

State missing evidence instead of inventing it. Never invent file paths,
metrics, test results or project conventions.

## Review

- Inspect the relevant implementation, callers, tests and configuration
  before reporting findings.
- Lead with demonstrated correctness, security, data-loss, concurrency and
  resource risks, then measured performance concerns and maintainability.
- Give file and line, impact, evidence and a grounded fix. Distinguish a
  reproduced failure from a plausible risk. Report no findings when warranted.
- Style preferences become findings only when they violate an adopted project
  rule or explain a concrete maintenance problem.
- When a change ships setup docs or examples, run them literally and probe
  from the client's side (real headers, proxies, default ports). A document
  that claims verification must name what was run.
- Verify libraries and APIs against current official documentation when their
  behavior may have changed.

## Risk-sensitive checks

- Validate external input with runtime errors; assertions are for internal
  invariants and may be disabled by the language or runtime.
- Bound retries, queues, resource growth and external work where exhaustion or
  hangs are possible. Long-running services need cancellation and backpressure.
- Inspect partial failure, cleanup, idempotency and concurrent access where
  relevant. Make defaults explicit when their drift would change the contract.
- Error paths preserve context without leaking secrets or personal data.
  Destructive operations stay within the user's authorized scope.
- For deploy, migration and other state-transition code, walk every mutating
  step through four cases: it fails, it is retried after a failure, it is
  retried after success, and its own recovery fails. Each case needs a
  refusal, an idempotent resume or a test; one gap found means check the rest.
- Optimize proven hot paths and real I/O cost; caches, limits and pagination
  need invalidation and failure behavior. Follow project tooling for
  formatting, lint, types and naming rather than inventing new limits.

## TigerStyle

Apply [the TigerStyle profile](tigerstyle-examples.md) only when the
repository's agent instructions adopt it. Agree on the applicable subset;
recursion bans, assertion quotas and function-size limits are not universal
correctness rules.
