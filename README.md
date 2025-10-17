# Crypto Dashboard (Dash & Streamlit + yfinance)

A lightweight, OOP-structured crypto price dashboard.
Fetches prices from **Yahoo Finance** via `yfinance`, renders interactive line charts with Plotly,
and ships with two frontends:
- **Dash** (development browser app)
- **Streamlit** (for local use and Streamlit Community Cloud deploy)

---

## Features
- Dark theme UI, one chart per row (scrollable page)
- Global **Period** / **Interval** selectors + **Refresh** button
- In-memory TTL cache to avoid rate limits
- Robust data fetching (fallback from `download()` to `Ticker.history()`)
- Optional per-ticker line colors
- Config-driven (YAML): tickers, UI, TTL, axis time offset (e.g., `UTC+02:00`)

---

## Project Structure

```
crypto_dash/
├─ main.py                  # Dash entry point (dev app)
├─ streamlit_app.py         # Streamlit entry point (Cloud deploy)
├─ requirements.txt
├─ config/
│  └─ config.yaml           # Tickers + UI + options
└─ py_components/
   ├─ __init__.py
   ├─ callbacks.py          # Dash callbacks
   ├─ chart_factory.py      # Plotly figure creation
   ├─ config_loader.py      # YAML loader
   ├─ data_fetcher.py       # yfinance with TTL cache + fallbacks
   ├─ data_utils.py         # timeseries normalization
   └─ utils_cache.py        # tiny in-memory TTL cache
```

> The same data/service layer is reused by both Dash and Streamlit.

---

## Configuration (`config/config.yaml`)

Key sections you can tune:

```yaml
tickers:
  - "DUEL28868-USD"
  - "XEM-USD"
  # ...

defaults:
  period: "5d"          # default time range
  interval: "1h"        # default interval

cache_ttl_seconds: 600  # 10 minutes

ui:
  bootstrap_theme: "DARKLY"
  columns_per_row: 1
  chart_height: 420
  time_offset_hours: 2     # shift X-axis by +2 hours
  time_label: "UTC+02:00"  # shown in axis title / hover

options:
  periods: ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"]
  intervals: ["1m","2m","5m","15m","30m","60m","90m","1h","1d","5d","1wk","1mo","3mo"]

# Optional per-ticker colors (hex)
colors:
  REN-USD: "#775DD0"
  BAKE-USD: "#00E396"
```

> Note: For Yahoo Finance, `1m` is available only for the last 7 days; sub-daily intervals (<1d) only for the last 60 days.

---

## Local Setup

```bash
# (optional) create venv
python -m venv .venv
# Windows:
# .\.venv\Scripts ctivate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### Run the Dash app (development)
```bash
python main.py
# App at http://127.0.0.1:8050
```

### Run the Streamlit app (local & Cloud-ready)
```bash
streamlit run streamlit_app.py
# App at http://localhost:8501
```

---

## Troubleshooting

- **"No data" or "Insufficient data"** – Many niche tickers may not exist on Yahoo or don’t provide data for certain period/interval combinations. Test with known symbols like `BTC-USD`, `ETH-USD`, `SOL-USD`.
- **Config not found** – The app reads YAML via `Path(__file__).parent / "config" / "config.yaml"`. Ensure the file exists in the repo.
- **Streamlit refresh** – Use `st.rerun()` (not `experimental_rerun` on newer Streamlit versions).
- **Performance/rate limits** – Increase `cache_ttl_seconds` (e.g., 900).

---
