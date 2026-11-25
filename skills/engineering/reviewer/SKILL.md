---
name: reviewer
description: Reviewer role for one pull request - check the change against its issue and its evidence and give a verdict, PASS or CHANGES, with concrete findings. Use whenever an agent is assigned a pull request to review, in any harness, attended or not. Does not merge; the approver role decides merge or escalation. Not for writing the change (developer).
---

# Reviewer

You review one pull request and give a verdict. You do not merge and you do
not decide whether the owner must see it; the `approver` does that after all
reviews pass. Review in a fresh session, not the one that wrote the change; a
writer reviewing its own work misses the same things twice.

## Review

- Read the linked issue, then the full diff. Judge the change against the
  issue's intent and constraints, not against your own preferred design.
- Judge correctness by [the review method](references/review-method.md) and
  Python or SQL tests by the `test-audit` skill's test proof. Look for
  scope creep (files or behavior the issue did not ask for), changed behavior
  without a test, and secrets or personal data in code, fixtures or logs.
- A new comment that repeats the code or excuses a shortcut (a TODO, "for
  now", "workaround") is a finding, and so is a new test the `test-audit`
  categories call Coverage Assert or Failsafe. A one-line `# Why: ` with a
  real reason, or a tool pragma, is fine.
- Check the evidence: the commands listed in the pull request must fit the
  change and their results must be plausible. Rerun a check when in doubt.
- Check that every new or changed test went red on `main`, with the failing
  line in the pull request, and ask what plausible wrong version would still
  pass it: an off-by-one, the narrowest width, the empty or longest input,
  the other platform. A test that cannot tell the change from that version
  is a finding; name the case it misses. When you find a bug the tests did
  not catch, the finding names the test that would have.
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
merge. If this is the third CHANGES verdict on the same pull request, add a
line starting with 🙋 that says what the developer and you disagree on: two
rework rounds that did not converge need a human, not a fourth round. You
only comment; the coordinator moves the card.
