---
name: prompt-tuner
description: Improves a skill, prompt or other repeatable task by bounded experiment - diagnoses real failures, freezes a rubric and held-out cases, changes one thing per round within an agreed budget, and keeps only measured gains. Use for "improve, tune or optimize this skill or prompt", "prove the change helped", "why does this skill keep failing" or autoresearch. Not for one-off edits without measurement.
---

# Prompt Tuner

Tune a skill, prompt or other repeatable task by experiment, not by
intuition: measure a baseline, change one thing at a time, and keep a
change only when frozen criteria on held-out cases say it helped. This is an
autoresearch loop with guardrails against its two usual failures: tuning to
the test set, and spending without limit on a goal that keeps moving.

The subject can be an agent skill, a prompt, a checklist, or any repeatable
task with an observable outcome (a report, a code change, a data
extraction). For skills, harness tooling such as Claude Code's
`skill-creator` can run the test prompts, baselines and viewer; this skill
supplies the design and the stopping rules around those runs.

## Phases

1. **Diagnose** what actually fails, from real evidence.
   See [diagnosis](references/diagnosis.md).
2. **Freeze a rubric** before comparing anything.
   See [rubric](references/rubric.md).
3. **Agree the experiment** with the user before any paid or external call.
4. **Run bounded rounds** and keep a log.
5. **Evaluate once on held-out cases** and hand the decision to the user.

Skip a phase only when its output already exists and the user confirms it
(for example, a rubric from an earlier cycle that still fits).

## 3. Agree the experiment

Write a short plan and wait for approval. It names:

- the subject and its preserved original (a copy, a branch or a commit);
- the dataset, split into development cases and held-out cases. Held-out
  identities and expected outcomes stay out of every tuning step;
- the harness, model, effort, tools and permissions, all fixed for the run;
- the budget: maximum rounds, wall-clock time, and cost or tokens;
- provider and data scope: which models see which data;
- allowed actions. Permission to analyze is not permission to publish, spend
  money, contact people or change production during an experiment;
- regression gates (which failures disqualify a candidate at once) and the
  smallest improvement worth keeping.

If any of these is missing, propose values and wait. Use a finite round cap,
never an open-ended target score: a target invites tuning until noise
crosses it.

## 4. Each round

1. Run the baseline and the candidate on the same development cases in the
   same environment.
2. Make one coherent change tied to a documented failure hypothesis. Several
   changes at once make the result impossible to attribute.
3. Score real outputs with the frozen rubric. Record correctness, severe
   regressions, false findings, user corrections, latency and usage next to
   any subjective judgment. Repeat an ambiguous comparison within the budget
   to see the variance before trusting a difference.
4. Keep or revert by the agreed criteria, and log it either way:

   ```text
   round | hypothesis | change | dev result vs baseline | kept/reverted | reason | cost
   ```

   Reverted candidates belong in the log; they are evidence too.

Stop after two rounds without a meaningful improvement, after a regression
that invalidates the approach, or at any budget cap, whichever comes first.

## 5. Held-out evaluation and handoff

Evaluate the selected candidate on the frozen held-out cases once. For
subjective quality, use a blind comparison where possible: the evaluator
does not know which output came from the candidate. A held-out failure is a
reason to reconsider the candidate, not permission to tune on the held-out
cases; another cycle needs a new approved held-out set.

Report, in this order:

- baseline evidence and the failures that motivated the work;
- the keep/revert log;
- held-out results against the baseline, with costs and variance;
- uncertainties and what the dataset does not cover;
- the candidate diff.

The user decides adoption. One task set does not prove a universal gain, and
a few pilot runs do not prove that unattended automation is safe.

## Never

- Count imagined or simulated outputs as runs, or report results that were
  not executed. Label static inspection separately from executed evidence.
- Spend, publish, message people or touch production beyond what the agreed
  plan allows.
- Look at held-out answers while tuning.

## Beyond skills

For a non-skill task, the same phases apply with the task's own outcome as
the measure. Separate hard correctness gates from subjective quality and
from operational cost, and end with a documented, repeatable procedure:
prerequisites, reproducible commands, rollback, and the cases that still need
human judgment. Propose automation only for validated, explicitly authorized
actions.

Turning lessons from the log into standing rules belongs to a retrospective
(for example the `retro` skill), not to this loop: one experiment is
evidence for a scoped hypothesis, not a permanent instruction.
