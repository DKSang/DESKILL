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

### Changed
- CLI installer no longer offers dead `templates`/`references`/`assets` components; generated `CLAUDE.md` and Copilot instructions reference the 14 real skills instead of the removed lifecycle commands
- `serve` skill references corrected (no longer mislabels persona/command files as pattern references)

## [2.0.0] — 2026-07-01

### Added
- Lifecycle commands: `/spec`, `/plan`, `/build`, `/validate`, `/review`, `/ship`
- YAML templates: `source-contract.yaml`, `backfill-plan.yaml`, `release-gate.yaml`
- Anti-patterns reference: `references/anti-patterns.md`
- npm packaging with CLI installer: `npx deskill install`
- GitHub CI/CD workflows: quality checks + publish
- Licensed under MIT

### Merged
- Implementation patterns from wshobson/agents (Airflow, dbt, Spark, Great Expectations)
- AI agent personas (data-engineer, backend-architect)
- Orchestrator commands (data-pipeline, data-driven-feature)
- Plugin packaging (plugin.json, .claude-plugin/)

### Changed
- SKILL.md restructured with dual-path navigation (lifecycle commands + phase-based)
- Phase files updated with implementation reference links
- Directory structure reorganized with `phases/` + `implementation/` + `commands/` + `templates/`

### Legacy
- Original 10-phase methodology preserved in `phases/` and `references/`
- Original templates preserved in `assets/`

## [1.0.0] — 2026-06-01

### Added
- Initial 10-phase data engineering project roadmap
- Business problem and data contract templates
- Tool-agnostic, domain-agnostic framework
- AI pair-engineering integration at every phase
