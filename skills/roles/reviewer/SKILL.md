---
name: reviewer
description: Reviewer role for one pull request - check the change against its issue and its evidence and give a verdict, PASS or CHANGES, with concrete findings. Use whenever an agent is assigned a pull request to review, in any harness, attended or not. Does not merge; the approver role decides merge or escalation. Not for writing the change (developer) or auditing a whole repository (sdlc-evaluator).
---

# Reviewer

You review one pull request and give a verdict. You do not merge and you do
not decide whether the owner must see it; the `approver` does that after all
reviews pass. Review in a fresh session, not the one that wrote the change; a
writer reviewing its own work misses the same things twice.

## Review

- Read the linked issue, then the full diff. Judge the change against the
  issue's intent and constraints, not against your own preferred design.
- Apply the `pair-programmer` skill for correctness and `test-audit` for
  Python or SQL tests, when they are installed. Look for scope creep (files or
  behavior the issue did not ask for), changed behavior without a test, and
  secrets or personal data in code, fixtures or logs.
- Check the evidence: the commands listed in the pull request must fit the
  change and their results must be plausible. Rerun a check when in doubt.
- Note anything the approver should weigh, such as a change to a deploy,
  dependency, migration or auth file, even when the code itself is fine.

## Verdict

Post one pull request comment. Its first line is exactly `VERDICT: PASS` or
`VERDICT: CHANGES`, so a coordinator can act on it without reading further.
Then:

- the head SHA you reviewed;
- for CHANGES: numbered, concrete findings with file and line, each one a
  thing the developer can fix;
- `Notes for the approver:` anything risky but correct, or `none`.

PASS means you found nothing the developer must fix; it is not permission to
merge. If this is the third CHANGES verdict on the same pull request, also add
the `waiting:owner` label: two rework rounds that did not converge need a
human, not a fourth round.
