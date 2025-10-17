from datetime import datetime
from typing import Dict, List
from dash import Input, Output, State, ALL
import pandas as pd

from .data_fetcher import DataFetcher
from .chart_factory import create_price_figure


def register_callbacks(app, config: Dict, fetcher: DataFetcher):
    tickers: List[str] = config.get("tickers", [])
    chart_height: int = int(config.get("ui", {}).get("chart_height", 350))

    # NEW: read time offset & label from config
    time_offset_hours: int = int(config.get(
        "ui", {}).get("time_offset_hours", 0))
    time_label: str | None = config.get("ui", {}).get("time_label", None)

    @app.callback(
        Output({"type": "price-graph", "ticker": ALL}, "figure"),
        Output("span-last-updated", "children"),
        Input("dd-period", "value"),
        Input("dd-interval", "value"),
        Input("btn-refresh", "n_clicks"),
        State("store-tickers", "data"),
        prevent_initial_call=False,
    )
    # pyright: ignore[reportUnusedFunction]
    def update_all_figures(period: str, interval: str, n_clicks, tickers_state: List[str]):
        if n_clicks is not None:
            fetcher.clear_cache()

        figures = []
        for t in tickers_state:
            df: pd.DataFrame = fetcher.fetch(
                t, period=period, interval=interval)
            fig = create_price_figure(
                df, ticker=t, height=chart_height,
                time_offset_hours=time_offset_hours,   # <-- pass offset
                time_label=time_label,                 # <-- optional label
            )
            figures.append(fig)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return figures, f"Last update: {now_str}"
