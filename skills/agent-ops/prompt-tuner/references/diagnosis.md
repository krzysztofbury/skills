# Diagnosis

Find out what fails before changing anything. Most failed improvement loops
fixed a problem nobody measured.

1. Collect the subject (skill, prompt or task definition), its intended
   boundaries, and real transcripts or outputs where they exist.
2. Propose a small dataset that covers normal tasks, edge cases and, for a
   skill, requests that should not trigger it. Agree on inputs, the provider
   and data scope, and a run, time and cost budget before any model call.
3. Run the unchanged subject as a baseline in the actual harness, or score
   existing runs whose conditions are known. Record model, effort, tools,
   permissions and the source snapshot (commit or copy). Label static
   inspection separately from executed evidence.
4. Rank observed failures by impact and frequency. Cite the input, the
   output and the requirement each one violates. Separate likely causes from
   demonstrated ones, and list competing explanations.
5. Report coverage gaps and how sure the evaluation is. A small smoke sample
   does not establish every failure pattern or model-wide behavior.

Output: baseline evidence, ranked failures with citations, competing
explanations, and a focused next experiment. Never invent outputs or run
results.
