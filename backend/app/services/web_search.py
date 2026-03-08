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

    log_event(logger, logging.INFO, "web_search.start", {"query_length": len(q), "limit": limit})
    try:
        async with httpx.AsyncClient(timeout=8.0, trust_env=settings.ai_http_trust_env) as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": q,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1",
                },
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as error:
        log_event(
            logger,
            logging.WARNING,
            "web_search.http_error",
            {"error": str(error), "error_type": type(error).__name__},
        )
        return ""

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
    if not snippets:
        log_event(logger, logging.INFO, "web_search.empty")
        return ""

    result = "\n".join(f"- {item}" for item in snippets[:limit])
    log_event(logger, logging.INFO, "web_search.done", {"snippet_count": min(len(snippets), limit)})
    return result
