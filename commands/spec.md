---
description: "Define business problem, data sources, and contracts before building anything"
---

# Data Engineering — Spec Command

Define the scope, requirements, and contracts for your data engineering project. Run this command FIRST.

## Instructions

### 1. Define Business Problem

Answer these questions with the user:

- Who consumes this data? What decision does it enable?
- What's the current state (no pipeline, spreadsheets, manual process)?
- What are 3-5 concrete analytical questions the final layer must answer?
- What's the success metric (not "pipeline runs" — tied to business outcome)?
- What are the constraints (budget, time, domain knowledge gaps)?

Write the output to `docs/business_problem.md`.

### 2. Evaluate Data Sources

For each candidate source, document:

| Field | Required |
|-------|----------|
| Access method | REST API / bulk file / DB / scrape |
| Auth | none / API key / OAuth / service account |
| Cost | Must be $0 or state actual cost |
| Actual schema | Pull a real sample, not just docs |
| Update frequency | real-time / hourly / daily / monthly / static |
| Rate limits | Documented limit + your volume math |
| Breaking-change risk | low/medium/high with reasoning |
| Shared join key | Common key across sources if needed |

### 3. Create Source Contracts

Generate one `contracts/source-<name>.yaml` per source using the template:

```yaml
apiVersion: datacontract.com/v1.0.0
kind: DataContract
metadata:
  name: <source-name>
  version: 1.0.0
owner: <team-or-person>

info:
  title: <Source Display Name>
  description: <Description of the source>

servers:
  production:
    type: <snowflake|bigquery|s3|api|postgres>
    <connection-details>

schema:
  type: object
  properties:
    <field-name>:
      type: <string|integer|number|boolean|datetime>
      required: true
      unique: false
      pii: false
      description: <Field description>

quality:
  checks:
    - row_count > 0
    - missing_count(<pk-field>) = 0
    - freshness(<timestamp-field>) < 24h

sla:
  freshness: <required freshness>
```

### 4. Output

- `docs/business_problem.md` — Problem statement, personas, analytical questions
- `contracts/<source-name>.yaml` — One contract per source

### 5. Next Step

Run `/plan` to design architecture and choose tooling.

## Related skills

- `phases/phase-0-discover.md` — Detailed business problem methodology
- `phases/phase-1-data-contracts.md` — Detailed data contract guidance
- `assets/business_problem_template.md` — Fill-in-the-blank template
- `templates/source-contract.yaml` — Machine-verifiable contract
