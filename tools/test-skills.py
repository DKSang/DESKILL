#!/usr/bin/env python3
"""
tools/test-skills.py — Baseline compliance testing for DESKILL skills.

This is NOT full pressure-scenario testing (see writing-skills skill for that).
It verifies structural compliance: every skill has the required sections,
correct frontmatter, valid chain links, and DONE WHEN criteria.

Run:  python tools/test-skills.py
Exit non-zero on any failure.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

failures: list[str] = []
passed = 0

REQUIRED_SECTIONS = [
    "## Purpose",
    "## Steps",
    "## Output",
    "## DONE WHEN",
    "## Next Step",
    "## References",
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(\S+)", re.MULTILINE)
DESC_RE = re.compile(r"^description:\s*\"?(.+?)\"?\s*$", re.MULTILINE)


def fail(msg: str) -> None:
    failures.append(msg)


def check_skill(path: Path, expected_id: str) -> None:
    global passed
    text = path.read_text(encoding="utf-8")
    name = path.parent.name

    # Frontmatter
    fm = FRONTMATTER_RE.match(text)
    if not fm:
        fail(f"{name}: missing YAML frontmatter")
        return
    raw = fm.group(1)
    nm = NAME_RE.search(raw)
    if not nm:
        fail(f"{name}: frontmatter missing 'name'")
    elif nm.group(1) != f"de-{expected_id}":
        fail(f"{name}: frontmatter name='{nm.group(1)}' expected 'de-{expected_id}'")
    desc = DESC_RE.search(raw)
    if not desc:
        fail(f"{name}: frontmatter missing 'description'")
    elif not desc.group(1).strip().startswith("Use when"):
        # Root SKILL.md is allowed to differ; skills should follow SDO
        if name != expected_id or path != ROOT / "SKILL.md":
            # Check if it starts with a trigger phrase — some skills use "Evaluate..." etc.
            if not any(desc.group(1).strip().startswith(t) for t in
                       ("Use when", "Define ", "Evaluate ", "Design ", "Create ",
                        "Implement ", "Write ", "Build ", "Set up ", "Validate ",
                        "Automatically verify")):
                fail(f"{name}: description should start with 'Use when...' (SDO)")
    desc_len = len(desc.group(1)) if desc else 0
    if desc_len > 500:
        fail(f"{name}: description is {desc_len} chars (max 500 for SDO)")

    # Required sections
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"{name}: missing section '{section}'")

    # DONE WHEN must have at least 1 checkbox
    done_match = re.search(r"## DONE WHEN\s*\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if done_match:
        if "- [ ]" not in done_match.group(1) and "- [x]" not in done_match.group(1):
            fail(f"{name}: DONE WHEN has no checklist items")

    # Next Step must mention a skill (prev/next or "run /")
    next_match = re.search(r"## Next Step\s*\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if next_match:
        ns = next_match.group(1)
        if "/" not in ns and "complete" not in ns.lower():
            fail(f"{name}: Next Step doesn't reference a skill or completion")

    passed += 1


def check_chain() -> None:
    """Verify skill-graph.json chain matches actual skill files."""
    global passed
    gp = ROOT / "skills/skill-graph.json"
    if not gp.exists():
        fail("skills/skill-graph.json: missing (needed for chain check)")
        return
    data = json.loads(gp.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    for n in nodes:
        sf = ROOT / n["skillFile"]
        if not sf.exists():
            fail(f"skill-graph: {n['id']}.skillFile missing: {n['skillFile']}")
        else:
            check_skill(sf, n["id"])
    # verify chain: next of node i = id of node i+1
    for i, n in enumerate(nodes):
        nxt = n.get("next")
        expected_next = nodes[i + 1]["id"] if i + 1 < len(nodes) else None
        if nxt != expected_next:
            fail(f"skill-graph: chain broken at {n['id']}.next={nxt} expected={expected_next}")
        prv = n.get("prev")
        expected_prev = nodes[i - 1]["id"] if i - 1 >= 0 else None
        if prv != expected_prev:
            fail(f"skill-graph: chain broken at {n['id']}.prev={prv} expected={expected_prev}")
    passed += 1


def check_deliverables_csv() -> None:
    """Verify deliverables.csv matches skill-graph.json."""
    global passed
    cp = ROOT / "skills/deliverables.csv"
    if not cp.exists():
        fail("skills/deliverables.csv: missing")
        return
    with open(cp, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 14:
        fail(f"deliverables.csv: expected 14 rows, got {len(rows)}")
    for row in rows:
        sf = ROOT / row["skill_file"]
        if not sf.exists():
            fail(f"deliverables.csv: skill_file missing for {row['skill']}: {row['skill_file']}")
    passed += 1


def check_anti_patterns() -> None:
    """Verify anti-patterns.md exists and references skills."""
    global passed
    ap = ROOT / "references/anti-patterns.md"
    if not ap.exists():
        fail("references/anti-patterns.md: missing")
        return
    text = ap.read_text(encoding="utf-8")
    if "AP-1:" not in text or "AP-24:" not in text:
        fail("references/anti-patterns.md: missing anti-pattern entries (AP-1..AP-24)")
    passed += 1


def main() -> int:
    print("Running DESKILL skill compliance tests...")
    print()
    check_chain()
    check_deliverables_csv()
    check_anti_patterns()

    if failures:
        print(f"FAIL ({len(failures)} issues, {passed} checks passed):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS — all {passed} compliance checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
