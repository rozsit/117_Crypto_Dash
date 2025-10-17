# py_components/chart_factory.py
from typing import Optional
import pandas as pd
import plotly.graph_objects as go


def create_price_figure(
    df: pd.DataFrame,
    ticker: str,
    height: int = 350,
    time_offset_hours: int = 0,
    time_label: Optional[str] = None,
    line_color: Optional[str] = None,
) -> go.Figure:
    """Create a line chart for normalized df with ['ts','Close'] or a placeholder."""
    fig = go.Figure()

    def _no_data(msg: str = "No data"):
        fig.add_annotation(
            text=msg,
            x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=18),
        )
        fig.update_layout(
            title=ticker,
            template="plotly_dark",
            height=height,
            margin=dict(l=40, r=20, t=40, b=40),
        )
        x_title = "Time" + (f" ({time_label})" if time_label else "")
        fig.update_xaxes(title_text=x_title, automargin=True, ticks="outside")
        fig.update_yaxes(title_text="Close", automargin=True, ticks="outside")
        return fig

    if df is None or df.empty or not {"ts", "Close"}.issubset(df.columns):
        return _no_data("No data")

    if len(df) < 3:
        return _no_data("Insufficient data")

    # Shift X by configured offset (e.g., +2 hours)
    x = df["ts"] + pd.Timedelta(hours=int(time_offset_hours))
    y = df["Close"]

    line_style = {"width": 2}
    if line_color:  # only set if provided
        line_style["color"] = line_color

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name=ticker,
            line=line_style,
            hovertemplate="%{x|%Y-%m-%d %H:%M}"
                          + (f" ({time_label})" if time_label else "")
                          + "<br>Close=%{y:.6g}<extra></extra>",
        )
    )

    x_title = "Time" + (f" ({time_label})" if time_label else "")
    fig.update_layout(
        title=ticker,
        template="plotly_dark",
        height=height,
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis_title=x_title,
        yaxis_title="Close",
        hovermode="x unified",
    )

    # Compact, adaptive date formats
    fig.update_xaxes(
        automargin=True,
        ticks="outside",
        ticklabelposition="outside",
        ticklabelmode="instant",
        tickfont=dict(size=12),
        tickformatstops=[
            dict(dtickrange=[None, 1000 * 60 * 60 * 12], value="%H:%M"),
            dict(dtickrange=[1000 * 60 * 60 * 12, 1000 *
                 60 * 60 * 24 * 7], value="%b %d\n%H:%M"),
            dict(dtickrange=[1000 * 60 * 60 * 24 * 7,
                 1000 * 60 * 60 * 24 * 30], value="%b %d"),
            dict(dtickrange=[1000 * 60 * 60 * 24 * 30, None], value="%Y-%m"),
        ],
    )
    fig.update_yaxes(
        automargin=True,
        ticks="outside",
        tickfont=dict(size=12),
        tickformat=".6~g",
    )
    return fig
