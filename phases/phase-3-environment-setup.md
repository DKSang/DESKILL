# Phase 3 — Environment Setup

## Goal
Get a minimal, reproducible environment running before writing any pipeline logic — so that "it works on my machine" is never a question later.

## Generic activities
1. Write the containerization config (e.g. `docker-compose.yml`) for the tools chosen in Phase 2 — typically an orchestrator UI + scheduler, and any local storage service.
2. Scaffold the transformation project (e.g. `dbt init` if using dbt) with folder structure matching the layer naming convention from Phase 2.
3. Set up secrets management: `.env` file (or equivalent) for API keys/credentials, explicitly excluded from version control via `.gitignore` — never hardcode credentials in scripts.
4. Pin dependencies (`requirements.txt`, `package.json`, or equivalent) so the environment is reproducible for anyone (including a future you) who clones the repo.
5. Verify the environment actually starts cleanly from a fresh clone — this is the acceptance test for this phase, not "it runs on my current machine state."

## Output
A repo that starts with a single command (e.g. `docker compose up`) and reaches a usable state (e.g. orchestrator UI reachable) with no manual undocumented steps.

## AI usage tips
- This phase has the highest AI leverage-to-risk ratio: boilerplate Docker/Dockerfile/dependency files are low-risk for AI to draft correctly on the first pass, freeing time for the higher-judgment phases.
- Have AI explain any config it generates that you don't fully understand yet — copying an unexplained Docker Compose block is a common source of later confusion.

## Feedback loop triggers
If Phase 4/5 requires a tool/library not accounted for here, update this environment definition immediately rather than installing things ad hoc and losing reproducibility.

## DESKILL Skills
This phase is implemented by:
- `/env` → `skills/env/SKILL.md` — creates `docker-compose.yml`, `.env.template`, `requirements.txt`

## Implementation patterns
- `implementation/orchestration/airflow-patterns.md` — project structure section for Airflow docker-compose setup
- `implementation/transformation/dbt-patterns.md` — dbt project initialization and `dbt_project.yml` configuration
- `commands/data-pipeline.md` — configuration files section with Docker Compose recommendations
