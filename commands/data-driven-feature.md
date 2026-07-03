---
description: "Build features guided by data insights, A/B testing, and continuous measurement"
argument-hint: "<feature description> [--experiment-type ab|multivariate|bandit] [--confidence 0.90|0.95|0.99]"
---

# Data-Driven Feature Development Orchestrator

> **Scope note:** This is an **extension command**, not part of the 14-skill DESKILL DE pipeline chain (`/problem → /docs`). It orchestrates product feature experimentation (A/B testing, ML model rollouts) and may consume outputs from a DESKILL-built pipeline (Gold tables, serving API). Use it after `/docs` when the pipeline feeds a feature experimentation workflow.

## CRITICAL BEHAVIORAL RULES

1. **Execute steps in order.** Do NOT skip ahead, reorder, or merge steps.
2. **Write output files.** Each step MUST produce its output file in `.data-driven-feature/` before the next step begins.
3. **Stop at checkpoints.** When you reach a `PHASE CHECKPOINT`, you MUST stop and wait for explicit user approval before continuing.
4. **Halt on failure.** If any step fails, STOP immediately. Present the error and ask the user how to proceed.
5. **Never enter plan mode autonomously.** This command IS the plan.

## Pre-flight Checks

Check if `.data-driven-feature/state.json` exists. If it exists with `"in_progress"`, ask to resume or start fresh.

Initialize `.data-driven-feature/state.json`:

```json
{
  "feature": "$ARGUMENTS",
  "status": "in_progress",
  "experiment_type": "ab",
  "confidence_level": 0.95,
  "current_step": 1,
  "current_phase": 1,
  "completed_steps": [],
  "files_created": [],
  "started_at": "ISO_TIMESTAMP",
  "last_updated": "ISO_TIMESTAMP"
}
```

Parse `$ARGUMENTS` for `--experiment-type` and `--confidence` flags. Use defaults if not specified.

---

## Phase 1: Data Analysis & Hypothesis (Steps 1-3)

### Step 1: Exploratory Data Analysis

Analyze existing user behavior data, identify patterns and opportunities. Segment users by behavior and engagement patterns. Calculate baseline metrics for key indicators.

Save to `.data-driven-feature/01-eda-report.md`.

### Step 2: Business Hypothesis Development

Define clear success metrics and expected impact on key business KPIs. Identify target user segments and minimum detectable effects. Create measurable hypotheses using ICE or RICE prioritization.

Save to `.data-driven-feature/02-hypotheses.md`.

### Step 3: Statistical Experiment Design

Calculate required sample size for statistical power. Define control and treatment groups with randomization strategy. Plan for multiple testing corrections. Consider Bayesian A/B testing approaches.

Save to `.data-driven-feature/03-experiment-design.md`.

---

## PHASE CHECKPOINT 1

Present analysis and experiment design for review. Ask user to approve before proceeding.

---

## Phase 2: Architecture & Instrumentation (Steps 4-6)

### Step 4: Feature Architecture Planning

Include feature flag integration (LaunchDarkly, Split.io, Optimizely). Design gradual rollout strategy with circuit breakers. Ensure clean separation between control and treatment logic.

Save to `.data-driven-feature/04-architecture.md`.

### Step 5: Analytics Instrumentation Design

Define event schemas for user interactions. Specify properties for segmentation and analysis. Design funnel tracking and conversion events.

Save to `.data-driven-feature/05-analytics-design.md`.

### Step 6: Data Pipeline Architecture

Include real-time streaming for live metrics. Design batch processing for detailed analysis. Plan data warehouse integration.

Save to `.data-driven-feature/06-data-pipelines.md`.

---

## PHASE CHECKPOINT 2

Present architecture, analytics design, and data pipelines for review.

---

## Phase 3: Implementation (Steps 7-9)

### Step 7: Backend Implementation

Implement feature with feature flag checks at decision points. Include event tracking for all user actions. Add performance metrics collection.

Save to `.data-driven-feature/07-backend.md`.

### Step 8: Frontend Implementation

Implement event tracking for all user interactions. Build A/B test variants with proper variant assignment. If no frontend component, skip and document why.

Save to `.data-driven-feature/08-frontend.md`.

### Step 9: ML Model Integration (if applicable)

Implement online inference with low latency. Set up A/B testing between model versions. Add model performance tracking and drift detection.

Save to `.data-driven-feature/09-ml-integration.md`.

---

## PHASE CHECKPOINT 3

Present implementation summary for review.

---

## Phase 4: Validation & Launch (Steps 10-13)

### Step 10: Analytics Validation

Test all event tracking in staging environment. Verify data quality and completeness. Validate funnel definitions.

Save to `.data-driven-feature/10-analytics-validation.md`.

### Step 11: Experiment Setup & Deployment

Set up feature flags with proper targeting rules. Configure traffic allocation. Create monitoring dashboards.

Save to `.data-driven-feature/11-experiment-setup.md`.

### Step 12: Gradual Rollout

Define rollout stages: internal → beta (1-5%) → gradual increase. Specify health checks and go/no-go criteria.

Save to `.data-driven-feature/12-rollout-plan.md`.

### Step 13: Security Review

Review for: OWASP Top 10, data privacy, PII handling, auth flaws, experiment manipulation risks.

Save to `.data-driven-feature/13-security-review.md`. Address critical/high findings before proceeding.

---

## PHASE CHECKPOINT 4

Present validation and launch readiness for review.

---

## Phase 5: Analysis & Decision (Steps 14-16)

### Step 14: Statistical Analysis

Define significance calculations with confidence intervals. Plan segment-level effect analysis. Use both frequentist and Bayesian approaches.

Save to `.data-driven-feature/14-analysis-plan.md`.

### Step 15: Business Impact Assessment

Define actual vs expected ROI calculation. Create decision framework for full rollout, iteration, or rollback.

Save to `.data-driven-feature/15-impact-framework.md`.

### Step 16: Optimization Roadmap

Define user behavior analysis methodology. Plan follow-up experiments and iteration cycles. Design continuous learning feedback loop.

Save to `.data-driven-feature/16-optimization-roadmap.md`.

---

## Completion

Update `state.json` with `status: "complete"`.

Present final summary with all output files and next steps:

1. Review all generated artifacts
2. Execute the rollout plan
3. Monitor using the configured dashboards
4. Run analysis after experiment completes
5. Make go/no-go decision using the impact framework
