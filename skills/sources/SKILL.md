---
name: de-sources
description: "Evaluate data sources and produce machine-verifiable source contracts before writing any ingestion code. Use this skill when the user asks 'what data sources should I use', 'how do I document my API', 'is this API reliable enough', 'help me write a data contract', 'I found this API, can I use it?', 'how do I check rate limits', 'how do I validate my source', or has a business problem defined and needs to lock down sources before building. Also use when the user wants to start coding ingestion without first documenting sources — redirect here first."
---

# Skill: Evaluate Sources & Create Data Contracts

## Purpose

Before writing a single line of ingestion code, you must know exactly **how much you can trust each source** — what the actual schema is, whether rate limits are sufficient, whether join keys match. This skill produces a data contract — a written commitment, not a bookmark.

## When to stop at this skill

Only move to `/arch` when every source has a `contracts/source-<name>.yaml` file with all 6 fields in DONE WHEN.

---

## Steps

### Step 1 — List candidate sources

From `docs/business_problem.md` (analytical questions), list **every** possible source. For each source, answer:
- Access method: REST API / bulk file / database / scrape (prefer API or bulk export, avoid scrape)
- Auth: none / API key / OAuth / service account
- Cost: $0 or a specific number — if unsure, test before committing

### Step 2 — Get the real schema (not from docs)

> **Important**: Documentation is often out of date. You must call the live API and record the schema from the actual response.

Run the probe script (see `scripts/probe_source.py`) or call manually:
```bash
curl -H "Authorization: Bearer $API_KEY" "https://api.example.com/endpoint?limit=1"
```

Paste the response into the contract. This is the real schema — not the schema from docs.

### Step 3 — Calculate rate limit math

Never write "should be fine." Calculate concretely:

```
Volume per run = number of entities × number of fields × number of runs/day
Rate limit = X calls/minute (from docs + real-world verification)
Margin = Rate limit / Volume per run → must be > 1
```

Example:
```
10,000 stocks × 1 call/stock × 1 run/day = 10,000 calls/day
Free tier: 500 calls/day → NOT ENOUGH → need bulk endpoint or paid tier
```

### Step 4 — Determine query schedule

Each source needs: **when to query, at what frequency?**

| Pattern | When to use |
|---------|-------------|
| Monthly batch | Data rarely changes (company list, market status) |
| Daily batch | Data updates every day (OHLC candles, daily reports) |
| Intraday batch | Data updates within the day (news sentiment, real-time prices) |
| On-demand | Static data (reference tables) |

### Step 5 — Verify join keys

If multiple sources need to be joined, verify clearly:
- What is the common key? (ticker symbol, product ID, user ID, timestamp grain)
- Do the keys actually match? (case sensitivity, format differences?)
- If there's no natural key → a mapping table is needed → document in the contract

### Step 6 — Assess breaking-change risk

| Risk | Signs |
|------|-------|
| **Low** | Versioned API (v1, v2), official docs, stable company |
| **Medium** | Not versioned but official, infrequent changes |
| **High** | Unofficial / undocumented / scraping |

---

## Output format

Create `contracts/source-<name>.yaml` for each source:

```yaml
# contracts/source-<name>.yaml
apiVersion: datacontract.com/v1.0.0
kind: DataContract
metadata:
  name: <source-name>           # e.g. "polygon-ohlc"
  version: 1.0.0
  owner: <owner-name>
  lastVerified: <YYYY-MM-DD>    # Date of most recent live call test

info:
  title: <Display Name>
  description: <1-line description>
  purpose: <Which analytical question this serves>

access:
  method: <api|file|database|scrape>
  authType: <none|api-key|oauth|service-account>
  endpoint: <URL or path>
  docsUrl: <Link to docs>

terms:
  cost: <$0 or specific amount>
  rateLimit: <X calls/unit>
  freeQuota: <free tier limit if any>

schedule:
  frequency: <monthly|daily|intraday|on-demand>
  cronExpression: <cron string, e.g. "0 0 * * *">
  reasoning: <Why this frequency was chosen>

volume:
  callsPerRun: <number>
  math: "<specific calculation>"
  fitsWithinLimit: <true|false>
  margin: <X>x   # callsPerRun / rateLimit, must be > 1

schema:
  # Schema from LIVE CALL — not from docs
  type: object
  sampleResponse: |
    <paste actual response>
  properties:
    <field-name>:
      type: <string|integer|number|boolean|datetime>
      description: <description>
      required: <true|false>
      pii: <true|false>

joinKey:
  field: <field name>
  matchesWith:
    - source: <other source>
      field: <corresponding field>
  verified: <true|false>
  notes: <format differences, mapping needed, etc.>

breakingChangeRisk: <low|medium|high>
breakingChangeReasoning: <reasoning>

quality:
  checks:
    - row_count > 0
    - missing_count(<pk-field>) = 0
    - freshness(<timestamp-field>) < <SLA>

sla:
  freshness: <max age, e.g. "24h">
```

---

## DONE WHEN

For each source, `contracts/source-<name>.yaml` has:
- [ ] Schema from live call (not from docs)
- [ ] Rate limit math calculated — `fitsWithinLimit: true`
- [ ] `schedule.frequency` and `cronExpression` clearly defined
- [ ] `joinKey` verified against other sources (or "n/a" with reason)
- [ ] `breakingChangeRisk` with reasoning
- [ ] `lastVerified` is an actual test date

---

## Feedback loop

If a source cannot provide a required field for an analytical question → go back to `docs/business_problem.md` and drop or revise that question — **do not force-fix it at ingestion time**.

## Next Step

After all contracts are done → run `/arch` to design your pipeline architecture and choose your tool stack.

> Scripts: `scripts/probe_source.py` — live-test a source, print actual schema.
> Reference: `phases/phase-1-data-contracts.md`
