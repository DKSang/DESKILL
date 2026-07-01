---
description: "Peer review architecture, code quality, security, and governance"
---

# Data Engineering — Review Command

Review the pipeline before shipping. Run AFTER `/validate`.

## Instructions

### 1. Architecture Review

- [ ] Architecture matches the business problem from `/spec`
- [ ] Layer contracts (Bronze/Silver/Gold) are clear and enforced
- [ ] Tool choices are justified by scale and job-market fit
- [ ] Naming conventions are consistent
- [ ] Failure modes are documented

### 2. Code Quality Review

- [ ] Tests exist for non-trivial transformation logic
- [ ] No hardcoded secrets or connection strings
- [ ] Retry logic exists for external calls
- [ ] Logging is actionable (not just "got here")
- [ ] Dependencies are pinned and reproducible

### 3. Data Quality Review

- [ ] Quality checks cover: freshness, volume, schema, distribution
- [ ] Thresholds are calibrated with domain knowledge
- [ ] Alerts exist for quality failures
- [ ] Dead letter queue or equivalent exists for bad records

### 4. Security & Governance Review

- [ ] Credentials via `.env` (never committed)
- [ ] PII is identified and handled appropriately
- [ ] Access control is documented
- [ ] Cost implications are noted
- [ ] Data lineage is documented

### 5. Output

`docs/review-report.md` with:
- Items checked and status (pass/fail/na)
- Issues found with severity
- Recommendations for improvement

### 6. Next Step

If review passes → run `/ship`.
If issues found → fix and re-run `/validate`, then `/review` again.

## Related skills

- `phases/phase-9-governance.md` — Governance methodology
- `references/anti-patterns.md` — Common mistakes to check for
- `agents/data-engineer.md` — AI agent for review discussions
