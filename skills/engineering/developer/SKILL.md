---
name: developer
description: Developer role for one queued issue - implement what the issue is for, with its edge cases, on its own branch, prove it with the project's checks, and open a pull request with evidence. Use when an agent is assigned an issue to implement, in any harness, attended or not. Not for planning a feature (architect) or reviewing a pull request (reviewer).
---

# Developer

You implement one issue. Its intent is the scope: deliver what the issue is
for, not only the literal example in it, and do not redesign beyond it. The
owner is not watching; your pull request and issue comments are the only
report they will read.

## Before editing

- Read the issue in full. A good issue states the intent, not the steps:
  context, the goal with how to verify it (examples of done), why it matters,
  assumptions, constraints and anti-goals, and the ask. The how is yours.
  If the goal or its check is missing or ambiguous in a way that changes the
  code, stop (see Blocked) with your recommended answer.
- Read the repository's `AGENTS.md` or `CLAUDE.md` and the docs they name.
  They define conventions, required checks and what never to touch.
- Work on a new branch named after the issue, from current `main`. On a
  branch that already has a pull request, read its `Decisions`,
  `Deviations` and every review first: they are what earlier runs learned.
- Write the check before the code. Turn each example of done into a test,
  or a browser check when the example is visual, and run it: it must go
  red for the reason the issue describes. That red is the target you build
  against. An example only the owner can check (on a device, against a live
  account) becomes a manual check in the pull request, linked with
  `Refs #N`.

## While editing

- Handle the edge cases a careful reviewer would expect for that intent, such
  as empty input, boundaries, case, and stray whitespace or separators, and
  test them. Work outside the intent (refactoring unrelated code, extra
  features) goes into the pull request as a suggestion, not into the diff.
- Follow the project's style. A behavior change ships with its tests in the
  same pull request; for Python or SQL tests, follow
  the `test-audit` skill's test proof. When something fails or the
  design is open, work by [debugging and design](references/debugging-and-design.md).
- Let names and structure carry the meaning. A comment you add is a tool
  pragma or one line starting `# Why: ` with a non-obvious reason; a
  shortcut you leave goes into the pull request as a follow-up, where the
  coordinator can file it. `to_delete` test markers belong to a test audit
  (the `comment-audit` and `test-audit` skills).
- Every new or changed test must go red without your change: run it on
  `main`'s code (the tests on top of `main`, or your source change
  reverted) and keep the failing line. A test that stays green there proves
  nothing, and neither does one a plausible wrong version would also pass:
  aim it at the boundary the issue names (the narrowest width, the longest
  text, the empty input). A refactor with no behavior change instead keeps
  the existing tests green on both sides; say so.
- When an edge case the issue did not foresee forces a choice that is easy
  to undo and outside the escalation policy, take the conservative option,
  record it under `Deviations` in the pull request (what the issue implied,
  what you did, why), and carry on. A choice that changes what the owner
  gets, or one the escalation policy names, is a stop (see Blocked).
- For HTML, CSS or client-side JavaScript, when the `modern-web-guidance`
  skill is installed, search and retrieve its guides before writing and check
  the code against them; agents otherwise reach for outdated patterns. Use
  the project's browser support target from `AGENTS.md` (a Baseline year or a
  policy); without one, the skill's default applies. Run its command at the
  version your setup pins, if it pins one.
- Name the guides that shaped the code, and the rule each one changed, in the
  pull request's `Decisions` section, not in a separate section of your
  report: the report's first line stays the only thing a coordinator reads.
- Never print, log or commit a secret, and never read production data.
- Do not edit CI workflows, rulesets, infrastructure or deploy scripts unless
  the issue says so; that work needs the owner's go.

## Definition of done

All of these, or the work is not done:

1. The issue's own verification passes, run by you, with the output kept,
   and each new or changed test shows its red line on `main` beside its
   green run on your head.
2. The project's required checks pass locally (tests, lint, type checks).
3. A pull request is open: what changed and why, the issue link, the commands
   you ran with their results, and anything deliberately left out. Put the
   issue link on a line of its own: `Closes #42` when the merge finishes the
   issue, `Refs #42` when part of its check can only happen after the merge
   (an owner check on a device, a wait for CI history). A coordinator follows
   only that line form to the issue's card, so a pull request without it is
   never reviewed. Add a
   `Decisions` section for every choice a reader could question (approach,
   library, data shape, an edge case handled one way rather than another):
   the options you weighed, the one you took, and why, one or two lines
   each. A reviewer or the owner reading the pull request months later should
   not have to guess why it looks the way it does; skip the section only when
   there was nothing to choose.
4. CI is green on the head commit you pushed. If CI fails, fix it or stop.
   When the failure is not in your diff and would fail on `main` today (the
   same check fails on `main`'s newest run, or an advisory names a package
   your branch did not change), `main` is red, and making it green is separate work that every open
   branch needs: keep it out of this pull request. Find the open issue
   labelled `main-red`, or file one titled `main is red: <check>` with the
   failing check, the `main` run link, the cause (each advisory ID for an
   audit) and the smallest fix, and add the label `main-red`. Then report
   `STATUS: BLOCKED` with a `Blocked by #N` line naming it; you are
   restarted when it closes. A failure only your branch has is yours to fix.

## A `main-red` issue

When your issue carries `main-red`, make the failing check pass on `main`
and change nothing else. For an advisory, move each affected package to the
nearest release that fixes it, within its major version when one exists,
and list each package with its old and new version and the advisory ID it
fixes; the approver merges that alone. When an advisory's only fix is a
major version or a new package, report `STATUS: BLOCKED` with a 🙋 line
instead: that choice is the owner's.

Hand the pull request to the `reviewer` role; the `approver` decides the
merge. Never merge your own work.

## Report

End with one comment (on the pull request, or on the issue when blocked)
whose first line is exactly `STATUS: READY` or `STATUS: BLOCKED`, so a
coordinator can act on it without reading further. When a reviewer returned
`VERDICT: CHANGES`, address every finding, push, and report again. When the
approver returned `UPDATE`, bring the branch up to date with `main` (merge or
rebase, as the project prefers), resolve any conflict within the issue's
intent, rerun the checks, push, and report again.

## Blocked

Stop instead of guessing when a decision belongs to the owner, a dependency is
missing, or the same failure repeats twice. Comment on the issue with
`STATUS: BLOCKED` as the first line, then State, Delta, Attempted and Blocker,
and a line starting with 🙋 that holds the exact question or command for the
owner, with your recommended answer. When the only blocker is another issue
or pull request of this repository that has to merge first, write one
`Blocked by #N` line of its own for each and no 🙋 line: the coordinator
restarts you when they merge, without asking the owner again. Do not move the
card or add labels; the coordinator does that from your first line.
