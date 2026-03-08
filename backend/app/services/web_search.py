import logging
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import log_event


def _extract_related_topics(items: Any, out: list[str], limit: int) -> None:
    if not isinstance(items, list):
        return
    for item in items:
        if len(out) >= limit:
            return
        if not isinstance(item, dict):
            continue
        text = item.get("Text")
        first_url = item.get("FirstURL")
        if isinstance(text, str) and text.strip():
            snippet = text.strip()
            if isinstance(first_url, str) and first_url.strip():
                snippet = f"{snippet} ({first_url.strip()})"
            out.append(snippet[:280])
            continue
        nested = item.get("Topics")
        if isinstance(nested, list):
            _extract_related_topics(nested, out, limit)


async def search_web_context(query: str, limit: int = 5) -> str:
    logger = logging.getLogger("chatweb.backend.services.web_search")
    q = query.strip()
    if not q:
        return ""

    provider = (settings.web_search_provider or "duckduckgo").strip().lower()
    log_event(
        logger,
        logging.INFO,
        "web_search.start",
        {"query_length": len(q), "limit": limit, "provider": provider},
    )
    try:
        if provider == "duckduckgo":
            snippets = await _search_duckduckgo(q, limit)
        elif provider == "searxng":
            snippets = await _search_searxng(q, limit)
        elif provider == "serpapi":
            if not settings.web_search_serpapi_key.strip():
                log_event(logger, logging.WARNING, "web_search.serpapi_key_missing")
                return ""
            snippets = await _search_serpapi(q, limit)
        elif provider == "tavily":
            if not settings.web_search_tavily_key.strip():
                log_event(logger, logging.WARNING, "web_search.tavily_key_missing")
                return ""
            snippets = await _search_tavily(q, limit)
        else:
            log_event(
                logger,
                logging.WARNING,
                "web_search.provider_invalid",
                {"provider": provider, "fallback_provider": "duckduckgo"},
            )
            snippets = await _search_duckduckgo(q, limit)
    except httpx.HTTPError as error:
        log_event(
            logger,
            logging.WARNING,
            "web_search.http_error",
            {"provider": provider, "error": str(error), "error_type": type(error).__name__},
        )
        return ""
    if not snippets:
        log_event(logger, logging.INFO, "web_search.empty", {"provider": provider})
        return ""

    result = "\n".join(f"- {item}" for item in snippets[:limit])
    log_event(
        logger,
        logging.INFO,
        "web_search.done",
        {"provider": provider, "snippet_count": min(len(snippets), limit)},
    )
    return result


def _build_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=settings.web_search_timeout_seconds, trust_env=settings.ai_http_trust_env)


async def _search_duckduckgo(query: str, limit: int) -> list[str]:
    async with _build_http_client() as client:
        response = await client.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
        )
        response.raise_for_status()
        payload = response.json()

    snippets: list[str] = []
    abstract = payload.get("AbstractText")
    if isinstance(abstract, str) and abstract.strip():
        heading = payload.get("Heading")
        abstract_url = payload.get("AbstractURL")
        prefix = f"{heading.strip()}: " if isinstance(heading, str) and heading.strip() else ""
        summary = f"{prefix}{abstract.strip()}"
        if isinstance(abstract_url, str) and abstract_url.strip():
            summary = f"{summary} ({abstract_url.strip()})"
        snippets.append(summary[:280])
    _extract_related_topics(payload.get("RelatedTopics"), snippets, limit)
    return snippets[:limit]


async def _search_searxng(query: str, limit: int) -> list[str]:
    async with _build_http_client() as client:
        response = await client.get(
            settings.web_search_searxng_url,
            params={"q": query, "format": "json"},
        )
        response.raise_for_status()
        payload = response.json()
    items = payload.get("results")
    if not isinstance(items, list):
        return []
    snippets: list[str] = []
    for item in items:
        if len(snippets) >= limit:
            break
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        content = item.get("content")
        url = item.get("url")
        parts = []
        if isinstance(title, str) and title.strip():
            parts.append(title.strip())
        if isinstance(content, str) and content.strip():
            parts.append(content.strip())
        if not parts:
            continue
        snippet = " - ".join(parts)
        if isinstance(url, str) and url.strip():
            snippet = f"{snippet} ({url.strip()})"
        snippets.append(snippet[:280])
    return snippets


async def _search_serpapi(query: str, limit: int) -> list[str]:
    api_key = settings.web_search_serpapi_key.strip()
    if not api_key:
        return []
    async with _build_http_client() as client:
        response = await client.get(
            "https://serpapi.com/search.json",
            params={"q": query, "api_key": api_key, "engine": "google", "num": str(limit)},
        )
        response.raise_for_status()
        payload = response.json()
    items = payload.get("organic_results")
    if not isinstance(items, list):
        return []
    snippets: list[str] = []
    for item in items:
        if len(snippets) >= limit:
            break
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        snippet_text = item.get("snippet")
        link = item.get("link")
        parts = []
        if isinstance(title, str) and title.strip():
            parts.append(title.strip())
        if isinstance(snippet_text, str) and snippet_text.strip():
            parts.append(snippet_text.strip())
        if not parts:
            continue
        line = " - ".join(parts)
        if isinstance(link, str) and link.strip():
            line = f"{line} ({link.strip()})"
        snippets.append(line[:280])
    return snippets


async def _search_tavily(query: str, limit: int) -> list[str]:
    api_key = settings.web_search_tavily_key.strip()
    if not api_key:
        return []
    async with _build_http_client() as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": limit, "include_answer": False},
        )
        response.raise_for_status()
        payload = response.json()
    items = payload.get("results")
    if not isinstance(items, list):
        return []
    snippets: list[str] = []
    for item in items:
        if len(snippets) >= limit:
            break
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        content = item.get("content")
        url = item.get("url")
        parts = []
        if isinstance(title, str) and title.strip():
            parts.append(title.strip())
        if isinstance(content, str) and content.strip():
            parts.append(content.strip())
        if not parts:
            continue
        line = " - ".join(parts)
        if isinstance(url, str) and url.strip():
            line = f"{line} ({url.strip()})"
        snippets.append(line[:280])
    return snippets
