---
name: de-problem
description: "Define the business problem, persona, and analytical questions for a data engineering project before choosing tools or writing code. Use when the user says 'I want to build a pipeline for...', 'where do I start', 'what should I build first', or jumps straight to tools without a clear problem statement."
---

# Skill: Define Business Problem

## Purpose

Determine **who needs what, to make what decision** before touching any tools. This is the cheapest step to get wrong and the most expensive to skip — a pipeline that runs beautifully but answers no useful questions is a failed pipeline.

## When to stop at this skill

Only move to `/sources` when `docs/business_problem.md` has **all 5 sections** listed in DONE WHEN.

## Steps

### Step 1 — Identify Persona

Ask (or infer from the user's description): *"Who will look at the output of this pipeline, and what will they do differently because of it?"*

Write in this format:
> "A **[role]** at a **[type of organization]** needs to make decisions about **[specific problem]**."

If the user doesn't know their persona, ask directly: *"Who is the end consumer — yourself for a portfolio project, a manager reading reports, or another system consuming the data?"*

### Step 2 — Write Problem Statement (3 parts)

| Part | Content |
|------|---------|
| **Context** | What are users relying on today without this pipeline? (spreadsheet, nothing, manual process?) |
| **Problem** | What question/decision is currently hard or impossible to answer, and why? List 1–3 specific pain points. |
| **Solution** | What will this pipeline provide — sources, layers, serving output — at a level a non-technical person can understand. |

### Step 3 — Define 3–5 Analytical Questions

Each question must:
- Be **specific enough to write SQL for today**, even without data yet.
- Have a clear entity, metric, threshold, and timeframe.
- Not be vague like "understand trends" — use "top 10 [entities] with [metric] change > [X]% in [Y] days".

If the user gives vague questions, stress-test them: *"If I were to write SQL for this question right now, what would the entity, metric, threshold, and timeframe be?"*

### Step 4 — Define Success Metric

**NOT**: "Pipeline runs without errors".

**MUST BE**: "Correctly answers questions 1–3 with data no older than [X] [hours/days]."

Example: *"Dashboard shows correct top movers daily with data lag ≤ 1 business day."*

### Step 5 — Document Constraints

Always be explicit about:
- **Budget**: $0 or a specific number.
- **Time available**: X hours/week for Y weeks.
- **Domain gaps**: What knowledge needs to be learned.

## Output format

Create `docs/business_problem.md` using the template below. For a fill-in version, see `skills/problem/assets/business_problem_template.md`.

```markdown
# Business Problem — [Project Name]

## Context
[What are users doing today before this pipeline exists?]

## Problem
1. [Specific pain point 1]
2. [Specific pain point 2]

## Solution
[1-paragraph pipeline description: sources → layers → serving output, in non-technical language]

## Persona
- **Who**: [role / organization type]
- **They need**: [specific decision or action this data enables]

## Analytical Questions
1. [Question specific enough to write SQL — entity + metric + threshold/timeframe]
2. [...]
3. [...]
4. [...]  ← optional
5. [...]  ← optional

## Success Metric
[Not "pipeline runs". Must tie to answering the questions above within a specific freshness window.]

## Constraints
- Budget: [e.g. $0]
- Time: [e.g. 10h/week × 4 weeks]
- Domain gaps: [...]
```

## DONE WHEN

File `docs/business_problem.md` exists and has:
- [ ] Persona written as "Who at where needs what decision".
- [ ] Problem statement with 3 parts: Context + Problem + Solution.
- [ ] 3–5 analytical questions specific enough to write SQL.
- [ ] Success metric is NOT "pipeline runs".
- [ ] Constraints specify budget + time.

## Next Step

After done → run `/sources` to evaluate each data source and create contracts.

If a later phase reveals that no source can answer a question, revisit this skill and revise the question rather than forcing the source.

## References

- Template: `skills/problem/assets/business_problem_template.md`
- Phase deep-dive: `phases/phase-0-discover.md`
- Next phase: `phases/phase-1-data-contracts.md`
