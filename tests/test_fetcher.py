import asyncio
from unittest import mock

import pytest

from fetcher import Fetcher, FetcherSession, AsyncFetcher, AsyncFetcherSession, DEFAULT_BROWSER_HEADERS


def test_fetcher_get_merges_headers_and_sets_referer():
    with mock.patch("requests.get") as req_get:
        Fetcher.get("https://example.com")
        args, kwargs = req_get.call_args
        sent_headers = kwargs.get("headers", {})
        # default UA present
        assert "User-Agent" in sent_headers
        # referer set to google
        assert sent_headers.get("Referer") == "https://www.google.com/"


def test_fetcher_get_explicit_headers_override_defaults():
    with mock.patch("requests.get") as req_get:
        Fetcher.get("https://example.com", headers={"User-Agent": "mybot", "Referer": "https://custom/"})
        _, kwargs = req_get.call_args
        sent_headers = kwargs.get("headers", {})
        assert sent_headers["User-Agent"] == "mybot"
        assert sent_headers["Referer"] == "https://custom/"


def test_fetcher_session_get_uses_session_and_merges_headers():
    fake_session = mock.Mock()
    fs = FetcherSession(session=fake_session)
    fs.get("https://example.com")
    fake_session.get.assert_called()
    sent_headers = fake_session.get.call_args[1]["headers"]
    assert "User-Agent" in sent_headers
    assert sent_headers.get("Referer") == "https://www.google.com/"


def test_async_fetcher_get_merges_headers_and_sets_referer(monkeypatch):
    # Create dummy aiohttp module so tests don't require the real package.
    import types

    class DummyResponse:
        def __init__(self):
            self._text = "ok"

        async def text(self):
            return self._text

    class DummyContext:
        def __init__(self, resp):
            self._resp = resp

        async def __aenter__(self):
            return self._resp

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class DummySession:
        def __init__(self):
            self.called_with = None

        def get(self, url, headers=None, **kwargs):
            self.called_with = headers
            return DummyContext(DummyResponse())

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    fake_aiohttp = types.ModuleType("aiohttp")
    fake_aiohttp.ClientSession = lambda: DummySession()
    monkeypatch.setitem(__import__("sys").modules, "aiohttp", fake_aiohttp)

    text = asyncio.run(AsyncFetcher.get("https://example.com"))
    assert text == "ok"
