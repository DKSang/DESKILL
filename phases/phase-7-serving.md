# Phase 7 — Serving Layer

## Goal
Turn the analytics-ready table into something a stakeholder can actually consume — answering the exact questions defined in Phase 0, nothing more, nothing decorative.

## Generic activities
1. Choose a serving method proportional to project scope: a lightweight dashboarding tool (e.g. Streamlit, Metabase) is usually sufficient and faster to build than a heavier BI tool for a solo portfolio project — reserve enterprise BI tools for when the project specifically targets that skill.
2. Build one view per analytical question from Phase 0 — resist the urge to add unrelated charts "because the data supports it." Every view should trace back to a stated question.
3. Prioritize correctness and clarity over visual polish — a plain chart that answers the right question beats a polished one that doesn't.
4. Capture a demo (screenshots or a short recording) for portfolio use, since not every reviewer will run the project themselves.

## Output
A working, locally runnable interface (or static export) plus a demo artifact for sharing.

## AI usage tips
- AI is efficient for the repetitive parts: dashboard boilerplate, chart code. Spend your own judgment on picking the right chart type for each specific question rather than delegating that choice.

## Feedback loop triggers
If a Phase 0 question can't be cleanly visualized from the Gold table as built, that's a signal to revisit Phase 5's aggregation grain — not a reason to over-engineer the serving layer to compensate.

## Implementation patterns
- `agents/backend-architect.md` — API design patterns if building a custom serving API
- `commands/data-pipeline.md` — architecture documentation section for serving layer design
