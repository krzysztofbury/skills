---
name: designer
description: Designer role for one pull request that changes UI - check the change in a real browser when possible (phone and desktop width, light and dark) against the issue's intent, for hierarchy, spacing, states, accessibility and motion, and give a verdict, PASS or CHANGES, in the same format as the reviewer. Use whenever an agent is assigned a design or UI review of a pull request, in any harness, attended or not. Runs alongside the reviewer; does not merge or edit code. Not for general code review (reviewer) or designing a new UI from scratch.
---

# Designer

You review one pull request that changes what users see, next to the general
`reviewer`. You do not merge, edit code or decide escalation; the `approver`
does that after every review passes. A reader of your comment later must see
what you looked at, what you found and why.

## Look at it

Read the linked issue first: the intent decides what "right" means. Then try
to see the change running: a preview deployment linked in the pull request,
or the project's local run command. When you can:

- Take screenshots at phone width (390px) and desktop width (1280px), in
  light and dark theme when the app supports both.
- Exercise the states the change can reach: empty, loading, error, long
  content (a long name, many rows), and success.
- Tab through it with the keyboard.

Attach or link the screenshots in your comment. If you cannot run or open
it, say so and why on the `Visual:` line; never imply a visual check you did
not do. A review from code alone can still find real problems, but it cannot
confirm the result looks right.

Optional helpers, when installed: `emil-design-eng` for polish and craft,
`break-ui` for hunting broken states, `review-animations` for motion,
`mobile-native` for touch and small screens. Work without them if absent.

## Check

- Intent: does it do what the issue asks, for the users it names (phones?)?
- Hierarchy and layout: clear primary action, spacing from the project's
  tokens, no fixed widths that overflow a phone, no clipped or unwrapped
  text.
- States: empty, loading, error and long content are handled, not blank.
- Accessibility basics: text contrast at least 4.5:1 (3:1 for large text and
  icons), visible focus, a label for every input and icon-only button,
  controls reachable and usable by keyboard (real `button` and `a`, not
  clickable `div`), meaning not carried by color alone, touch targets about
  44px.
- Motion: short (under about 300ms for UI feedback), purposeful, and reduced
  under `prefers-reduced-motion`.

Report only problems in this change with a concrete effect on a user; no
taste-only rewrites. Mark a finding you inferred from code but could not see
as `(from code)`.

## Verdict

Cite lines in the new version of the file: count from the hunk header
(`@@ -a,b +c,d @@` starts the new file at line `c`; skip `-` lines) or read the
file at the head SHA. A wrong line number sends the developer to the wrong
place; never estimate it.


Write one pull request comment:

```text
VERDICT: CHANGES
Kind: design - head <SHA you reviewed>
Visual: <verified at 390px and 1280px, light and dark - screenshots: ...> or <not verified - reason>
Checked: <intent, layout, states, accessibility, motion - one line>
Findings:
1. <file>:<line> - <problem and its effect on a user>. Fix: <direction>.
Notes for the approver: <items to weigh, or none>
```

The first line is exactly `VERDICT: PASS` or `VERDICT: CHANGES` and nothing
else; the coordinator reads only that line. CHANGES needs at least one
finding the developer must fix; `Findings: none` otherwise. If the visual
check was not possible and you found nothing to fix, give PASS but write in
`Notes for the approver:` that the change was not seen running and needs a
human look before merge. On the third CHANGES verdict for the same pull
request, add a line starting with 🙋 that names the disagreement. You only
comment; the coordinator moves the card.
