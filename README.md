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

## Quick Start — 6 Lifecycle Commands

Chạy theo thứ tự, mỗi command có hướng dẫn step-by-step:

```mermaid
flowchart LR
    A[/spec] --> B[/plan]
    B --> C[/build]
    C --> D[/validate]
    D --> E[/review]
    E --> F[/ship]
```

| Command | Làm gì | Output |
|---------|--------|--------|
| `/spec` | Define business problem + data contracts | `docs/business_problem.md` + `contracts/*.yaml` |
| `/plan` | Design architecture + set up environment | `docs/architecture.md` + Docker Compose + dbt init |
| `/build` | Implement ingestion + transformation | Bronze/Silver/Gold tables + test suite |
| `/validate` | Data quality checks + contract validation | Quality report + release gate evidence |
| `/review` | Peer review architecture, code, security | Review report |
| `/ship` | Deploy, orchestrate, document, CI/CD | Production pipeline + README + lineage |

---

## Cấu trúc repo

```
DESKILL/
├── SKILL.md                        # Entry point — principles, navigation, phase map
├── package.json                    # npm package + CLI installer
├── commands/                       # 6 lifecycle commands + 2 orchestrator commands
├── phases/                         # Deep-dive methodology (10 phases)
├── implementation/                 # Code patterns: Airflow, dbt, Spark, GE
├── templates/                      # YAML templates: contracts, backfill, release gate
├── agents/                         # AI agent personas: data-engineer, backend-architect
├── references/                     # Anti-patterns + legacy phase docs
└── assets/                         # Fill-in-the-blank templates
```

---

## Tính năng chính

- **Domain-agnostic:** Weather, e-commerce, finance, IoT, logistics — dùng được hết
- **Tool-agnostic:** Không mandate stack, chỉ dẫn chọn tool theo scale và mục tiêu
- **Iterative:** Phases có feedback loops — phát hiện ở phase sau có thể quay lại sửa phase trước
- **AI-native:** Designed để dùng với AI pair-engineer ở mọi phase
- **Production patterns:** Code examples từ Airflow, dbt, Spark, Great Expectations
- **Safe operations:** Backfill plan template + release gate + anti-patterns reference

---

## So sánh với các framework khác

| | DESKILL | wshobson/agents | vaquarkhan/agent-skills |
|---|---|---|---|
| Methodology | 10-phase roadmap + 6 lifecycle commands | ❌ | ❌ (chỉ skill rời rạc) |
| Code patterns | Airflow, dbt, Spark, GE | Airflow, dbt, Spark, GE | ❌ |
| AI agent personas | data-engineer + backend-architect | data-engineer + backend-architect | ❌ |
| Lifecycle commands | /spec → /plan → /build → /validate → /review → /ship | ❌ | ❌ |
| Anti-patterns | ~30 common mistakes cataloged | ❌ | ✅ (trong 73 skills) |
| Templates | 3 YAML + 2 markdown | ❌ | 8 YAML |
| Packaging | npm + CLI + CI/CD | Plugin-only | Full IDE integration |

---

## Credits

- **Process methodology:** Inspired by *Fundamentals of Data Engineering* (Reis & Housley)
- **Implementation patterns:** Adapted from [wshobson/agents](https://github.com/wshobson/agents) (MIT)
- **Lifecycle commands + templates:** Inspired by [vaquarkhan/data-engineering-agent-skills](https://github.com/vaquarkhan/data-engineering-agent-skills)
- **Packaging pattern:** Inspired by [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)

---

## License

MIT © DESKILL
