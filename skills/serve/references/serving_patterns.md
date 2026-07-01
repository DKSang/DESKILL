# Serving Layer Patterns Reference
# Read this when: choosing serving approach or designing dashboard layout.
# Do NOT paste this entire file into SKILL.md — load on demand.

## 1. Choosing a Serving Method

| Method | Best for | Complexity | Deploy time |
|--------|----------|------------|-------------|
| **Streamlit** | Portfolio projects, Python-first teams, quick POC | Low | Minutes |
| **Metabase** | Non-technical users, SQL editor, self-hosted BI | Low-medium | Hours (setup) |
| **Apache Superset** | Open-source BI, SQL Lab, custom dashboards | Medium | Hours |
| **Grafana** | Metrics/time-series, ops dashboards | Medium | Hours |
| **Jupyter + nbconvert** | Analysis-heavy, reproducible reports | Low | Minutes |
| **FastAPI** | Data serving as API for other apps | Medium | Hours |
| **dbt Semantic Layer** | Metric definitions shared across tools | Medium-high | Days |

**Portfolio default**: Streamlit — installs with `pip install streamlit`, deploy with 1 command.

---

## 2. Dashboard Layout Principles

### One chart = one question
Each chart must answer exactly one analytical question. Label the chart title AS the question:
- ❌ "Stock Performance" (tells you nothing)
- ✅ "Which stocks moved > 5% today vs 7-day average?" (answers the question)

### Information hierarchy
```
Page title: [project name] Analytics Dashboard
├── Filters sidebar (date range, entity filter)
├── KPI metrics row (3-4 top-line numbers)
├── Primary chart (answers Q1)
├── Divider
├── Secondary chart (answers Q2)
└── Data freshness footer ("Data as of: YYYY-MM-DD HH:MM UTC")
```

### Always show data freshness
Users need to know if they're looking at yesterday's data or real-time.
```python
# Streamlit
latest_ts = conn.execute("SELECT MAX(_loaded_at) FROM fct_candles").fetchone()[0]
st.caption(f"📅 Data as of: {latest_ts.strftime('%Y-%m-%d %H:%M UTC')}")
```

---

## 3. Streamlit Patterns

### Caching (essential for performance)
```python
import streamlit as st
import duckdb

@st.cache_resource
def get_db_connection():
    """One connection shared across all sessions — reuse, don't reconnect per query."""
    return duckdb.connect("data/warehouse.duckdb", read_only=True)

@st.cache_data(ttl=3600)  # Cache query result for 1 hour
def load_daily_summary(start_date: str, end_date: str) -> pd.DataFrame:
    conn = get_db_connection()
    return conn.execute("""
        SELECT ...
        FROM fct_candles
        WHERE trade_date BETWEEN ? AND ?
    """, [start_date, end_date]).df()
```

### Filter sidebar pattern
```python
with st.sidebar:
    st.title("Filters")

    # Date range
    col1, col2 = st.columns(2)
    start = col1.date_input("From", value=date.today() - timedelta(days=30))
    end = col2.date_input("To", value=date.today())

    # Entity multi-select (load options from DB)
    all_tickers = get_db_connection().execute(
        "SELECT DISTINCT ticker FROM dim_companies ORDER BY ticker"
    ).df()["ticker"].tolist()
    selected = st.multiselect("Tickers", all_tickers, default=all_tickers[:10])

    # Apply button (prevent re-query on every keystroke)
    apply = st.button("Apply Filters", type="primary")
```

### KPI metrics row
```python
metrics = get_db_connection().execute("""
    SELECT
        COUNT(DISTINCT ticker)  AS total_stocks,
        AVG(pct_change_1d)      AS avg_daily_move,
        MAX(ABS(pct_change_1d)) AS max_mover
    FROM fct_candles
    WHERE trade_date = ?
""", [end]).fetchone()

col1, col2, col3 = st.columns(3)
col1.metric("Stocks tracked", f"{metrics[0]:,}")
col2.metric("Avg daily move", f"{metrics[1]:.2f}%")
col3.metric("Biggest mover", f"{metrics[2]:.2f}%")
```

### Chart patterns
```python
import plotly.express as px
import plotly.graph_objects as go

# Line chart (time series)
fig = px.line(df, x="trade_date", y="close", color="ticker",
              title="Closing Prices Over Time",
              labels={"close": "Close Price (USD)", "trade_date": "Date"})
fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)

# Horizontal bar (ranking)
top_n = df.nlargest(10, "pct_change_1d")
fig = px.bar(top_n, x="pct_change_1d", y="ticker", orientation="h",
             title="Top 10 Movers Today",
             color="pct_change_1d", color_continuous_scale="RdYlGn",
             labels={"pct_change_1d": "1-Day Change (%)", "ticker": ""})
st.plotly_chart(fig, use_container_width=True)

# Scatter (correlation)
fig = px.scatter(df, x="volume", y="pct_change_1d", color="sector",
                 hover_data=["ticker"],
                 title="Volume vs Price Change Correlation",
                 trendline="ols")  # adds regression line
st.plotly_chart(fig, use_container_width=True)
```

---

## 4. FastAPI Patterns (when serving as API)

```python
# serving/api.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import duckdb
from datetime import date
from typing import Optional
import pandas as pd

app = FastAPI(
    title="<Project> Analytics API",
    description="Serves Gold layer analytics for <analytical questions>",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_methods=["GET"],
)

conn = duckdb.connect("data/warehouse.duckdb", read_only=True)

@app.get("/api/v1/candles", summary="Daily OHLCV data per stock")
def get_candles(
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    limit: int = Query(1000, le=10000, description="Max records to return"),
):
    """
    Returns daily OHLCV candles.
    Answers: [analytical question this endpoint addresses]
    """
    sql = """
        SELECT c.ticker, t.date, f.open, f.high, f.low, f.close, f.volume
        FROM fct_candles f
        JOIN dim_companies c ON f.company_id = c.company_id
        JOIN dim_time t ON f.time_id = t.time_id
        WHERE t.date BETWEEN ? AND ?
    """
    params = [start_date, end_date]
    if ticker:
        sql += " AND c.ticker = ?"
        params.append(ticker.upper())
    sql += " ORDER BY t.date DESC LIMIT ?"
    params.append(limit)

    try:
        df = conn.execute(sql, params).df()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "rows_in_fct_candles": conn.execute("SELECT COUNT(*) FROM fct_candles").fetchone()[0]}
```

---

## 5. Deploy Checklist

### Streamlit (local / portfolio)
```bash
pip install streamlit plotly duckdb
streamlit run serving/app.py
# Open: http://localhost:8501
```

### Streamlit Cloud (free hosting for portfolio)
1. Push repo to GitHub
2. Go to share.streamlit.io → Deploy → Select repo + `serving/app.py`
3. Add secrets (API keys) in Streamlit Cloud settings

### Docker (reproducible)
```dockerfile
# serving/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY serving/ serving/
COPY data/ data/  # Or mount as volume
EXPOSE 8501
CMD ["streamlit", "run", "serving/app.py", "--server.address", "0.0.0.0"]
```
