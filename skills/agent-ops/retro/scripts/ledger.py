#!/usr/bin/env python3
"""Retro ledger: a small log of retrospective entries.

Standard library only. Run as `python3 -I scripts/ledger.py <command>`.

Ledger path, first match wins:
  1. environment variable RETRO_LEDGER
  2. key "ledger" in ~/.config/retro/config.json (XDG_CONFIG_HOME honored)
  3. .agents/retro.jsonl in the current git repository, if that file exists
  4. ${XDG_STATE_HOME:-~/.local/state}/retro/ledger.sqlite

A path ending in .jsonl is an append-only JSON Lines file, one entry per line,
meant to be committed with the project so the history is reviewable and
merges cleanly. Any other path is a SQLite database.
"""

import argparse
import json
import os
import secrets
import stat
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

GOALS = ("achieved", "partial", "not_achieved")
FIELDS = (
    "id",
    "created_at",
    "project",
    "harness",
    "goal",
    "helped",
    "friction",
    "changes",
    "candidates",
    "refs",
)
TEXT_FIELDS = ("helped", "friction", "changes", "candidates", "refs")
SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    project TEXT NOT NULL,
    harness TEXT,
    goal TEXT CHECK (goal IN ('achieved', 'partial', 'not_achieved')),
    helped TEXT,
    friction TEXT,
    changes TEXT,
    candidates TEXT,
    refs TEXT
)
"""
REPO_LEDGER = Path(".agents") / "retro.jsonl"


class LedgerError(Exception):
    pass


def _env_dir(name, fallback):
    value = os.environ.get(name, "")
    return Path(value).expanduser() if value else Path.home() / fallback


def config_path():
    return _env_dir("XDG_CONFIG_HOME", ".config") / "retro" / "config.json"


def ledger_path():
    env = os.environ.get("RETRO_LEDGER", "")
    if env:
        return Path(env).expanduser()
    cfg = config_path()
    if cfg.is_file():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise LedgerError(f"cannot read {cfg}: {exc}") from exc
        if not isinstance(data, dict):
            raise LedgerError(f"{cfg} must contain a JSON object")
        value = data.get("ledger")
        if value:
            if not isinstance(value, str):
                raise LedgerError(f'{cfg}: "ledger" must be a string path')
            return Path(value).expanduser()
    top = _git("rev-parse", "--show-toplevel")
    if top:
        candidate = Path(top) / REPO_LEDGER
        if candidate.is_file():
            root = Path(top).resolve()
            if candidate.is_symlink() or root not in candidate.resolve().parents:
                raise LedgerError(
                    f"{candidate} is a link or leaves the repository; refusing it"
                )
            return candidate
    return _env_dir("XDG_STATE_HOME", ".local/state") / "retro" / "ledger.sqlite"


def is_jsonl(path):
    return path.suffix == ".jsonl"


def jsonl_rows():
    """All entries of a JSON Lines ledger; a missing file has none."""
    path = ledger_path()
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except ValueError as exc:
                raise LedgerError(f"{path}:{number}: not JSON: {exc}") from exc
            if not isinstance(item, dict):
                raise LedgerError(f"{path}:{number}: entry must be an object")
            rows.append({key: item.get(key) for key in FIELDS})
    return rows


def jsonl_append(entry):
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o644)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise LedgerError(f"{path} is not a regular file")
    with os.fdopen(fd, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=False) + "\n")


def connect():
    """Open the ledger for writing, creating it on first use."""
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(entries)")}
    if "refs" not in columns:
        conn.execute("ALTER TABLE entries ADD COLUMN refs TEXT")
    conn.commit()
    return conn


def read_rows(sql, params):
    """Run a query read-only. A missing ledger has no rows; nothing is created."""
    path = ledger_path()
    if not path.exists():
        return []
    conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [
            {key: dict(row).get(key) for key in FIELDS}
            for row in conn.execute(sql, params).fetchall()
        ]
    except sqlite3.OperationalError as error:
        if "no such table" in str(error):
            return []
        raise
    finally:
        conn.close()


def _git(*args):
    try:
        out = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def _strip_credentials(url):
    """Drop user:password@ from an http(s) remote so tokens never reach the ledger."""
    parts = urlsplit(url)
    if parts.scheme in ("http", "https") and "@" in parts.netloc:
        host = parts.netloc.rsplit("@", 1)[1]
        return urlunsplit((parts.scheme, host, parts.path, parts.query, parts.fragment))
    return url


def detect_project():
    """Remote URL of origin when available, else the git toplevel path."""
    remote = _git("remote", "get-url", "origin")
    project = _strip_credentials(remote) if remote else _git(
        "rev-parse", "--show-toplevel"
    )
    if not project:
        raise LedgerError(
            "cannot detect project: not in a git repository; pass --project"
        )
    return project


def _like(pattern):
    escaped = (
        pattern.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    )
    return f"%{escaped}%"


def _emit(rows, as_json, footer=None):
    items = [dict(row) for row in rows]
    if as_json:
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return
    for item in items:
        print(
            f"#{item['id']} {item['created_at']} | {item['harness'] or '-'}"
            f" | {item['project']} | goal: {item['goal'] or '-'}"
        )
        for key in TEXT_FIELDS:
            if item[key]:
                print(f"  {key}: {item[key]}")
    if footer is not None:
        print(footer)


def cmd_add(args):
    project = args.project or detect_project()
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    values = {key: getattr(args, key) for key in ("harness", "goal") + TEXT_FIELDS}
    if is_jsonl(ledger_path()):
        new_id = secrets.token_hex(4)
        entry = {"id": new_id, "created_at": created_at, "project": project}
        entry.update({key: value for key, value in values.items() if value})
        jsonl_append(entry)
    else:
        with connect() as conn:
            cur = conn.execute(
                "INSERT INTO entries (created_at, project, harness, goal, helped,"
                " friction, changes, candidates, refs)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (created_at, project) + tuple(values.values()),
            )
            new_id = cur.lastrowid
        conn.close()
    if args.json:
        print(json.dumps({"id": new_id, "created_at": created_at, "project": project}))
    else:
        print(new_id)


def _newest_first(rows):
    return sorted(rows, key=lambda row: row["created_at"] or "", reverse=True)


def cmd_list(args):
    if is_jsonl(ledger_path()):
        rows = [r for r in jsonl_rows() if not args.project or r["project"] == args.project]
        _emit(_newest_first(rows)[: args.limit], args.json)
        return
    sql = "SELECT * FROM entries"
    params = []
    if args.project:
        sql += " WHERE project = ?"
        params.append(args.project)
    sql += " ORDER BY created_at DESC, id DESC LIMIT ?"
    params.append(args.limit)
    rows = read_rows(sql, params)
    _emit(rows, args.json)


def cmd_search(args):
    if is_jsonl(ledger_path()):
        needle = args.pattern.casefold()
        rows = [
            r
            for r in jsonl_rows()
            if (not args.project or r["project"] == args.project)
            and any(needle in (r[key] or "").casefold() for key in TEXT_FIELDS[1:4])
        ]
        rows = _newest_first(rows)
        _emit(rows, args.json, footer=f"matches: {len(rows)}")
        return
    like = _like(args.pattern)
    sql = (
        "SELECT * FROM entries WHERE (friction LIKE ? ESCAPE '\\'"
        " OR changes LIKE ? ESCAPE '\\' OR candidates LIKE ? ESCAPE '\\')"
    )
    params = [like, like, like]
    if args.project:
        sql += " AND project = ?"
        params.append(args.project)
    sql += " ORDER BY created_at DESC, id DESC"
    rows = read_rows(sql, params)
    _emit(rows, args.json, footer=f"matches: {len(rows)}")


def cmd_path(_args):
    print(ledger_path())


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ledger.py", description="Retro ledger (JSON Lines or SQLite)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record one retro entry")
    add.add_argument(
        "--project",
        help="project id; default: git remote origin URL, else git toplevel path",
    )
    add.add_argument("--harness", help="for example claude-code, codex, opencode")
    add.add_argument("--goal", choices=GOALS, help="session goal outcome")
    add.add_argument("--helped", help="practice that helped")
    add.add_argument("--friction", help="problem and confirmed cause or hypothesis")
    add.add_argument("--changes", help="files actually changed, or none")
    add.add_argument("--candidates", help="pattern and occurrence count, or none")
    add.add_argument("--refs", help="issue or pull request links the entry is about")
    add.add_argument("--json", action="store_true", help="print JSON")
    add.set_defaults(func=cmd_add)

    lst = sub.add_parser("list", help="show recent entries, newest first")
    lst.add_argument("--project", help="exact project id to filter on")
    lst.add_argument("--limit", type=int, default=20, help="default 20")
    lst.add_argument("--json", action="store_true", help="print JSON")
    lst.set_defaults(func=cmd_list)

    srch = sub.add_parser(
        "search",
        help="case-insensitive substring search over friction, changes, candidates",
    )
    srch.add_argument("pattern", help="text to look for (no wildcards needed)")
    srch.add_argument("--project", help="exact project id to filter on")
    srch.add_argument("--json", action="store_true", help="print JSON")
    srch.set_defaults(func=cmd_search)

    pth = sub.add_parser("path", help="print the resolved ledger path")
    pth.set_defaults(func=cmd_path)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (LedgerError, sqlite3.Error, OSError) as exc:
        print(f"ledger.py: error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
