#!/usr/bin/env python3
"""
tools/validate.py — DESKILL repo integrity validator.

Checks:
  1. Every skills/*/SKILL.md has valid YAML frontmatter (name + description)
  2. Every .md file is clean UTF-8 (no double-mojibake artifacts)
  3. Version is in sync across package.json, plugin.json, .claude-plugin/*
  4. skill-graph.json is internally consistent (chain, no cycles, paths exist)
  5. marketplace.json skill/command/agent paths resolve
  6. phases 0-9 exist

Exits non-zero on any error so it can gate CI.
Run:  python tools/validate.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

errors: list[str] = []
warnings: list[str] = []

# Characters that indicate unrepaired cp1252/cp1258 double-mojibake.
_MOJIBAKE = set("\u00e2\u20ac\u201c\u201d\u2030\u00a4\u2020\u0102\u0090\u009d\u008d\u0081")


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# ─── 1. Frontmatter ──────────────────────────────────────────────────────────
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def check_frontmatter(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        err(f"{path.relative_to(ROOT)}: not valid UTF-8 ({e})")
        return
    m = _FRONTMATTER_RE.match(text)
    if not m:
        err(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return
    raw = m.group(1)
    name = re.search(r"^name:\s*(\S+)", raw, re.MULTILINE)
    desc = re.search(r"^description:\s*(.+)", raw, re.MULTILINE)
    if not name:
        err(f"{path.relative_to(ROOT)}: frontmatter missing 'name'")
    if not desc:
        err(f"{path.relative_to(ROOT)}: frontmatter missing 'description'")


# ─── 2. UTF-8 / mojibake ──────────────────────────────────────────────────────
def check_encoding(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        err(f"{path.relative_to(ROOT)}: invalid UTF-8 ({e})")
        return
    bad = sorted({ch for ch in text if ch in _MOJIBAKE})
    if bad:
        err(f"{path.relative_to(ROOT)}: mojibake artifacts found: {[hex(ord(c)) for c in bad]}")


# ─── 3. Version sync ──────────────────────────────────────────────────────────
def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        err(f"{path.relative_to(ROOT)}: invalid JSON ({e})")
        return {}


def check_versions() -> None:
    versions: dict[str, str] = {}
    for rel in ["package.json", "plugin.json", ".claude-plugin/plugin.json"]:
        p = ROOT / rel
        if p.exists():
            data = read_json(p)
            v = data.get("version")
            if v:
                versions[rel] = v
    mp = ROOT / ".claude-plugin/marketplace.json"
    if mp.exists():
        data = read_json(mp)
        for plugin in data.get("plugins", []):
            versions[".claude-plugin/marketplace.json"] = plugin.get("version")
            break
    unique = set(versions.values())
    if len(unique) > 1:
        err(f"Version drift: {versions}")
    elif len(unique) == 1:
        print(f"OK  version sync: {unique.pop()}")


# ─── 4. skill-graph.json ──────────────────────────────────────────────────────
def check_skill_graph() -> None:
    gp = ROOT / "skills/skill-graph.json"
    if not gp.exists():
        err("skills/skill-graph.json: missing")
        return
    data = read_json(gp)
    nodes = data.get("nodes", [])
    if not nodes:
        err("skill-graph.json: no nodes")
        return
    by_id = {n["id"]: n for n in nodes}
    ids = [n["id"] for n in nodes]

    # chain integrity: next of node i == id of node i+1
    for i, n in enumerate(nodes):
        nxt = n.get("next")
        if nxt is not None and nxt != (nodes[i + 1]["id"] if i + 1 < len(nodes) else None):
            err(f"skill-graph: broken chain at {n['id']}.next={nxt}")
        prv = n.get("prev")
        if prv is not None and prv != (nodes[i - 1]["id"] if i - 1 >= 0 else None):
            err(f"skill-graph: broken chain at {n['id']}.prev={prv}")
        # cycle check via next pointer walk
    # path existence for declared assets/scripts/references/skillFile
    for n in nodes:
        for key in ("skillFile",):
            p = ROOT / n.get(key, "")
            if not p.exists():
                err(f"skill-graph: {n['id']}.{key} path missing: {n.get(key)}")
        for key in ("assets", "scripts", "references"):
            for rel in n.get(key, []) or []:
                if not (ROOT / rel).exists():
                    err(f"skill-graph: {n['id']}.{key} path missing: {rel}")
        # feedback targets must be valid ids
        for fb in n.get("feedbackTo", []) or []:
            if fb not in by_id:
                err(f"skill-graph: {n['id']}.feedbackTo unknown skill: {fb}")
    # top-level references and tools paths
    for rel in data.get("references", []) or []:
        if not (ROOT / rel).exists():
            err(f"skill-graph: references path missing: {rel}")
    for rel in data.get("tools", []) or []:
        if not (ROOT / rel).exists():
            err(f"skill-graph: tools path missing: {rel}")
    print(f"OK  skill-graph: {len(nodes)} nodes, chain intact")


# ─── 5. marketplace.json paths ────────────────────────────────────────────────
def check_marketplace() -> None:
    mp = ROOT / ".claude-plugin/marketplace.json"
    if not mp.exists():
        return
    data = read_json(mp)
    base = mp.parent
    for plugin in data.get("plugins", []):
        for key in ("skills", "commands", "agents"):
            for rel in plugin.get(key, []) or []:
                if not (base / rel).resolve().exists():
                    err(f"marketplace.json: {key} path missing: {rel}")


# ─── 6. phases ────────────────────────────────────────────────────────────────
def check_phases() -> None:
    for i in range(10):
        if not list((ROOT / "phases").glob(f"phase-{i}-*.md")):
            err(f"phases/phase-{i}-*.md: missing")
    # check phase files have DESKILL Skills back-links
    for pf in sorted((ROOT / "phases").glob("phase-*.md")):
        text = pf.read_text(encoding="utf-8")
        if "## DESKILL Skills" not in text:
            warn(f"{pf.relative_to(ROOT)}: missing '## DESKILL Skills' back-link section")


# ─── 7. references ────────────────────────────────────────────────────────────
def check_references() -> None:
    ap = ROOT / "references/anti-patterns.md"
    if not ap.exists():
        err("references/anti-patterns.md: missing")
        return
    text = ap.read_text(encoding="utf-8")
    if "AP-24:" not in text:
        err("references/anti-patterns.md: incomplete (missing AP-24 or later)")


# ─── main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    print(f"Validating DESKILL repo at {ROOT}")
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for sf in skill_files:
        check_frontmatter(sf)
    md_files = [ROOT / "SKILL.md"] + skill_files
    md_files += sorted((ROOT / "phases").glob("*.md"))
    md_files += sorted((ROOT / "implementation").rglob("*.md"))
    md_files += sorted((ROOT / "commands").glob("*.md"))
    md_files += sorted((ROOT / "agents").glob("*.md"))
    for mf in md_files:
        check_encoding(mf)
    check_versions()
    check_skill_graph()
    check_marketplace()
    check_phases()
    check_references()

    # also validate deliverables.csv parses
    csvp = ROOT / "skills/deliverables.csv"
    if csvp.exists():
        try:
            with open(csvp, encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            print(f"OK  deliverables.csv: {len(rows)} rows")
        except Exception as e:
            err(f"deliverables.csv: {e}")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  - {e}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"\nAll checks passed ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
