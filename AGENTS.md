# AGENTS.md — Conventions for AI agents working in DESKILL

## Repository purpose

DESKILL is a data engineering skill framework: 14 sequential skills (`/problem → /docs`) plus deep-dive phases, implementation patterns, and AI agent personas. It ships as an npm package (`deskill-de`) and a Kilo/Claude plugin.

## Directory map

| Path | Contents |
|------|----------|
| `SKILL.md` | Root entry point — principles, skill flow, phase map |
| `skills/<name>/SKILL.md` | 14 atomic skills, each owns one deliverable |
| `skills/<name>/assets/` | Templates (YAML, MD) consumed by the skill |
| `skills/<name>/scripts/` | Reusable Python tools (probe, ingest, validate) |
| `skills/<name>/references/` | Heavy reference docs (>50 lines) |
| `skills/skill-graph.json` | Machine-readable skill dependency graph |
| `skills/deliverables.csv` | Flat skill→deliverable→phase manifest |
| `phases/phase-0..9-*.md` | 10 deep-dive methodology docs |
| `implementation/<cat>/*.md` | Code patterns (Airflow, dbt, Spark, GE) |
| `commands/*.md` | Orchestrator commands (`data-pipeline`, `data-driven-feature`) |
| `agents/*.md` | AI agent personas (`data-engineer`, `backend-architect`) |
| `references/anti-patterns.md` | 24 cataloged DE anti-patterns |
| `tools/validate.py` | Repo integrity validator (CI gate) |
| `tools/test-skills.py` | Baseline skill compliance testing |
| `tools/installer/cli.js` | npm CLI installer |

## Commands to run before claiming work is done

```bash
# 1. Repo integrity (frontmatter, encoding, version sync, graph, references)
python tools/validate.py

# 2. Baseline skill compliance (if you modified any skill)
python tools/test-skills.py

# 3. YAML template validity
python -c "import yaml,glob;[yaml.safe_load(open(f,encoding='utf-8')) for f in glob.glob('skills/**/*.y*ml',recursive=True)]"

# 4. JSON validity
python -c "import json;[json.load(open(f,encoding='utf-8')) for f in ['plugin.json','package.json','.claude-plugin/plugin.json','.claude-plugin/marketplace.json','skills/skill-graph.json']]"

# 5. Python syntax (scripts + inline code in skills)
python -c "import ast,glob;[ast.parse(open(f,encoding='utf-8').read()) for f in glob.glob('tools/*.py',recursive=True)+glob.glob('skills/**/*.py',recursive=True)]"

# 6. JS syntax
node --check tools/installer/cli.js
```

If any command fails, fix the issue before declaring completion. Do not commit with failing checks.

## Skill authoring rules

1. **One deliverable per skill.** Each `skills/<name>/SKILL.md` produces exactly one artifact.
2. **Frontmatter:** `name` (letters/numbers/hyphens only) + `description` (starts with "Use when...", <500 chars, when-to-use only — never summarize workflow).
3. **Standard sections:** `## Purpose` → `## When to stop` → `## Steps` → `## Output` → `## DONE WHEN` → `## Next Step` → `## References`.
4. **Chain links:** Every skill references `prev` and `next` skill. First skill (`problem`) has no prev; last (`docs`) has no next.
5. **Feedback loops:** If a later skill can invalidate an earlier decision, state it in `## Next Step` (e.g., "If source can't answer a question, revisit `/problem`").
6. **Encoding:** All files must be clean UTF-8. No cp1252/cp1258 mojibake artifacts. Run `python tools/validate.py` to check.
7. **Cross-references:** Use relative paths from repo root (e.g., `phases/phase-0-discover.md`). Verify paths exist.

## Anti-patterns

See `references/anti-patterns.md` for 24 cataloged mistakes. Check the relevant anti-patterns when modifying a skill.

## Version sync

All manifest files must share one version:
- `package.json` → `version`
- `plugin.json` → `version`
- `.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

`tools/validate.py` enforces this. Bump all four together.

## What NOT to do

- Do not create a central `templates/` or `assets/` directory — templates live per-skill in `skills/<name>/assets/`.
- Do not add `model: opus` to skill frontmatter (only agents have `model`).
- Do not reference the removed lifecycle commands (`/spec`, `/plan`, `/build`, `/validate`, `/review`, `/ship`) — they don't exist. The 14 skills ARE the lifecycle.
- Do not hardcode credentials in examples — use `.env` + `${{ secrets.* }}` in CI.
- Do not skip `tools/validate.py` before committing.
