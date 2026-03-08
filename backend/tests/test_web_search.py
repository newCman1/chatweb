import asyncio
from types import SimpleNamespace

from app.services import web_search


def test_search_web_context_uses_serpapi_provider(monkeypatch):
    async def fake_serpapi(_query: str, _limit: int):
        return ["serpapi hit"]

    monkeypatch.setattr(
        web_search,
        "settings",
        SimpleNamespace(
            web_search_provider="serpapi",
            web_search_serpapi_key="serp-key",
            web_search_tavily_key="",
            web_search_timeout_seconds=2.0,
            ai_http_trust_env=False,
            web_search_searxng_url="http://127.0.0.1:8080/search",
        ),
    )
    monkeypatch.setattr(web_search, "_search_serpapi", fake_serpapi)

    result = asyncio.run(web_search.search_web_context("python", limit=3))
    assert "serpapi hit" in result


def test_search_web_context_falls_back_to_duckduckgo_on_invalid_provider(monkeypatch):
    async def fake_duck(_query: str, _limit: int):
        return ["duck hit"]

    monkeypatch.setattr(
        web_search,
        "settings",
        SimpleNamespace(
            web_search_provider="unknown-provider",
            web_search_serpapi_key="",
            web_search_tavily_key="",
            web_search_timeout_seconds=2.0,
            ai_http_trust_env=False,
            web_search_searxng_url="http://127.0.0.1:8080/search",
        ),
    )
    monkeypatch.setattr(web_search, "_search_duckduckgo", fake_duck)

    result = asyncio.run(web_search.search_web_context("fallback", limit=3))
    assert "duck hit" in result


def test_search_web_context_returns_empty_when_serpapi_key_missing(monkeypatch):
    async def fake_serpapi(_query: str, _limit: int):
        return ["should-not-be-used"]

    monkeypatch.setattr(
        web_search,
        "settings",
        SimpleNamespace(
            web_search_provider="serpapi",
            web_search_serpapi_key="",
            web_search_tavily_key="",
            web_search_timeout_seconds=2.0,
            ai_http_trust_env=False,
            web_search_searxng_url="http://127.0.0.1:8080/search",
        ),
    )
    monkeypatch.setattr(web_search, "_search_serpapi", fake_serpapi)

    result = asyncio.run(web_search.search_web_context("no-key", limit=3))
    assert result == ""
