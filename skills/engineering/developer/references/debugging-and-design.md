# Debugging and design

How the developer finds a cause and chooses a design. Prioritize Safety >
Performance > Developer Experience, using the project's actual requirements
and conventions.

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

## Debugging and design

- Gather the error, reproduction conditions and relevant code. Test a
  falsifiable hypothesis against the error, trace or reproduction before
  changing anything; then make the smallest correct change when authorized.
- Add a regression test when it protects the failing behavior. For Python or SQL
  tests, follow [test-audit.md](test-audit.md).
- For design, establish the workload, failure modes and constraints from code
  and user context; do not assume the stack, scale, latency target or data
  sensitivity. Explain decisive safety, cost and complexity trade-offs. Prefer
  a reversible first step and state the conditions that justify a more complex
  design.
- Validate the changed runtime path and relevant project checks. Do not keep
  broadening checks after the acceptance criteria pass.

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
