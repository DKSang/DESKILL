# Changelog

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
