"""
Simple Fetcher utilities: `Fetcher`, `AsyncFetcher`, and session wrappers.

Behavior:
- Each request auto-injects realistic browser headers and a Google `Referer`.
- If the caller supplies `headers=` those values override the defaults.

This module keeps dependencies optional: it uses `requests` for sync and
`aiohttp` for async and raises helpful errors when missing.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

DEFAULT_BROWSER_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

DEFAULT_GOOGLE_REFERER = "https://www.google.com/"


def _merge_headers(defaults: Dict[str, str], explicit: Optional[Dict[str, str]], google_referer: bool) -> Dict[str, str]:
    """Merge default headers with explicit headers.

    Explicit headers (if provided) override defaults.
    If `google_referer` is True, ensure `Referer` points to Google unless
    explicitly provided.
    """
    merged = dict(defaults)
    if explicit:
        # explicit overrides defaults
        merged.update({k: v for k, v in explicit.items() if v is not None})

    if google_referer and "Referer" not in merged:
        merged["Referer"] = DEFAULT_GOOGLE_REFERER

    return merged


class FetcherSession:
    """Synchronous session-based fetcher using `requests`.

    The class is light-weight: if `requests` is not installed a helpful
    ImportError is raised when an HTTP method is invoked.
    """

    def __init__(self, session: Any = None, default_headers: Optional[Dict[str, str]] = None, google_referer: bool = True):
        self._provided_session = session
        self.default_headers = default_headers or DEFAULT_BROWSER_HEADERS
        self.google_referer = google_referer
        self._session = session

    def _ensure_session(self):
        if self._session is None:
            try:
                import requests

                self._session = requests.Session()
            except Exception as exc:  # pragma: no cover - informative message
                raise ImportError("requests is required for FetcherSession: pip install requests") from exc

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        """Perform a GET request, merging headers as described.

        Example:
            s = FetcherSession()
            r = s.get("https://example.com")
        """
        self._ensure_session()
        final_headers = _merge_headers(self.default_headers, headers, self.google_referer)
        return self._session.get(url, headers=final_headers, **kwargs)

    def post(self, url: str, data: Any = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        self._ensure_session()
        final_headers = _merge_headers(self.default_headers, headers, self.google_referer)
        return self._session.post(url, data=data, headers=final_headers, **kwargs)


class Fetcher:
    """Stateless synchronous helper using `requests` for one-off calls."""

    @staticmethod
    def get(url: str, headers: Optional[Dict[str, str]] = None, google_referer: bool = True, **kwargs) -> Any:
        try:
            import requests
        except Exception as exc:  # pragma: no cover - informative message
            raise ImportError("requests is required for Fetcher.get: pip install requests") from exc

        final_headers = _merge_headers(DEFAULT_BROWSER_HEADERS, headers, google_referer)
        return requests.get(url, headers=final_headers, **kwargs)

    @staticmethod
    def post(url: str, data: Any = None, headers: Optional[Dict[str, str]] = None, google_referer: bool = True, **kwargs) -> Any:
        try:
            import requests
        except Exception as exc:  # pragma: no cover - informative message
            raise ImportError("requests is required for Fetcher.post: pip install requests") from exc

        final_headers = _merge_headers(DEFAULT_BROWSER_HEADERS, headers, google_referer)
        return requests.post(url, data=data, headers=final_headers, **kwargs)


class AsyncFetcherSession:
    """Async session wrapper using `aiohttp`.

    Only created when used so `aiohttp` remains optional at import time.
    """

    def __init__(self, session: Any = None, default_headers: Optional[Dict[str, str]] = None, google_referer: bool = True):
        self._provided_session = session
        self.default_headers = default_headers or DEFAULT_BROWSER_HEADERS
        self.google_referer = google_referer
        self._session = session

    async def _ensure_session(self):
        if self._session is None:
            try:
                import aiohttp

                self._session = aiohttp.ClientSession()
            except Exception as exc:  # pragma: no cover - informative message
                raise ImportError("aiohttp is required for AsyncFetcherSession: pip install aiohttp") from exc

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        await self._ensure_session()
        final_headers = _merge_headers(self.default_headers, headers, self.google_referer)
        async with self._session.get(url, headers=final_headers, **kwargs) as resp:
            return await resp.text()

    async def post(self, url: str, data: Any = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        await self._ensure_session()
        final_headers = _merge_headers(self.default_headers, headers, self.google_referer)
        async with self._session.post(url, data=data, headers=final_headers, **kwargs) as resp:
            return await resp.text()


class AsyncFetcher:
    """Stateless async helpers using `aiohttp` for one-off calls."""

    @staticmethod
    async def get(url: str, headers: Optional[Dict[str, str]] = None, google_referer: bool = True, **kwargs) -> Any:
        try:
            import aiohttp
        except Exception as exc:  # pragma: no cover - informative message
            raise ImportError("aiohttp is required for AsyncFetcher.get: pip install aiohttp") from exc

        final_headers = _merge_headers(DEFAULT_BROWSER_HEADERS, headers, google_referer)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=final_headers, **kwargs) as resp:
                return await resp.text()


__all__ = [
    "Fetcher",
    "FetcherSession",
    "AsyncFetcher",
    "AsyncFetcherSession",
    "DEFAULT_BROWSER_HEADERS",
]
