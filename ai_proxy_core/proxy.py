from __future__ import annotations

import logging

import httpx
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("ai_proxy_core.proxy")

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def _filter_headers(headers: dict) -> dict:
    return {k: v for k, v in headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}


_client: httpx.AsyncClient | None = None


def get_client(timeout: float = 30.0) -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(follow_redirects=False, timeout=timeout)
    return _client


async def close_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def forward(request: Request, backend_url: str, timeout: float = 30.0) -> Response:
    target = backend_url.rstrip("/") + request.url.path
    if request.url.query:
        target += "?" + request.url.query

    body = await request.body()
    client = get_client(timeout)

    logger.debug("Forwarding %s %s -> %s", request.method, request.url.path, backend_url)
    resp = await client.request(
        method=request.method,
        url=target,
        headers=_filter_headers(dict(request.headers)),
        content=body,
    )
    logger.debug("Response from %s: %s", backend_url, resp.status_code)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=_filter_headers(dict(resp.headers)),
        media_type=resp.headers.get("content-type"),
    )
