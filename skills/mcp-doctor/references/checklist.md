# MCP Tool Catalog Checklist

Each check names its source. Re-check the sources when the specification
version changes; the requirements below match MCP specification 2025-11-25.

Sources:

- **Spec:** MCP specification, server tools,
  https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- **Directory:** Anthropic connector review criteria,
  https://claude.com/docs/connectors/building/review-criteria
- **Builder:** Anthropic `mcp-builder` best practices,
  https://github.com/anthropics/skills/tree/main/skills/mcp-builder
- **Practice:** this skill's own rules, from reviewing servers in use.

## Names

- [ ] 1 to 128 characters; only `A-Z a-z 0-9 _ - .`; no spaces. (Spec, SHOULD)
- [ ] Unique within the server; treated as case-sensitive. (Spec, SHOULD)
- [ ] At most 64 characters. (Directory, required)
- [ ] `snake_case`, verb first (`get_`, `list_`, `search_`, `create_`),
      specific rather than generic. (Builder)
- [ ] A service prefix (`github_create_issue`) when the server is used next
      to others with similar tools. (Builder)

## Title and annotations

- [ ] Every tool has a `title`. (Directory, required)
- [ ] The applicable hint is set: `readOnlyHint: true` on read-only tools,
      `destructiveHint: true` on tools that modify or delete data; Claude
      derives auto-permissions from them. (Directory, required)
- [ ] `idempotentHint` and `openWorldHint` set deliberately. Defaults when
      unset: `readOnlyHint` false, `destructiveHint` true, `idempotentHint`
      false, `openWorldHint` true. (Spec schema, Builder)
- [ ] Hints match behavior: a tool that writes anything is not read-only.
      (Practice)
- [ ] Nothing relies on annotations for security; clients treat them as
      untrusted unless the server is trusted. (Spec, MUST for clients)

## Read and write separation

- [ ] No tool both reads and changes state; documenting the difference in
      the description does not count. (Directory, required)
- [ ] One tool per kind of effect (read, write, delete) when effects differ.
      (Practice)

## Descriptions

- [ ] Opens with a verb and what the tool returns. (Practice)
- [ ] States what the tool does not do and names the sibling tool to use
      instead, in both directions. (Practice, Builder)
- [ ] Output-to-input chains named concretely (which field of which result
      becomes which parameter) and checked against the receiving schema.
      (Practice)
- [ ] States what annotations cannot: remote state changed, what the server
      remembers, limits (date windows, page sizes, rate limits), data the
      caller must not send. (Practice)
- [ ] No instructions to the model ("always", "you must call X first",
      overriding instructions, promotion). (Directory, required; treated as
      prompt injection)
- [ ] A tool that takes free-form API paths or parameters links the target
      API's documentation. (Directory, required)
- [ ] Accurate: matches what the tool actually does today. (Builder)
- [ ] Within the per-description byte budget. (Practice)

## Input schema

- [ ] A valid JSON Schema object, never `null`. (Spec, MUST)
- [ ] A tool without parameters uses
      `{"type": "object", "additionalProperties": false}`. (Spec, recommended)
- [ ] Every property has a description. (Practice, Builder; directories
      score coverage)
- [ ] Tight types: enums for choices, `minimum`/`maximum` and defaults for
      numbers, patterns for IDs, defaults stated for optional inputs.
      (Practice)
- [ ] For free-form values, a description with an example works better than
      an enum that cannot list every case. (Practice)
- [ ] The server validates every input regardless of the schema: sizes,
      ranges, paths (no traversal), URLs, no command injection. (Spec, MUST
      validate; Builder)

## Output

- [ ] Results include the IDs a follow-up call needs. (Practice)
- [ ] Writes return a short confirmation with the created or changed ID,
      never a bare "ok". (Practice)
- [ ] Structured data as JSON; with an `outputSchema`, `structuredContent`
      conforms to it. (Spec, MUST when an output schema is declared)
- [ ] `structuredContent` is also serialized into a text block for older
      clients. (Spec, SHOULD)
- [ ] No raw HTML or unfiltered API dumps. (Practice)
- [ ] Large payloads as a `resource_link`; small, always-needed ones
      embedded. (Practice)
- [ ] Outputs sanitized. (Spec, MUST)

## Size and pagination

- [ ] List tools accept `limit` and return a cursor or offset, `has_more`
      and, when cheap, a total. (Builder)
- [ ] Default page of about 20 to 50 items; never load everything into
      memory. (Builder)
- [ ] Truncation is stated with a way to narrow the query ("Showing 10 of
      847; add a date filter"). (Practice)
- [ ] `tools/list` itself paginates for very large catalogs. (Spec)

## Errors

- [ ] Execution failures (API errors, invalid input values, business rules)
      return a result with `isError: true`. (Spec)
- [ ] Protocol errors (JSON-RPC) only for unknown tools, malformed requests
      and server faults. (Spec)
- [ ] Every error message says what to do next. (Spec intent, Practice)
- [ ] No stack traces, internal paths or secrets in errors. (Builder)
- [ ] No generic errors ("Internal Server Error", "Bad Request" without
      detail); every tool succeeds with valid parameters. (Directory,
      required)

## Catalog

- [ ] Total catalog within its byte budget; tool count justified (about 15
      dedicated tools is comfortable, beyond about 30 consider
      search-plus-execute). (Practice, `mcp-server-dev` plugin)
- [ ] No near-duplicate tools an agent cannot tell apart. (Practice)
- [ ] `serverInfo` matches `server.json`. (Practice, Registry)
- [ ] The server declares the `tools` capability, and `listChanged` only if
      it emits the notification. (Spec, MUST)

## Data and scope (Directory)

- [ ] Responses sized to the request; no full dumps when a summary was asked.
- [ ] No collection of conversation data beyond what the tool needs; no
      queries into the client's memory, chat history or user files.
- [ ] The server calls its own first-party APIs or ones it legitimately
      proxies.

## Server security (from the specification)

- [ ] Access control on every tool; rate limits on invocations. (Spec, MUST)
- [ ] Sensitive operations are separate tools so clients can ask the user
      for confirmation. (Spec intent for clients, Practice)
