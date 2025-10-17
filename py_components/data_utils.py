# py_components/data_utils.py
from __future__ import annotations
import pandas as pd


def _find_close_column(cols) -> str | None:
    """Return a suitable 'Close' column name in a case-insensitive way."""
    candidates = ["Close", "close", "Adj Close",
                  "AdjClose", "adjclose", "adj close"]
    for c in candidates:
        if c in cols:
            return c
    # Sometimes download() with multiindex flattening can yield 'Close_<TICKER>'
    for c in cols:
        if str(c).lower().startswith("close"):
            return c
        if str(c).lower().startswith("adj close") or str(c).lower().startswith("adjclose"):
            return c
    return None


def normalize_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize yfinance frame into two columns: ts (UTC naive) and Close.
    - Detect & convert time column to UTC-naive
    - Case-insensitive mapping to 'Close'
    - Drop NaNs/dupes, sort by time
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["ts", "Close"])

    # Detect time column or index
    if "Datetime" in df.columns:
        ts = pd.to_datetime(df["Datetime"], utc=True, errors="coerce")
    elif "Date" in df.columns:
        ts = pd.to_datetime(df["Date"], utc=True, errors="coerce")
    elif isinstance(df.index, pd.DatetimeIndex):
        ts = pd.to_datetime(df.index, utc=True, errors="coerce")
    else:
        # Fallback: try first column (best effort)
        first = df.columns[0]
        ts = pd.to_datetime(df[first], utc=True, errors="coerce")

    out = df.copy()

    # Find a suitable Close column
    close_col = _find_close_column(out.columns)
    if close_col is None:
        return pd.DataFrame(columns=["ts", "Close"])

    out = out.assign(ts=ts, Close=out[close_col])

    # Convert tz-aware -> UTC naive
    if pd.api.types.is_datetime64tz_dtype(out["ts"]):
        out["ts"] = out["ts"].dt.tz_convert("UTC").dt.tz_localize(None)
    else:
        out["ts"] = pd.to_datetime(out["ts"], errors="coerce")
        # Already naive; keep as is

    # Keep only valid rows, drop duplicates, sort
    out = out.loc[out["ts"].notna() & out["Close"].notna(), ["ts", "Close"]]
    out = out.drop_duplicates(subset=["ts"]).sort_values(
        "ts").reset_index(drop=True)
    return out
