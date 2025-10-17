from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st

from py_components.config_loader import load_config
from py_components.utils_cache import TTLCache
from py_components.data_fetcher import DataFetcher
from py_components.chart_factory import create_price_figure


@st.cache_resource
def get_fetcher(ttl_seconds: int) -> DataFetcher:
    """Persist a single DataFetcher instance (with in-memory TTL cache) across reruns."""
    cache = TTLCache(ttl_seconds=ttl_seconds)
    return DataFetcher(cache=cache)


def main():
    # --- Page setup
    st.set_page_config(page_title="Crypto Dashboard", layout="wide")

    # --- Load config (path relative to this file)
    cfg_path = Path(__file__).parent / "config" / "config.yaml"
    config: Dict = load_config(str(cfg_path))

    tickers: List[str] = config.get("tickers", [])
    defaults: Dict = config.get("defaults", {})
    options: Dict = config.get("options", {})
    ui: Dict = config.get("ui", {})
    colors_map: Dict[str, str] = config.get("colors", {})

    periods = options.get("periods", [])
    intervals = options.get("intervals", [])
    default_period = defaults.get("period", "1d")
    default_interval = defaults.get("interval", "1m")

    chart_height = int(ui.get("chart_height", 420))
    time_offset_hours = int(ui.get("time_offset_hours", 0))
    time_label: Optional[str] = ui.get("time_label", None)

    st.title("Crypto Dashboard (Streamlit + yfinance)")
    st.caption(
        "Dark theme • One chart per row • Global controls • In-memory cache")

    # --- Controls (global)
    with st.expander("Controls (period & interval)", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            idx_p = periods.index(
                default_period) if default_period in periods else 0
            sel_period = st.selectbox("Period", periods, index=idx_p)
        with c2:
            idx_i = intervals.index(
                default_interval) if default_interval in intervals else 0
            sel_interval = st.selectbox("Interval", intervals, index=idx_i)
        with c3:
            refresh_clicked = st.button("Refresh", use_container_width=True)
        st.caption(
            "Note: 1m data is available for the last 7 days; "
            "sub-daily intervals (<1d) only for the last 60 days. Invalid combos will show 'No data'."
        )

    # --- Data service (cached across reruns)
    fetcher = get_fetcher(int(config.get("cache_ttl_seconds", 600)))

    # Handle refresh: clear service cache and rerun
    if refresh_clicked:
        fetcher.clear_cache()
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()

    # --- Render charts (1 per row by default in Streamlit)
    status_counts = {"ok": 0, "insufficient": 0, "no": 0}

    for t in tickers:
        df = fetcher.fetch(t, period=sel_period, interval=sel_interval)

        # classify status (keep the figure generation unified)
        if df is None or df.empty:
            status_counts["no"] += 1
        elif len(df) < 3:
            status_counts["insufficient"] += 1
        else:
            status_counts["ok"] += 1

        fig = create_price_figure(
            df,
            ticker=t,
            height=chart_height,
            time_offset_hours=time_offset_hours,
            time_label=time_label,
            line_color=colors_map.get(t),  # None -> Plotly default colorway
        )
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    st.divider()
    st.caption(
        f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • "
        f"OK: {status_counts['ok']} • Insufficient: {status_counts['insufficient']} • No data: {status_counts['no']}"
    )


if __name__ == "__main__":
    main()
