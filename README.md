<p align="center">
  <img src="https://raw.githubusercontent.com/anomalyco/DESKILL/main/Wordmark.png" alt="DESKILL" width="480"/>
</p>

<p align="center">
  <em>Data Engineering Project Roadmap — từ business problem đến production pipeline</em>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/deskill-de"><img src="https://img.shields.io/npm/v/deskill-de" alt="npm version"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/npm/l/deskill-de" alt="MIT License"/></a>
  <a href="https://www.npmjs.com/package/deskill-de"><img src="https://img.shields.io/npm/dt/deskill-de" alt="npm downloads"/></a>
</p>

---

## Tại sao DESKILL?

Xây dựng data pipeline thường rơi vào 2 cái bẫy:
- **Bẫy 1:** Nhảy thẳng vào chọn tool, quên mất business problem cần giải
- **Bẫy 2:** Có methodology nhưng không biết implement code thế nào

DESKILL giải quyết cả hai: **process methodology** (dạy tư duy, thứ tự, feedback loops) kết hợp với **code patterns production** (Airflow, dbt, Spark, Great Expectations) trong một framework thống nhất.

---

## Cài đặt

```bash
# Cách 1: npm (recommended)
npx deskill-de install

# Cách 2: Clone repo
git clone https://github.com/anomalyco/DESKILL.git
```

---

## Quick Start — 14 Sequential Skills

Chạy theo thứ tự, mỗi skill gợi ý skill tiếp theo:

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

## Cấu trúc repo

```
DESKILL/
├── SKILL.md                        # Entry point — principles, skill flow, phase map
├── plugin.json                     # Plugin manifest
├── package.json                    # npm package + CLI installer
├── commands/                       # Orchestrator commands: data-pipeline, data-driven-feature
├── skills/                         # 14 atomic skills (1 deliverable each)
│   ├── problem/                    #   Business problem definition
│   ├── sources/                    #   Source evaluation + data contracts
│   ├── arch/                       #   Pipeline architecture design
│   ├── schema/                     #   DW schema (Fact/Dim tables)
│   ├── env/                        #   Development environment setup
│   ├── ingest/                     #   Bronze ingestion layer
│   ├── transform/                  #   Silver + Gold transformations
│   ├── test/                       #   Test suite (schema + logic)
│   ├── dq/                         #   Runtime data quality checks
│   ├── contract-check/             #   Data vs contract validation
│   ├── dag/                        #   Orchestration DAG
│   ├── serve/                      #   Serving layer (dashboard/API)
│   ├── ci/                         #   CI/CD (GitHub Actions)
│   └── docs/                       #   Documentation
├── phases/                         # Deep-dive methodology (10 phases)
├── implementation/                 # Code patterns: Airflow, dbt, Spark, GE
└── agents/                         # AI agent personas: data-engineer, backend-architect
```

---

## Tính năng chính

- **Domain-agnostic:** Weather, e-commerce, finance, IoT, logistics — dùng được hết
- **Tool-agnostic:** Không mandate stack, chỉ dẫn chọn tool theo scale và mục tiêu
- **Iterative:** Phases có feedback loops — phát hiện ở phase sau có thể quay lại sửa phase trước
- **AI-native:** Designed để dùng với AI pair-engineer ở mọi phase
- **Production patterns:** Code examples từ Airflow, dbt, Spark, Great Expectations
- **Parallel by design:** Mỗi skill độc lập, chạy tuần tự với gợi ý skill tiếp theo

---

## So sánh với các framework khác

| | DESKILL | wshobson/agents | vaquarkhan/agent-skills |
|---|---|---|---|---|
| Methodology | 10-phase roadmap + 14 sequential skills | ❌ | ❌ (chỉ skill rời rạc) |
| Code patterns | Airflow, dbt, Spark, GE | Airflow, dbt, Spark, GE | ❌ |
| AI agent personas | data-engineer + backend-architect | data-engineer + backend-architect | ❌ |
| Skill graph | 14 skills, mỗi skill gợi ý skill tiếp theo | ❌ | ❌ |
| Anti-patterns | ~30 common mistakes cataloged | ❌ | ✅ (trong 73 skills) |
| Templates | 14 skill assets | ❌ | 8 YAML |
| Packaging | npm + CLI + CI/CD + plugin | Plugin-only | Full IDE integration |

---

## Credits

- **Process methodology:** Inspired by *Fundamentals of Data Engineering* (Reis & Housley)
- **Implementation patterns:** Adapted from [wshobson/agents](https://github.com/wshobson/agents) (MIT)
- **Packaging pattern:** Inspired by [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)

---

## License

MIT © DESKILL
