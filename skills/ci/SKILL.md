---
name: de-ci
description: "Set up CI/CD for a data engineering project so tests run automatically on every code change. Use this skill when the user says 'set up CI', 'automate my tests', 'GitHub Actions for data pipeline', 'make tests run on PR', 'continuous integration', 'automate pipeline deployment', 'set up pre-commit hooks', or has a working test suite and wants it to run automatically without manual intervention."
---

# Skill: Setup CI/CD

## Purpose

Make the test suite run **automatically on every code change** — no need to remember to manually run tests before merging. CI is the proof-of-work for testing discipline: anyone reviewing a portfolio sees a green badge, not just a verbal claim.

## When to stop at this skill

Done when tests run automatically on PRs and the pipeline deploys reproducibly from a fresh clone.

---

## Steps

### Step 1 — Define CI triggers

| Trigger | When |
|---------|------|
| **On PR** | Run tests — block merge if they fail |
| **On push to main** | Run full test + optionally deploy |
| **On schedule** | Run DQ checks periodically |

### Step 2 — Define CI steps

```
1. Checkout code
2. Setup Python (pin version)
3. Cache dependencies (pip / uv)
4. Install dependencies
5. Run linting (optional but recommended)
6. Run unit tests (pytest)
7. Run dbt test (if using dbt)
8. Upload test results (optional)
```

### Step 3 — Secrets management

Don't hardcode API keys in CI. Use GitHub Secrets:
- Settings → Secrets → New repository secret
- Reference in the workflow: `${{ secrets.SOURCE_API_KEY }}`

---

## Output

### `.github/workflows/ci.yml`:

```yaml
# .github/workflows/ci.yml
# Runs the test suite on every PR and push to main.

name: CI — Data Pipeline Tests

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"

jobs:
  test:
    name: Run Test Suite
    runs-on: ubuntu-latest

    steps:
      # 1. Checkout
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Setup Python
      - name: Setup Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      # 3. Cache dependencies
      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      # 4. Install dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # 5. Lint (fail fast before running time-consuming tests)
      - name: Lint with ruff
        run: |
          pip install ruff
          ruff check ingestion/ quality/ serving/ transform/ tests/
        continue-on-error: true

      # 6. Unit tests
      - name: Run unit tests
        env:
          SOURCE_API_KEY: ${{ secrets.SOURCE_API_KEY }}
          MINIO_ROOT_USER: minioadmin
          MINIO_ROOT_PASSWORD: minioadmin
        run: |
          pytest tests/ -v --tb=short \
            --junitxml=test-results/pytest-results.xml \
            --cov=ingestion --cov=transform --cov=quality \
            --cov-report=xml:coverage.xml \
            --cov-report=term-missing

      # 7. dbt tests (if using dbt)
      - name: Run dbt tests
        if: hashFiles('dbt_project.yml') != ''
        env:
          DBT_PROFILES_DIR: .
        run: |
          dbt deps
          dbt build --profiles-dir . --target ci
        continue-on-error: false

      # 8. Upload test results
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            test-results/
            coverage.xml

  # Optional: Coverage report on PR
  coverage:
    name: Coverage Report
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'pull_request'

    steps:
      - uses: actions/checkout@v4
      - name: Download coverage
        uses: actions/download-artifact@v4
        with:
          name: test-results

      - name: Coverage comment on PR
        uses: orgoro/coverage@v3
        with:
          coverageFile: coverage.xml
          token: ${{ secrets.GITHUB_TOKEN }}
          thresholdAll: 0.7
```

### `dbt_profiles.ci.yml` (if using dbt):

```yaml
<project-name>:
  target: ci
  outputs:
    ci:
      type: duckdb
      path: /tmp/ci_warehouse.duckdb
      threads: 2
```

### `pytest.ini` or `pyproject.toml`:

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

---

## DONE WHEN

- [ ] `.github/workflows/ci.yml` committed to the repo
- [ ] Tests run automatically when a PR is created (check GitHub Actions tab)
- [ ] Secrets (API keys) in GitHub Secrets, not hardcoded in the workflow
- [ ] `requirements.txt` pins versions — CI installs the same as local
- [ ] CI passes on a fresh push (not just on the local machine)

---

## Next Step

After done → run `/docs` to write your project documentation.

> Asset: `skills/ci/assets/github_actions_template.yml`
