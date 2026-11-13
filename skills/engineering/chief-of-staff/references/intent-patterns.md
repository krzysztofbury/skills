# Intent patterns

Patterns for stating intent instead of steps: the effect expected, how to
tell it is met, and why. Adapted from Sebastian Gebski's "magic lamp" series
(no-kill-switch.ghost.io). Pick one per situation; do not stack them.

## Input: shaping an issue

| Pattern | Use for |
|---|---|
| Context -> Goal (with examples of done) -> Why -> Constraints -> Anti-goals -> Ask | most features and changes |
| Facts + Assumptions + Constraints + Unknowns + Goal exit criteria + Ask | work with open questions; the unknowns become questions to settle first |
| State -> Delta -> Attempted -> Blocker | a stuck piece of work handed on |
| Invariants + Variables -> Optimization metric | tuning, performance, cost |

Every issue needs a check that says when it is done. Examples of done beat
adjectives: "`paginate([1,2,3], 2)` returns `[[1,2],[3]]`", not "pagination
works".

## Process: how a role works

| Pattern | Use for |
|---|---|
| Decompose -> Resolve dependencies -> Synthesize | a feature too large for one change; produces `Blocked by #N` issues |
| Step back -> Identify principles -> Apply them | a fix that keeps coming back |
| Diverge -> Evaluate -> Converge | a design choice with several plausible options |
| Hypotheses -> Discriminating evidence -> Tests | a bug or an unexplained failure |

## Output: shaping a report

| Pattern | Use for |
|---|---|
| State -> Delta -> Attempted -> Blocker | `STATUS: BLOCKED` comments |
| Context -> Decision drivers -> Options considered -> Decision -> Consequences | `ESCALATE` and other decisions the owner must make |
| Diagnosis -> Guiding policy -> Coherent actions | a plan or a retro finding |
| Before -> After -> Bridge | a pull request body |
| Point -> Reason -> Example -> Point | a short argument in a review |
