<p align="center">
  <img src="https://raw.githubusercontent.com/anomalyco/DESKILL/main/Wordmark.png" alt="DESKILL" width="480"/>
</p>

<p align="center">
  <em>Data Engineering Project Roadmap — from business problem to production pipeline</em>
</p>



---

## Why DESKILL?

Building a data pipeline usually falls into two traps:

- **Trap 1:** Jumping straight into tool selection, forgetting the business problem
- **Trap 2:** Having methodology but no idea how to implement it in code

DESKILL solves both: **process methodology** (thinking framework, ordering, feedback loops) combined with **production code patterns** (Airflow, dbt, Spark, Great Expectations) in a unified framework.

---

## Installation

```bash
# Option 1: npm (recommended)
npx deskill-de install

# Option 2: Clone repo
git clone https://github.com/anomalyco/DESKILL.git
```

---

## Quick Start — 14 Sequential Skills

Each skill produces one deliverable and suggests the next skill to run:

```
  /problem → /sources → /arch → /schema → /env → /ingest → /transform
  → /test → /dq → /contract-check → /dag → /serve → /ci → /docs
```

| Skill | Output |
|-------|--------|
| `/problem` | `docs/business_problem.md` |
| `/sources` | `contracts/source-*.yaml` |
| `/arch` | `docs/architecture.md` |
| `/schema` | `docs/dw_schema.md` |
| `/env` | `docker-compose.yml` |
| `/ingest` | `ingestion/<source>/ingest.py` |
| `/transform` | Silver + Gold models |
| `/test` | `tests/` all passing |
| `/dq` | `quality/dq_checks.py` |
| `/contract-check` | Contract validation report |
| `/dag` | `dags/<project>_pipeline.py` |
| `/serve` | `serving/app.py` |
| `/ci` | `.github/workflows/ci.yml` |
| `/docs` | `README.md` + lineage + cost |

---

## Repository Structure

```
DESKILL/
├── SKILL.md                        # Entry point — principles, skill flow, phase map
├── plugin.json                     # Plugin manifest
├── package.json                    # npm package + CLI installer
├── commands/                       # Orchestrator commands
├── skills/                         # 14 atomic skills (one deliverable each)
│   ├── problem/                    #   Business problem definition
│   ├── sources/                    #   Source evaluation & data contracts
│   ├── arch/                       #   Pipeline architecture design
│   ├── schema/                     #   DW schema (Fact & Dimension tables)
│   ├── env/                        #   Development environment setup
│   ├── ingest/                     #   Bronze ingestion layer
│   ├── transform/                  #   Silver & Gold transformations
│   ├── test/                       #   Test suite (schema & logic)
│   ├── dq/                         #   Runtime data quality checks
│   ├── contract-check/             #   Data vs contract validation
│   ├── dag/                        #   Orchestration DAG
│   ├── serve/                      #   Serving layer (dashboard / API)
│   ├── ci/                         #   CI/CD (GitHub Actions)
│   └── docs/                       #   Documentation
├── phases/                         # Deep-dive methodology (10 phases)
├── implementation/                 # Code patterns: Airflow, dbt, Spark, GE
└── agents/                         # AI agent personas
```

---

## Key Features

- **Domain-agnostic** — Weather, e-commerce, finance, IoT, logistics: works everywhere
- **Tool-agnostic** — No mandated stack; guidance for choosing tools by scale and goals
- **Iterative** — Feedback loops between phases; later discoveries can revise earlier decisions
- **AI-native** — Designed to be used with an AI pair-engineer at every phase
- **Production patterns** — Real code examples from Airflow, dbt, Spark, Great Expectations
- **Sequential by design** — Each skill suggests the next, guiding you end-to-end

---

## Comparison with Other Frameworks

| | DESKILL | wshobson/agents | vaquarkhan/agent-skills |
|---|---|---|---|
| Methodology | 10-phase roadmap + 14 sequential skills | — | — (isolated skills only) |
| Code patterns | Airflow, dbt, Spark, GE | Airflow, dbt, Spark, GE | — |
| AI agent personas | data-engineer + backend-architect | data-engineer + backend-architect | — |
| Skill graph | 14 skills, each suggests the next | — | — |
| Anti-patterns | ~30 common mistakes cataloged | — | Yes (across 73 skills) |
| Templates | 14 skill assets | — | 8 YAML |
| Packaging | npm + CLI + CI/CD + plugin | Plugin-only | Full IDE integration |

---

## Credits

- **Process methodology:** Inspired by *Fundamentals of Data Engineering* (Reis & Housley)
- **Implementation patterns:** Adapted from [wshobson/agents](https://github.com/wshobson/agents) (MIT)
- **Packaging pattern:** Inspired by [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)

---

## License

MIT © DESKILL
