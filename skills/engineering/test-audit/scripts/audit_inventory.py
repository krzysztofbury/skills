#!/usr/bin/env python3
"""Compact inventory for labelling tests or comments in batches (Python 3.10+).

A labeller reads these batches instead of whole files, so raw source stays
out of its context. Each batch is a JSONL file with one item per line:

- tests: id (path::name), path, name, source (the test function with its
  decorators), helpers (up to three project functions or classes the test
  imports by name, each cut at 45 lines);
- comments: id (path:line), path, line, context (numbered lines around one
  comment block, the block's own lines marked with ">").

Comments are found exactly as audit_ratchet.py counts them (same pragmas,
exemptions, languages and vendored files), so its sibling file is required.

  audit_inventory.py tests --roots tests --out DIR [--batch 40]
  audit_inventory.py comments --roots src tests --out DIR
                     [--languages py sql] [--batch 40]
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_ratchet as ar  # noqa: E402

HELPER_LINES = 45
MAX_HELPERS = 3


def test_functions(tree: ast.Module) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    found: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            found.append((node.name, node))
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name.startswith("test"):
                    found.append((f"{node.name}::{sub.name}", sub))
    return found


def span(lines: list[str], node: ast.stmt) -> list[str]:
    decorators = getattr(node, "decorator_list", [])
    start = min([node.lineno, *(d.lineno for d in decorators)])
    return lines[start - 1 : node.end_lineno]


def helpers(tree: ast.Module, node: ast.AST, modules: dict[str, str]) -> str:
    imported: dict[str, tuple[str, str]] = {}
    for stmt in tree.body:
        if isinstance(stmt, ast.ImportFrom) and stmt.module and stmt.level == 0:
            for alias in stmt.names:
                imported[alias.asname or alias.name] = (stmt.module, alias.name)
    used = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
    parts: list[str] = []
    for local in sorted(used & imported.keys()):
        module, name = imported[local]
        path = modules.get(module)
        if path is None:
            continue
        source = Path(path).read_text(encoding="utf-8")
        for stmt in ast.parse(source).body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and stmt.name == name:
                lines = span(source.splitlines(), stmt)
                if len(lines) > HELPER_LINES:
                    lines = [*lines[:HELPER_LINES], "    ... (cut)"]
                parts.append(f"# {path}\n" + "\n".join(lines))
        if len(parts) >= MAX_HELPERS:
            break
    return "\n\n".join(parts)


def module_index() -> dict[str, str]:
    """Dotted module name -> file, for every tracked Python file (any src layout)."""
    index: dict[str, str] = {}
    for path in ar.tracked_files(["."], ["py"]):
        parts = list(Path(path).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        for start in range(len(parts)):
            index.setdefault(".".join(parts[start:]), path)
    return index


def test_items(roots: list[str]) -> list[dict[str, str]]:
    modules = module_index()
    items: list[dict[str, str]] = []
    for path in ar.tracked_files(roots, ["py"]):
        if not Path(path).name.startswith("test_"):
            continue
        source = Path(path).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=path)
        lines = source.splitlines()
        for name, node in test_functions(tree):
            items.append({
                "id": f"{path}::{name}", "path": path, "name": name,
                "source": "\n".join(span(lines, node)),
                "helpers": helpers(tree, node, modules),
            })
    return items


def comment_items(roots: list[str], languages: list[str]) -> list[dict[str, str | int]]:
    items: list[dict[str, str | int]] = []
    for path in ar.tracked_files(roots, languages):
        source = Path(path).read_text(encoding="utf-8")
        lines = source.splitlines()
        rows = sorted({row for row, _ in ar.comments(path, source)})
        blocks: list[list[int]] = []
        for row in rows:
            if blocks and blocks[-1][-1] == row - 1:
                blocks[-1].append(row)
            else:
                blocks.append([row])
        for block in blocks:
            low, high = max(1, block[0] - 4), min(len(lines), block[-1] + 6)
            context = "\n".join(
                f"{i:>5}{'>' if i in block else ' '} {lines[i - 1]}" for i in range(low, high + 1)
            )
            items.append({"id": f"{path}:{block[0]}", "path": path, "line": block[0], "context": context})
    return items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=["tests", "comments"])
    parser.add_argument("--roots", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--languages", nargs="+", default=["py"])
    parser.add_argument("--batch", type=int, default=40)
    args = parser.parse_args(argv)
    try:
        items = test_items(args.roots) if args.kind == "tests" else comment_items(args.roots, args.languages)
    except (ar.RatchetError, SyntaxError) as error:
        print(error, file=sys.stderr)
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    batches = [items[i : i + args.batch] for i in range(0, len(items), args.batch)]
    for number, batch in enumerate(batches, 1):
        with open(out / f"{args.kind}-{number:03d}.jsonl", "w", encoding="utf-8") as handle:
            handle.writelines(json.dumps(item) + "\n" for item in batch)
    print(f"{len(items)} {args.kind} in {len(batches)} batches of up to {args.batch} under {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
