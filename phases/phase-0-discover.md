# Phase 0 — Discover: Business Problem & Scope

## Goal
Establish who consumes this data, what decision it enables, and how success will be measured — before touching any tool. This is the cheapest phase to get wrong in and the most expensive to fix later if skipped.

## Generic activities
1. Name the persona(s): who looks at the output of this pipeline, and what do they do differently because of it? ("A [role] at a [type of organization] needs to [decision]" — fill in for the actual domain.)
2. Write a problem statement with three parts: **Context** (what's true today without this pipeline), **Problem** (what's missing/hard right now), **Solution** (what this project will provide).
3. Define 3-5 concrete analytical questions the final (Gold/serving) layer must be able to answer. These should be specific enough that you could write the SQL query for them today, even without data yet — e.g. not "understand trends" but "which [entity] had a [metric] change greater than [threshold] over [time window]?"
4. Define a success metric that is NOT "the pipeline runs" — it should be tied to correctly answering the questions above within an acceptable data-freshness window.
5. Note constraints up front: budget (usually $0 for portfolio projects), time available, and any domain knowledge gaps you'll need to fill.

## Output
`docs/business_problem.md` using `skills/problem/assets/business_problem_template.md` — problem statement, personas, the analytical questions, success metrics, constraints.

## Common failure mode
Jumping straight to "which tools should I use" without this phase produces a pipeline that runs cleanly but doesn't answer anything anyone needed — a very common trap for portfolio projects built backwards from "I want to learn tool X."

## AI usage tips
- Use Claude to stress-test the problem statement: "given this data source, can this analytical question actually be answered, or do I need something else?"
- Use Claude to sanity-check scope against time available — ask it to flag anything that looks like a multi-month project disguised as a weekend one.
- Don't ask AI to invent the business problem from scratch if this is a portfolio piece for a specific job target — the problem should reflect what that role's employers actually care about (ask Claude to research what data problems are common in that industry if unsure).

## Feedback loop triggers
Revisit this file when:
- Phase 1 reveals that no free/available source can answer one of the analytical questions (cut or revise the question, don't force it).
- Phase 4 or 5 reveals the real data can't support the question at the granularity assumed (e.g. data is monthly, question needs daily).

## DESKILL Skills
This phase is implemented by:
- `/problem` → `skills/problem/SKILL.md` — defines business problem, persona, analytical questions
- `/sources` → `skills/sources/SKILL.md` — evaluates data sources and creates contracts (crosses into Phase 1)

## Implementation patterns
- `implementation/pipeline/pipeline-patterns.md` — end-to-end architecture design patterns once scope is defined
- `skills/problem/assets/business_problem_template.md` — fill-in-the-blank template for this phase's output
