---
name: mcp-doctor
description: Review, score and fix the tool catalog of an existing MCP server - tool names, titles, descriptions, input and output schemas, annotations, errors and result sizes - when agents pick the wrong tool or call it with bad arguments, or before publishing to the MCP Registry, the Anthropic Directory or a directory such as Glama. Not for building a server from scratch.
---

# MCP Doctor

Agents choose a tool from the catalog alone: its name, title, description and
schemas. This skill examines that catalog as the agent sees it, scores it
against the MCP specification and the established practice below, and turns
the findings into fixes held by tests. A directory score is a check, not the
goal.

## Scope

Use it for a server that exists, even a draft: a review, a directory or
registry submission, or an agent that keeps choosing the wrong tool.

To build a server from scratch, use an established builder skill instead,
then come back here before release:

- Anthropic's `mcp-builder` (github.com/anthropics/skills): research, Python
  and TypeScript implementation, and an evaluation harness. It is a plain
  Agent Skill, so Codex and OpenCode can use it too.
- In Claude Code, the `mcp-server-dev` plugin (`build-mcp-server`,
  `build-mcp-app`, `build-mcpb`): deployment model, scaffolds, auth and
  packaging.

## Procedure

1. **Get the real catalog.** List it through an MCP client (`tools/list`,
   following `nextCursor`), not from the source code: decorators, schema
   generators and SDK defaults change what the agent receives. Record the
   server version and the total catalog size in bytes.
2. **Check every tool** against [the checklist](references/checklist.md).
   Each check states its source: the specification (MUST/SHOULD), a directory
   requirement, or practice. Mark a finding as a spec violation, a directory
   blocker or a recommendation, never one for another.
3. **Check the chains.** For every place where one tool's output feeds
   another tool's input, confirm the field name, format and type match what
   the second schema accepts. A description that leads to an input the
   schema rejects is worse than no description.
4. **Exercise it.** Call each read-only tool with valid input, a malformed
   input and an out-of-range input, and read the actual results and errors.
   Do not call write or destructive tools without the owner's approval and a
   safe target.
5. **Score and report** in the format below. Propose fixes as a diff to the
   definitions, plus the tests that hold them.
6. **Measure what matters** when tool choice is the problem: an evaluation
   of realistic questions (see Evaluation) shows whether a change helps
   agents, which a directory score does not.

## The checks in brief

The [checklist](references/checklist.md) has the full list with sources.

- **Names:** 1 to 128 characters of `A-Za-z0-9_-.`, unique, case-sensitive
  (spec); at most 64 characters for the Anthropic Directory. Prefer
  `snake_case`, a verb first and a service prefix when the server shares a
  client with others.
- **Title and annotations:** every tool has a `title` and deliberate
  `readOnlyHint`, `destructiveHint`, `idempotentHint` and `openWorldHint`.
  Unset hints mean the worst case (`destructiveHint` and `openWorldHint`
  default to true). Clients treat annotations from untrusted servers as
  untrusted: they shape the UI, not security.
- **Read and write apart:** a tool that both reads and changes state cannot
  carry an honest `readOnlyHint`; split it.
- **Descriptions:** open with a verb and what the tool returns; say what it
  does not do and name the sibling to use instead; state what annotations
  cannot (remote state changed, what the server remembers, limits such as
  date windows or page sizes, data the caller must not send). Never instruct
  the model how to behave ("always call X first"); directories reject that
  as prompt injection.
- **Inputs:** every property has a description; tight types (enums, ranges,
  patterns, defaults); a tool without parameters declares
  `{"type": "object", "additionalProperties": false}`.
- **Outputs:** IDs the next call needs; a short confirmation with an ID for
  writes; JSON for structured data, with `outputSchema` and
  `structuredContent` plus the same JSON as text for clients that ignore it.
- **Size:** paginate lists (`limit`, a cursor or offset, `has_more`), default
  to 20 to 50 items, and say when a result was truncated and how to narrow it.
- **Errors:** execution failures come back as results with `isError: true`
  and a next step ("Item 42 not found; use search_items"); protocol errors
  only for unknown tools and malformed requests. No stack traces or internals.
- **Catalog budget:** keep descriptions short and hold the whole catalog to a
  byte budget with a test. Without a project budget, start at 200 to 400
  bytes per description and tool count times 400 in total. Past about 30
  tools, consider search-plus-execute or merging near-duplicates.

## Report format

Per tool, then for the catalog:

```text
tool_name  [spec: n violations] [directory: n blockers] [practice: n]
  - <finding> (<source>) -> <fix>
Catalog: <tools>, <bytes>, chains checked <n>/<n>, evaluation <score or "not run">
```

Lead with spec violations and directory blockers. When the owner targets a
directory, name it and check its current requirements; they change.

## Evaluation

For tool-choice problems, run a small evaluation instead of arguing from the
catalog: about ten realistic, read-only, independent questions, each with
one stable, verifiable answer (a name, ID, date or number) that needs several
tool calls. Run them through the agent, compare accuracy, calls per task and
the agent's own complaints about the tools before and after the change.
Anthropic's `mcp-builder` includes a harness and the question rules. A
higher directory score without a better evaluation is not an improvement.

## Python SDK and Pydantic traps

- A PEP 695 `type X = Annotated[..., Field(description=...)]` alias becomes a
  `$ref`, and the description disappears where it is used. Use a plain
  assignment alias, or put the description in `WithJsonSchema`.
- A shared alias needs a description that is true at every use.
- Check the generated schema, not the model class: list the catalog through
  a client and assert on what it returns.

## Registry and directories

- Give the server `serverInfo` (name, version, title, website URL, icons)
  that agrees with `server.json`, and test that they match.
- Validate `server.json` in CI with a pinned, signature-verified
  `mcp-publisher`. Publishing and namespace proof (DNS TXT or GitHub) are
  owner steps.
- Registry versions are immutable: run every check before the first publish.
  A missing icon or description costs a version.
- Glama indexes the Registry and GitHub and scores tool definitions (TDQS) on
  Purpose, Usage, Behavior, Parameters, Conciseness and Completeness, from an
  image it builds itself. Check its build spec in the admin pages; its
  inferred defaults can be wrong.
- The Anthropic Directory review adds hard requirements: a `title` and the
  applicable hint on every tool (`readOnlyHint` on reads, `destructiveHint`
  on writes), names of at most 64 characters, read and write split, no
  behavioral instructions, documentation links for tools that take free API
  paths, actionable errors and reasonably sized responses. The checklist
  links the current page.

## Tests that hold the line

An integration test lists the catalog through the MCP client and asserts:

- every tool has a title and deliberate annotations;
- every input property has a description;
- names match the allowed characters and length;
- each description of an overlapping tool names its sibling;
- the catalog stays within its byte budget;
- `serverInfo` equals `server.json`.

## Suggested repository layout

- The server module with descriptions and schemas next to the handlers.
- The catalog integration test above.
- `server.json` at the repository root, validated in CI.
- A tool contract document (for example `MCP_CONTRACT.md`) stating each
  tool's inputs, outputs, side effects and sibling tools.
- A distribution document (for example `DISTRIBUTION.md`) recording
  directory build specs and the publish checklist.
