import yaml
from typing import Dict


def load_config(path: str) -> Dict:
    """Load YAML config as a dict, with very light sanity checks."""
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Minimal validation
    cfg.setdefault("tickers", [])
    cfg.setdefault("defaults", {})
    cfg["defaults"].setdefault("period", "1d")
    cfg["defaults"].setdefault("interval", "1m")
    cfg.setdefault("options", {})
    cfg["options"].setdefault("periods", [])
    cfg["options"].setdefault("intervals", [])
    cfg.setdefault("ui", {})
    cfg["ui"].setdefault("columns_per_row", 3)
    cfg["ui"].setdefault("chart_height", 350)
    cfg.setdefault("cache_ttl_seconds", 600)
    return cfg
