from dash import Dash
import dash_bootstrap_components as dbc
import logging

from py_components.config_loader import load_config
from py_components.utils_cache import TTLCache
from py_components.data_fetcher import DataFetcher
from py_components.layout_builder import LayoutBuilder
from py_components.callbacks import register_callbacks
from py_components.logging_setup import configure_logging  # <-- NEW


def create_app() -> Dash:
    # Load configuration
    config = load_config("config/config.yaml")

    # Configure logging once
    logger = configure_logging(config)
    logger.info("Starting Crypto Dashboard")

    # Select Bootstrap theme
    theme_name = getattr(dbc.themes, config["ui"].get(
        "bootstrap_theme", "DARKLY"), dbc.themes.DARKLY)

    app = Dash(
        __name__,
        external_stylesheets=[theme_name],
        suppress_callback_exceptions=True,
        title="Crypto Dashboard",
    )

    cache = TTLCache(ttl_seconds=int(config.get("cache_ttl_seconds", 600)))
    fetcher = DataFetcher(cache=cache)

    builder = LayoutBuilder(config=config)
    app.layout = builder.build_layout()

    register_callbacks(app=app, config=config, fetcher=fetcher)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
