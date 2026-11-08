# Rubric

Turn the user's acceptance criteria into a compact rubric, reusing the
diagnosis evidence, and freeze it before comparing candidates.

1. Separate hard requirements, unacceptable failures and subjective
   preferences.
2. Use pass/fail checks for observable requirements, one behavior per check.
   Use anchored ratings or a human comparison for qualities such as clarity.
   Give each criterion a severity, so a critical regression cannot hide in an
   average score.
3. Apply the draft rubric to real outputs, including a failure and a sound
   output. Record disagreements and ambiguous criteria, and revise the
   criterion rather than claiming the subjective judgment has gone away.
4. Keep only criteria that discriminate. There is no right number of checks,
   and a longer checklist does not prevent score gaming.
5. Freeze the rubric before the first candidate comparison. Keep held-out
   case identities and expected outcomes out of every tuning step.

Output, one row per criterion:

```text
criterion | scoring (pass/fail, anchored 1-5, human comparison) | severity | evidence required | pass example | fail example
```

State which decisions still need human review.
