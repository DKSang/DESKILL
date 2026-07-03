# Changelog

## [3.1.0] — 2026-07-03

### Fixed
- Repaired UTF-8 double-mojibake (em/en-dash, arrows, box-drawing, ×, ≤/≥) across 10 skill files
- Reconciled version drift: `plugin.json`, `package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` now share one version
- Removed `marketplace.json` references to nonexistent lifecycle commands (`/spec`, `/plan`, `/build`, `/validate`, `/review`, `/ship`); corrected relative paths to `../commands/` and `../agents/`
- Removed nonexistent `templates/`, `references/`, `assets/` entries from `package.json` `files` (would break `npm pack`)
- Created `skills/contract-check/scripts/validate_contract.py` to satisfy the skill's broken script reference
- Fixed `dag` Prefect example (missing `transform_gold`, `dq_checks`, `contract_check` task definitions)
- Fixed SQL injection vectors and timezone-naive comparisons in `dq` and `contract-check` examples (parameterized queries + tz-aware timestamps)
- `dq` now writes `docs/dq_report.md` as its DONE WHEN claims; aligned report paths with the root progress checklist
- Fixed `quality.yml` phase-file glob (always reported MISSING) and removed dead `templates/*.yaml` step
- Fixed `publish.yml` invalid `body_path` expression

### Added
- `skills/skill-graph.json` — machine-readable skill dependency graph (skill → next/prev/phase/deliverable)
- `skills/deliverables.csv` — skill→deliverable→phase manifest for tooling and verification
- `tools/validate.py` — repo integrity validator (frontmatter, version sync, reference resolution, graph cycles)
- `tools/test-skills.py` — baseline compliance testing for discipline skills (TDD for skills)
- `references/anti-patterns.md` — 24 cataloged DE anti-patterns with skill cross-references
- `AGENTS.md` — AI agent conventions, lint/typecheck/test commands

### Changed
- CLI installer no longer offers dead `templates`/`references`/`assets` components; generated `CLAUDE.md` and Copilot instructions reference the 14 real skills instead of the removed lifecycle commands
- `serve` skill references corrected (no longer mislabels persona/command files as pattern references)
- Root `SKILL.md` description trimmed to 387 chars (SDO-compliant, when-to-use only)
- `env` skill: added prod warning for demo `admin/admin` Airflow credentials
- `data-driven-feature` command: marked as extension outside the 14-skill chain
- `CONTRIBUTING.md`: fixed dead `validate-skills.js` reference → `validate.py`

## [2.0.0] — 2026-07-01

### Added
- Initial 10-phase data engineering project roadmap
- Business problem and data contract templates (now in `skills/*/assets/`)
- Tool-agnostic, domain-agnostic framework
- AI pair-engineering integration at every phase

### Legacy
- Original 10-phase methodology preserved in `phases/`
- Original templates preserved in `skills/*/assets/` (per-skill, not a central `templates/` dir)
