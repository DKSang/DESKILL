---
name: de-project-roadmap
description: "Use whenever the user is planning or working through ANY data engineering project or portfolio pipeline, in any domain (weather, e-commerce, finance, IoT, logistics, etc.) or scale. Trigger on: building a data pipeline, ETL/ELT project, data platform, dbt project, Airflow/orchestration DAG, Medallion architecture, 'how should I structure my data engineering project', 'roadmap for building X pipeline', 'plan my data engineer portfolio project', or being stuck mid-project on what phase comes next. Also use when the user has a business problem or source in mind but no project structure yet. Skip for pure data-analysis questions or narrow single-tool asks (e.g. one SQL query) with no project-level structure needed."
---

# Data Engineering Project Roadmap

A domain-agnostic, tool-agnostic framework for planning and building a data engineering project end-to-end — from business problem to production-ready portfolio piece. Grounded in the Data Engineering Lifecycle from *Fundamentals of Data Engineering* (Reis & Housley) and designed to be used with AI as an active pair-engineer at every phase.

This skill combines **process methodology** (the 10-phase roadmap, iterative thinking, data contracts) with **concrete implementation patterns** (code examples, tool-specific configurations, AI agent personas) from production data engineering practice.

## Core principles (apply these before anything else)

1. **Iterative, not linear.** A 10-phase list looks sequential on paper, but real projects loop back constantly — a discovery made in Phase 4 (Ingestion) routinely forces a revision in Phase 1 (Data Contracts) or even Phase 0 (Business Problem). Treat every phase boundary as provisional, not final. Never let the user (or yourself) treat "I already finished Phase X" as a reason to ignore a contradiction found later.
2. **Undercurrents run throughout, not at the end.** Security, Data Management, DataOps, Data Architecture, Orchestration, and Software Engineering are NOT a checklist item bolted onto the last phase — they are concerns to actively raise at every phase. When helping with any phase, briefly flag relevant undercurrents rather than deferring them.
3. **Data contracts are a first-class deliverable**, not a footnote to "evaluate sources." Before writing any ingestion code, the schema, update frequency, rate limits, auth method, and breaking-change risk of each source should be written down.
4. **Testing ≠ Data Quality.** Testing validates transformation *logic* (does this SQL/Python do what it's supposed to do, checked at code-change time). Data Quality validates *actual data* (is today's data within expected bounds, checked at runtime). Keep these as separate concerns even though they often live in the same tooling (e.g. dbt).
5. **Tools are choices, not requirements.** This skill never mandates a specific stack. Each phase reference lists common options with tradeoffs; pick based on project scale, target job market, and what's genuinely needed to answer the business problem — not because a tutorial used it.

## Quick start — Lifecycle commands (recommended)

The fastest path through a project uses these 6 lifecycle commands in order:

| Command | What it does | Maps to phases |
|---------|--------------|----------------|
| `/spec` | Define business problem, data sources, contracts | Phase 0, 1 |
| `/plan` | Design architecture, choose tools, set up environment | Phase 2, 3 |
| `/build` | Implement ingestion + transformation + tests | Phase 4, 5 |
| `/validate` | Run data quality checks, validate contracts | Phase 5, 6 |
| `/review` | Peer review architecture, code, security, governance | All phases |
| `/ship` | Deploy, orchestrate, document, hand off | Phase 7, 8, 9 |

Each command in `commands/` has step-by-step instructions, output requirements, and a "next step" pointer.

## How to use this skill

**Option A — Lifecycle commands** (fast, recommended for most users):
1. Run `/spec` → `/plan` → `/build` → `/validate` → `/review` → `/ship` in order.
2. Each command tells you what inputs it needs and what outputs to produce.
3. Use `phases/phase-N-*.md` for deep-dive methodology when a command isn't detailed enough.

**Option B — Phase-by-phase** (methodical, best for learning):
1. Identify which phase the user is in (or starting from).
2. Read the relevant `phases/phase-N-*.md` file for methodology guidance.
3. When concrete code/config is needed, reference `implementation/`:
   - `implementation/orchestration/` — Airflow DAG patterns, testing DAGs
   - `implementation/transformation/` — dbt models, macros, incremental strategies
   - `implementation/quality/` — Great Expectations, data contracts, dbt tests
   - `implementation/optimization/` — Spark partitioning, joins, memory tuning
   - `implementation/pipeline/` — end-to-end pipeline architecture patterns
4. For specialized AI agent assistance, load agent personas from `agents/`.
5. Use `templates/` for machine-verifiable YAML contracts and plans.
6. Use `references/anti-patterns.md` to check for common mistakes.

Regardless of path, always flag if something suggests a feedback loop back to an earlier phase.

## Phase map

| #   | Phase                              | Core question it answers                                                                             |
| --- | ---------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 0   | Discover                           | Who needs this data, what decision does it enable, what does "done" look like?                       |
| 1   | Data source evaluation & contracts | What sources exist, and what exactly can I rely on from each?                                        |
| 2   | Architecture design                | How do sources become a queryable analytics layer, and with what layers?                             |
| 3   | Environment setup                  | What's the minimal reproducible environment to start building?                                       |
| 4   | Ingestion (Bronze)                 | How does raw data get from source into storage, reliably?                                            |
| 5   | Transformation + testing           | How does raw data become trustworthy, analysis-ready tables, and how do I know the logic is correct? |
| 6   | Data quality & observability       | Is the data itself — at runtime — within expected bounds?                                            |
| 7   | Serving layer                      | How does a stakeholder actually consume the answer?                                                  |
| 8   | Orchestration                      | How does this run automatically, reliably, on schedule?                                              |
| 9   | Governance, docs, CI/CD            | Is this maintainable, explainable, and credible to someone else?                                     |

See `phases/phase-0-discover.md` through `phases/phase-9-governance.md` for details on each. See `assets/business_problem_template.md` and `assets/data_contract_template.md` for fill-in-the-blank templates usable in any domain.

## Skill structure

```
DESKILL/
├── SKILL.md                         # Entry point, principles, navigation
├── README.md                        # Human-facing project overview
├── plugin.json                      # Plugin packaging
├── .gitignore
│
├── commands/                        # [CHÍNH] Lifecycle commands — fastest path
│   ├── spec.md                      # Define business problem, sources, contracts
│   ├── plan.md                      # Design architecture, environment setup
│   ├── build.md                     # Implement ingestion + transformation
│   ├── validate.md                  # Data quality checks + contract validation
│   ├── review.md                    # Architecture, code, security review
│   ├── ship.md                      # Deploy, orchestrate, document
│   ├── data-pipeline.md             # Pipeline architecture command (advanced)
│   └── data-driven-feature.md       # A/B testing orchestrator command
│
├── phases/                          # Deep-dive methodology (10 phases)
│   ├── phase-0-discover.md through phase-9-governance.md
│
├── implementation/                  # Code patterns by topic
│   ├── orchestration/airflow-patterns.md
│   ├── transformation/dbt-patterns.md
│   ├── quality/data-quality-patterns.md
│   ├── optimization/spark-patterns.md
│   └── pipeline/pipeline-patterns.md
│
├── templates/                       # Machine-verifiable YAML templates
│   ├── source-contract.yaml         # Data source contract
│   ├── backfill-plan.yaml           # Safe backfill plan
│   └── release-gate.yaml            # Release gate evidence
│
├── agents/                          # AI agent personas
│   ├── data-engineer.md
│   └── backend-architect.md
│
├── references/                      # Reference guides
│   ├── anti-patterns.md             # Common mistakes to avoid
│   └── phase-*.md                   # (from old references/)
│
└── assets/                          # Fill-in templates
    ├── business_problem_template.md
    └── data_contract_template.md
```

## Time-optimization with AI (applies across all phases)

- **AI accelerates fastest on:** boilerplate code (Docker Compose, DAG skeletons, dbt model scaffolding), summarizing long API docs, generating test cases and edge cases, writing documentation/README content, and debugging when given a concrete error message.
- **AI should not autonomously decide:** business-critical thresholds (what counts as an anomaly), overall architecture tradeoffs, or which data quality issues are acceptable to ship with — these need domain judgment the user has and the model doesn't.
- **Always verify AI-summarized API/library documentation** against the live source before building on it — training data can be stale relative to a fast-moving API.
- **Budget a short feedback-loop check after every phase**: "does this phase's output change anything decided in an earlier phase?" This single habit is what separates an iterative process from a linear one that silently accumulates rework.
