---
name: de-serve
description: "Build the serving layer so stakeholders can consume the analytics output from the data pipeline. Use this skill when the user says 'build a dashboard', 'create a serving layer', 'visualize my data', 'expose my Gold tables', 'build a BI view', 'make a Streamlit app', 'create an API for my data', 'show my analytical results', or has Gold tables and needs to answer the analytical questions from the business problem in a consumable format."
---

# Skill: Build Serving Layer

## Purpose

Turn Gold tables into something **stakeholders can read and make decisions from**. Every analytical question from `docs/business_problem.md` must have at least 1 view/chart answering it. Correctness > polish — 1 correct chart beats 10 pretty charts that answer nothing.

## When to stop at this skill

Done when every analytical question has ≥1 working view/chart, and the demo is captured (screenshot or recording).

---

## Steps

### Step 1 — Map questions → views

From `docs/business_problem.md`, list each analytical question and the appropriate chart type:

| Question | Chart type | Reason |
|---------|-----------|--------|
| "Trend over time" | Line chart | Shows trend over time |
| "Compare entities" | Bar chart | Compare values across categories |
| "Distribution" | Histogram / box plot | Shows value distribution |
| "Correlation" | Scatter plot | Relationship between 2 metrics |
| "Ranking / Top N" | Horizontal bar | Clear ranking |
| "Part of whole" | Pie / treemap | Proportion of total |

**Rule**: Each chart must answer exactly 1 question. Don't add charts "just because the data is there."

### Step 2 — Choose serving method based on scope

| Method | When to use |
|--------|-------------|
| **Streamlit** | Portfolio project, Python-first, quick to deploy |
| **Metabase / Superset** | Need SQL editor, non-technical users |
| **Jupyter Notebook** | Analysis-heavy, no shared dashboard needed |
| **REST API (FastAPI)** | Data needs to be served to another app |
| **Static exports** | Simplest — PDF/HTML report |

> Portfolio projects: **Streamlit is the default** — deploy with one command, Python, good-looking enough.

### Step 3 — Build 1 view per question

Each view/page must have:
- **Title** = the analytical question being answered
- **1 primary chart** answering the question
- **Filters** only when necessary (date range, entity)
- **Data source label** — when data was last updated

### Step 4 — Capture demo

Capture so portfolio reviewers don't need to run the project themselves:
```bash
# Screenshot
# Recording: OBS / ShareX / Loom
```

---

## Output

### If using Streamlit — `serving/app.py`:

```python
"""
serving/app.py — Analytics dashboard.

Answers analytical questions from docs/business_problem.md.
Run: streamlit run serving/app.py
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ─── Setup ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="<Project> Analytics",
    page_icon="chart",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_resource
def get_conn():
    return duckdb.connect("data/warehouse.duckdb", read_only=True)

conn = get_conn()

def query(sql: str) -> pd.DataFrame:
    return conn.execute(sql).df()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")
date_range = st.sidebar.date_input(
    "Date range",
    value=(datetime.today() - timedelta(days=30), datetime.today()),
    max_value=datetime.today(),
)
start_date, end_date = date_range[0], date_range[1] if len(date_range) > 1 else date_range[0]

# Data freshness indicator
latest = query("SELECT MAX(_loaded_at) as latest FROM fct_candles").iloc[0]["latest"]
st.sidebar.caption(f"Data updated: {latest}")

# ─── Page: Question 1 ─────────────────────────────────────────────────────────
st.title("<Project> Analytics Dashboard")

# Analytical Question 1
st.header("Question 1: <Question title>")
col1, col2 = st.columns([3, 1])

with col1:
    df = query(f"""
        SELECT
            t.date,
            c.ticker,
            f.<measure>
        FROM fct_<fact> f
        JOIN dim_companies c ON f.company_id = c.company_id
        JOIN dim_time t ON f.time_id = t.time_id
        WHERE t.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY t.date
    """)

    fig = px.line(df, x="date", y="<measure>", color="ticker",
                  title="<Chart title>",
                  labels={"<measure>": "<Unit>", "date": "Date"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric("Avg <measure>", f"{df['<measure>'].mean():.2f}")
    st.metric("Max <measure>", f"{df['<measure>'].max():.2f}")

st.divider()

# Analytical Question 2
st.header("Question 2: <Question title>")

df2 = query(f"""
    SELECT ...
    FROM fct_<fact2> f
    ...
""")

fig2 = px.bar(df2, x="<category>", y="<measure>",
              title="<Title>",
              orientation="h")
st.plotly_chart(fig2, use_container_width=True)
```

### If using FastAPI (serving for other apps):

```python
# serving/api.py
from fastapi import FastAPI, Query
import duckdb
from datetime import date

app = FastAPI(title="<Project> Data API", version="1.0.0")
conn = duckdb.connect("data/warehouse.duckdb", read_only=True)

@app.get("/api/v1/<endpoint>")
def get_data(
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    limit: int = Query(default=100, le=1000),
):
    """<Describe which analytical question this endpoint answers>"""
    df = conn.execute("""
        SELECT ...
        FROM fct_<fact>
        WHERE date BETWEEN ? AND ?
        LIMIT ?
    """, [start_date, end_date, limit]).df()
    return df.to_dict(orient="records")
```

---

## DONE WHEN

- [ ] Every analytical question from `docs/business_problem.md` has ≥1 working view/chart
- [ ] Title of each view = the question it answers (not "Dashboard")
- [ ] Data freshness label present (users know how recent the data is)
- [ ] Dashboard runs locally with `streamlit run` or `uvicorn`
- [ ] Demo captured (screenshot or recording)

---

## Next Step

After done → run `/ci` to set up CI/CD for automated testing.

> Reference: `phases/phase-7-serving.md`
