import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Dict


def configure_logging(config: Dict) -> logging.Logger:
    """Configure a shared application logger based on YAML config."""
    log_cfg = config.get("logging", {})
    level_name = str(log_cfg.get("level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger("crypto_dash")
    logger.setLevel(level)

    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    handlers = log_cfg.get("handlers", ["console"])
    if "console" in handlers:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    if "file" in handlers:
        path = log_cfg.get("file", "logs/app.log")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fh = RotatingFileHandler(
            path,
            maxBytes=int(log_cfg.get("max_bytes", 1_048_576)),
            backupCount=int(log_cfg.get("backup_count", 3)),
        )
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    # Quiet noisy deps
    logging.getLogger("yfinance").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger
