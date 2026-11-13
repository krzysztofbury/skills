'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const net = require('node:net');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const { DatabaseSync } = require('node:sqlite');

const {
  agentsFromTerminals,
  compactNumber,
  coreSocketPath,
  fetchCodexQuota,
  highestPriorityAgent,
  normalizeQuota,
  queryActivity,
  reconcileAgentSlots,
  renderQuota,
  renderPulse,
  renderSession,
  requestCore,
} = require('../plugin');

function decodeSvg(dataUri) {
  return Buffer.from(dataUri.split(',')[1], 'base64').toString('utf8');
}

function terminal(address, state, extra = {}) {
  return {
    address,
    state: 'live',
    parent: null,
    status: state ? { app: 'claude-code', state } : null,
    labels: { where: `DEV / ${address}-tab` },
    created_ms: Number(address.slice(1)),
    status_ms: 0,
    ...extra,
  };
}

test('keeps existing agents in stable slots and fills gaps in start order', () => {
  const agents = agentsFromTerminals({ terminals: [terminal('t9', 'idle'), terminal('t1', 'idle'), terminal('t3', 'idle')] });
  assert.deepEqual(reconcileAgentSlots(agents, ['t3', null, 'missing', null]), ['t3', 't1', 't9', null]);
});

test('an agent is a live root terminal that reports a status', () => {
  const agents = agentsFromTerminals({
    terminals: [
      terminal('t1', 'working'),
      terminal('t2', null),
      terminal('t3', 'idle', { state: 'finished' }),
      terminal('t4', 'blocked', { parent: 't1' }),
      terminal('t5', 'thinking'),
    ],
  });
  assert.deepEqual(agents.map((agent) => [agent.address, agent.agent_status]), [['t1', 'working'], ['t5', 'unknown']]);
});

test('labels come from the Herdr app space and tab, with fallbacks', () => {
  const [labelled, named, bare] = agentsFromTerminals({
    terminals: [
      terminal('t1', 'idle', { labels: { where: 'PRIV / fix / login' } }),
      terminal('t2', 'idle', { labels: {}, name: 'review' }),
      terminal('t3', 'idle', { labels: {}, status: { state: 'idle' }, foreground: { name: 'pi' } }),
    ],
  });
  assert.deepEqual([labelled.space, labelled.displayLabel], ['PRIV', 'fix / login']);
  assert.deepEqual([named.space, named.displayLabel], ['', 'review']);
  assert.equal(bare.displayLabel, 'pi');
  assert.match(decodeSvg(renderSession(labelled, true)), /PRIV \| t1/);
});

test('selects blocked or error, then done, then working agents for attention', () => {
  const agents = agentsFromTerminals({
    terminals: [
      terminal('t1', 'working', { status_ms: 9 }),
      terminal('t2', 'done', { status_ms: 2 }),
      terminal('t3', 'error', { status_ms: 1 }),
    ],
  });
  assert.equal(highestPriorityAgent(agents).address, 't3');
  assert.equal(highestPriorityAgent(agents.slice(0, 2)).address, 't2');
  assert.match(decodeSvg(renderPulse(agents, true)), /1 BLOCKED/);
});

test('finds the herdr-core socket', () => {
  assert.equal(coreSocketPath({ HC_SOCKET: '/x/hc.sock', XDG_RUNTIME_DIR: '/run/user/7' }), '/x/hc.sock');
  assert.equal(coreSocketPath({ XDG_RUNTIME_DIR: '/run/user/7' }), '/run/user/7/herdr-core/default.sock');
});

test('sends JSON-RPC 2.0 requests to the herdr-core socket', async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'opendeck-herdr-core-'));
  const socketPath = path.join(directory, 'default.sock');
  const server = net.createServer((socket) => {
    socket.once('data', (data) => {
      const request = JSON.parse(data.toString().trim());
      assert.equal(request.jsonrpc, '2.0');
      if (request.method === 'terminal.list') {
        socket.end(`${JSON.stringify({ jsonrpc: '2.0', id: request.id, result: { terminals: [] } })}\n`);
      } else {
        socket.end(`${JSON.stringify({ jsonrpc: '2.0', id: request.id, error: { code: -32601, message: 'secret', data: { kind: 'unknown_method' } } })}\n`);
      }
    });
  });
  try {
    await new Promise((resolve) => server.listen(socketPath, resolve));
    const previous = process.env.HC_SOCKET;
    process.env.HC_SOCKET = socketPath;
    try {
      assert.deepEqual(await requestCore('terminal.list'), { terminals: [] });
      await assert.rejects(requestCore('nope'), /herdr-core nope failed: unknown_method/);
      process.env.HC_SOCKET = path.join(directory, 'missing.sock');
      await assert.rejects(requestCore('terminal.list'), /ENOENT/);
    } finally {
      if (previous === undefined) delete process.env.HC_SOCKET;
      else process.env.HC_SOCKET = previous;
    }
  } finally {
    await new Promise((resolve) => server.close(resolve));
    fs.rmSync(directory, { recursive: true });
  }
});

test('normalizes Codex 5-hour and 7-day windows', () => {
  const windows = normalizeQuota({
    result: {
      rateLimitsByLimitId: {
        codex: {
          primary: { usedPercent: 30, windowDurationMins: 300 },
          secondary: { usedPercent: 5, windowDurationMins: 10080 },
        },
      },
    },
  });
  assert.deepEqual(windows.map((window) => window.remainingPercent), [70, 95]);
  assert.deepEqual(windows.map((window) => window.durationMinutes), [300, 10080]);
});

test('rejects invalid Codex quota windows', () => {
  assert.throws(() => normalizeQuota({ rateLimits: {} }), /no rate-limit windows/);
  assert.throws(
    () => normalizeQuota({ rateLimits: { primary: { usedPercent: null } } }),
    /invalid rate-limit percentage/,
  );
});

test('rejects malformed Codex responses without escaping the promise', async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'opendeck-codex-malformed-'));
  const executable = path.join(directory, 'codex');
  fs.writeFileSync(executable, `#!/bin/sh
IFS= read -r initialize
printf '%s\\n' '{"id":0,"result":{}}'
IFS= read -r initialized
IFS= read -r request
printf '%s\\n' '{"id":2,"result":{}}'
`);
  fs.chmodSync(executable, 0o755);
  try {
    await assert.rejects(
      fetchCodexQuota({ codexExecutable: executable, codexHome: directory }),
      /no rate-limit snapshot/,
    );
  } finally {
    fs.rmSync(directory, { recursive: true });
  }
});

test('kills a Codex app-server that ignores the timeout signal', async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'opendeck-codex-timeout-'));
  const executable = path.join(directory, 'codex');
  const pidFile = path.join(directory, 'pid');
  fs.writeFileSync(executable, `#!/bin/sh
printf '%s\\n' "$$" > "${pidFile}"
trap '' TERM
exec sleep 30
`);
  fs.chmodSync(executable, 0o755);
  try {
    await assert.rejects(
      fetchCodexQuota({ codexExecutable: executable, codexHome: directory }, 25),
      /timed out/,
    );
    const pid = fs.readFileSync(pidFile, 'utf8').trim();
    assert.equal(fs.existsSync(`/proc/${pid}`), false);
  } finally {
    fs.rmSync(directory, { recursive: true });
  }
});

test('queries only root OpenCode sessions in the requested window', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'opendeck-agents-'));
  const databasePath = path.join(directory, 'opencode.db');
  const db = new DatabaseSync(databasePath);
  db.exec(`
    CREATE TABLE session (id TEXT PRIMARY KEY, parent_id TEXT);
    CREATE TABLE message (id TEXT PRIMARY KEY, session_id TEXT, time_created INTEGER, data TEXT);
  `);
  const insertSession = db.prepare('INSERT INTO session VALUES (?, ?)');
  insertSession.run('root', null);
  insertSession.run('child', 'root');
  const insertMessage = db.prepare('INSERT INTO message VALUES (?, ?, ?, ?)');
  const data = JSON.stringify({ role: 'assistant', tokens: { input: 100, output: 20, reasoning: 5, cache: { read: 300 } } });
  insertMessage.run('current-root', 'root', Date.now(), data);
  insertMessage.run('current-child', 'child', Date.now(), data);
  insertMessage.run('old-root', 'root', Date.now() - (48 * 60 * 60 * 1000), data);
  db.close();

  try {
    assert.deepEqual(queryActivity(24, databasePath), {
      sessions: 1,
      messages: 1,
      input: 100,
      output: 20,
      reasoning: 5,
      cache_read: 300,
    });
  } finally {
    fs.rmSync(directory, { recursive: true });
  }
});

test('renders self-contained SVG data and compact values', () => {
  assert.match(renderPulse([{ agent_status: 'blocked' }], true), /^data:image\/svg\+xml;base64,/);
  assert.match(decodeSvg(renderPulse([{ agent_status: 'unknown' }], true)), /1 UNKNOWN/);
  assert.match(decodeSvg(renderQuota([{ remainingPercent: 70, durationMinutes: 300 }], 'offline')), /CODEX STALE/);
  assert.equal(compactNumber(1_853_322), '1.9M');
});
