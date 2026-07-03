# Phase 9 — Governance, Documentation, CI/CD

## Goal
Make the project maintainable and credible to someone other than its author — this phase is often what separates a fresher-level project from a junior-level one in a portfolio review.

## Generic activities
1. Write a README covering: the business problem (from Phase 0), architecture diagram (from Phase 2), how to run it, and a demo screenshot/link.
2. Set up basic CI (e.g. GitHub Actions) to run the Phase 5 test suite automatically on every pull request — this demonstrates the testing discipline rather than just claiming it.
3. Generate/document data lineage if the transformation tool supports it natively (e.g. `dbt docs generate`) rather than building this by hand.
4. Even for a project run entirely locally/free, add a brief cost note: what would this cost to run in a cloud environment at this scale, and how would that change if scope grew 10x? This demonstrates cost-awareness even without an actual cloud bill.
5. Document access control considerations, even if trivial for a solo project (e.g. "credentials via `.env`, never committed; a production version would use a secrets manager").

## Output
A repository that a reviewer (or future employer) can understand, run, and trust within a few minutes of looking at it.

## AI usage tips
- This phase is low-risk for heavy AI use — README writing, docstrings, and CI config generation are all "describe what already exists" tasks where AI errors are easy to catch and low-stakes.

## Feedback loop triggers
If writing the README surfaces an architecture decision that's hard to justify in writing, that's a signal the decision itself (Phase 2) may need revisiting — clear documentation often exposes fuzzy thinking that was easy to skip past while building.

## DESKILL Skills
This phase is implemented by:
- `/ci` → `skills/ci/SKILL.md` — sets up CI/CD (GitHub Actions) to run tests automatically
- `/docs` → `skills/docs/SKILL.md` — writes README, data lineage, cost analysis

## Implementation patterns
- `implementation/transformation/dbt-patterns.md` — `dbt docs generate` for automated data lineage and model documentation
- `implementation/quality/data-quality-patterns.md` — data contract YAML specification for governance
- `commands/data-pipeline.md` — operations guide, deployment procedures, monitoring setup
- `commands/data-driven-feature.md` — experiment tracking and governance for feature development
