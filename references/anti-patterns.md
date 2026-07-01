# Data Engineering Anti-Patterns

Common anti-patterns to recognize and avoid. Each entry names the anti-pattern, why it's harmful, and the healthy alternative.

## Validation & Testing

| Anti-Pattern | Why It's Harmful | Healthy Alternative |
|---|---|---|
| **Testing only in production** | Data issues discovered by consumers erodes trust | Test in dev/staging with representative data |
| **No schema tests** | Silent data corruption propagates downstream | Add not-null, unique, accepted-values on key columns |
| **Testing everything equally** | Test maintenance becomes a burden | Focus on critical columns and business logic |
| **Ignoring test warnings** | Warnings are early signals of real failures | Treat warnings as actionable items, not noise |

## Data Modeling & Storage

| Anti-Pattern | Why It's Harmful | Healthy Alternative |
|---|---|---|
| **One Big Table everything** | No separation of concerns, hard to maintain | Medallion architecture (Bronze/Silver/Gold) |
| **Skipping staging layer** | Raw-to-mart transformations become brittle | Always stage data before business logic |
| **No naming conventions** | Impossible to navigate without tribal knowledge | Prefix layers: stg_, int_, dim_, fct_ |
| **Drop nulls without investigation** | Silent data loss hides upstream problems | Explicitly handle nulls: default, flag, or investigate |

## Pipeline Design

| Anti-Pattern | Why It's Harmful | Healthy Alternative |
|---|---|---|
| **One script handles all sources** | Tight coupling, one source change breaks everything | One ingestion script per source |
| **No retry logic** | Transient failures cause pipeline breaks | Add exponential backoff retry |
| **Full refresh every run** | Wastes time and resources on unchanged data | Incremental loading with watermark columns |
| **No dead letter queue** | Bad records block the entire pipeline | Route invalid records to DLQ for investigation |
| **Hardcoded dates** | Breaks replay, catchup, and backfill | Use execution date / {{ ds }} macros |

## Orchestration

| Anti-Pattern | Why It's Harmful | Healthy Alternative |
|---|---|---|
| **depends_on_past=True** | Creates sequential bottlenecks | Idempotent tasks that can run independently |
| **No task timeouts** | Zombie tasks consume resources forever | Set timeouts on every task |
| **List 4 orchestrators "to compare later"** | Analysis paralysis, nothing gets built | Pick one, build, iterate |
| **Scheduling faster than source updates** | Wasted compute on unchanged data | Match schedule to real source update frequency |

## Data Quality & Governance

| Anti-Pattern | Why It's Harmful | Healthy Alternative |
|---|---|---|
| **Testing = Data Quality** | Misses runtime data anomalies | Testing validates logic (code-change time); DQ validates data (runtime) |
| **No freshness checks** | Stale data silently poisons downstream decisions | Monitor source freshness with alert thresholds |
| **No data lineage** | Impossible to trace a wrong number back to its root | Generate lineage (dbt docs, DataHub, OpenLineage) |
| **Credentials in code** | Security incident waiting to happen | Use `.env` + secrets manager, never commit secrets |

## Operations

| Anti-Pattern | Why It's Harmful | Healthy Alternative |
|---|---|---|
| **Backfill without a plan** | Data corruption, no rollback path | Always write a backfill plan with scope, safeguards, validation, rollback |
| **No monitoring on initial deploy** | First failure is invisible | Add monitoring and alerting from day one |
| **Silent partial failure** | Some data missing, no one knows | Fail loudly, alert immediately, halt on critical failures |
| **No cost awareness** | Cloud bills grow without understanding why | Document cost at each layer, set budgets |

## Governance & Security

| Anti-Pattern | Why It's Harmful | Healthy Alternative |
|---|---|---|
| **PII in analytics layer** | Compliance violation, reputational damage | Mask or aggregate PII before Gold layer |
| **No access control documentation** | New team members don't know who can access what | Document access model early |
| **Skip cost analysis "because it's free-tier"** | No understanding of production costs | Always note: "what would this cost at 10x scale?" |

## How to Use This Reference

When reviewing a pipeline (during `/review` or Phase 9), check each anti-pattern category:
1. Scan for each anti-pattern name in your code/config
2. If found, apply the healthy alternative
3. If choosing to keep it, document the rationale explicitly
