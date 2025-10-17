import logging
import pandas as pd
import yfinance as yf

from .utils_cache import TTLCache
from .data_utils import normalize_timeseries

logger = logging.getLogger("crypto_dash")


class DataFetcher:
    """Fetches price data via yfinance with a tiny TTL cache and robust fallbacks."""

    def __init__(self, cache: TTLCache):
        self.cache = cache

    def _cache_key(self, ticker: str, period: str, interval: str) -> str:
        return f"{ticker}|{period}|{interval}"

    def _normalize_single(self, raw: pd.DataFrame) -> pd.DataFrame:
        if raw is None or raw.empty:
            return pd.DataFrame(columns=["ts", "Close"])
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = ["_".join([str(c) for c in col if c])
                           for col in raw.columns]
        raw = raw.reset_index()
        return normalize_timeseries(raw)

    def fetch(self, ticker: str, period: str, interval: str) -> pd.DataFrame:
        key = self._cache_key(ticker, period, interval)
        cached = self.cache.get(key)
        if cached is not None:
            logger.info(f"[fetch] cache hit: {key} (rows={len(cached)})")
            return cached

        logger.info(f"[fetch] downloading: {key}")
        df_norm = pd.DataFrame(columns=["ts", "Close"])

        # Attempt 1: yf.download
        try:
            df = yf.download(
                tickers=ticker,
                period=period,
                interval=interval,
                auto_adjust=True,
                group_by="column",
                progress=False,
                threads=False,
            )
            df_norm = self._normalize_single(df)
        except Exception as e:
            logger.exception(
                f"[fetch] download() failed for {ticker} ({period},{interval})")

        # Attempt 2: Ticker.history fallback
        if df_norm.empty:
            try:
                hist = yf.Ticker(ticker).history(
                    period=period,
                    interval=interval,
                    auto_adjust=True,
                    actions=False,
                )
                df_norm = self._normalize_single(hist)
                if not df_norm.empty:
                    logger.info(
                        f"[fetch] fallback history() ok: {key} (rows={len(df_norm)})")
            except Exception:
                logger.exception(
                    f"[fetch] history() failed for {ticker} ({period},{interval})")

        if df_norm.empty:
            logger.warning(f"[fetch] no data: {key}")
        else:
            logger.info(f"[fetch] got {len(df_norm)} rows: {key}")

        self.cache.set(key, df_norm)
        return df_norm

    def clear_cache(self) -> None:
        self.cache.clear()
