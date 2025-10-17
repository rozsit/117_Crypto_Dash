from typing import Dict, List
from dash import html, dcc
import dash_bootstrap_components as dbc


class LayoutBuilder:
    """Builds the Dash layout from config."""

    def __init__(self, config: Dict):
        self.config = config
        self.tickers: List[str] = config.get("tickers", [])
        self.periods: List[str] = config.get("options", {}).get("periods", [])
        self.intervals: List[str] = config.get(
            "options", {}).get("intervals", [])
        self.default_period: str = config.get(
            "defaults", {}).get("period", "1d")
        self.default_interval: str = config.get(
            "defaults", {}).get("interval", "1m")
        self.columns_per_row: int = int(
            config.get("ui", {}).get("columns_per_row", 3))
        self.chart_height: int = int(
            config.get("ui", {}).get("chart_height", 350))

    def _controls(self) -> dbc.Accordion:
        """Global controls inside a collapsible accordion (using dbc.Select for dark-friendly styling)."""
        return dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Period"),
                                        dbc.Select(
                                            id="dd-period",
                                            options=[{"label": p, "value": p}
                                                     for p in self.periods],
                                            value=self.default_period,
                                            size="lg",               # larger text/height
                                            className="text-light",  # ensure light text in dark theme
                                        ),
                                    ],
                                    md=3, sm=12
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Interval"),
                                        dbc.Select(
                                            id="dd-interval",
                                            options=[{"label": itv, "value": itv}
                                                     for itv in self.intervals],
                                            value=self.default_interval,
                                            size="lg",
                                            className="text-light",
                                        ),
                                    ],
                                    md=3, sm=12
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Actions"),
                                        dbc.Button(
                                            "Refresh", id="btn-refresh", color="primary", className="w-100"),
                                        html.Small(
                                            id="span-last-updated", className="text-muted d-block mt-2"),
                                    ],
                                    md=2, sm=12
                                ),
                            ],
                            className="g-3",
                        ),
                        html.Div(
                            [
                                html.Small(
                                    "Note: 1m data is available for the last 7 days only; "
                                    "sub-daily intervals (<1d) for the last 60 days. Invalid combos will show 'No data'."
                                )
                            ],
                            className="mt-2 text-secondary",
                        ),
                    ],
                    title="Controls (period & interval)",
                )
            ],
            start_collapsed=False,
            always_open=True,
            className="mb-3",
        )

    def _grid(self) -> dbc.Container:
        """3-column responsive grid of charts."""
        cols_per_row = self.columns_per_row
        rows = []

        # Chunk tickers into rows
        for i in range(0, len(self.tickers), cols_per_row):
            row_tickers = self.tickers[i: i + cols_per_row]
            cols = []
            for t in row_tickers:
                cols.append(
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5(t, className="mb-0")),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id={"type": "price-graph", "ticker": t},
                                        figure={},  # will be filled by callback
                                        config={"displayModeBar": True},
                                    )
                                ),
                            ],
                            className="h-100",
                        ),
                        md=12 // cols_per_row, sm=12, className="mb-4"
                    )
                )
            rows.append(dbc.Row(cols, className="g-3"))
        return dbc.Container(rows, fluid=True)

    def build_layout(self):
        """Compose the full page layout."""
        return dbc.Container(
            [
                # Hidden store for the tickers list
                dcc.Store(id="store-tickers", data=self.tickers),
                html.H2("Crypto Dashboard (Plotly Dash + yfinance)",
                        className="mt-3 mb-2"),
                html.Div("Dark theme • 3-column grid • Global controls • In-memory TTL cache",
                         className="text-secondary mb-2"),
                self._controls(),
                self._grid(),
                html.Hr(),
                html.Footer(
                    html.Small(
                        "Built with Dash + dbc • Windows 11 • Python 3.12", className="text-secondary"),
                    className="mb-4",
                ),
            ],
            fluid=True,
        )
