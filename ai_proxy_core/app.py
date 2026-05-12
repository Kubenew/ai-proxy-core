from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse

from .balancer import AdaptiveBalancer
from .anomaly import ZScoreDetector
from .metrics import (
    REQ_COUNT,
    REQ_LATENCY,
    BACKEND_SCORE,
    ANOMALY_COUNT,
    metrics_response,
)
from .proxy import close_client

logger = logging.getLogger("ai_proxy_core.app")


def create_app(
    balancer: AdaptiveBalancer,
    detector: ZScoreDetector | None,
    circuit_breaker_enabled: bool,
    error_threshold: int,
    cooldown_seconds: int,
    metrics_enabled: bool,
    metrics_path: str,
    proxy_timeout: float = 30.0,
) -> FastAPI:
    app = FastAPI(title="ai-proxy-core")

    @app.on_event("startup")
    async def startup():
        logger.info("ai-proxy-core starting up")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Shutting down ai-proxy-core")
        await close_client()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
    async def handler(request: Request):
        backend = balancer.choose()
        if not backend:
            logger.warning("No healthy backends available")
            raise HTTPException(status_code=503, detail="No healthy backend")

        backend.active_requests += 1
        start = time.perf_counter()
        try:
            from .proxy import forward
            resp = await forward(request, backend.url, timeout=proxy_timeout)
        except Exception as e:
            backend.error_count += 1
            logger.error("Request to %s failed: %s", backend.url, e)
            return JSONResponse(status_code=502, content={"detail": "Bad gateway"})
        finally:
            backend.active_requests -= 1

        latency = time.perf_counter() - start
        backend.last_latency_ms = latency * 1000.0

        if detector and detector.add(backend.last_latency_ms):
            logger.info("Anomaly detected on %s: latency=%.2fms", backend.url, backend.last_latency_ms)
            ANOMALY_COUNT.labels(backend=backend.url).inc()

        if circuit_breaker_enabled and backend.error_count >= error_threshold:
            logger.warning("Circuit breaker tripped for %s (%d errors)", backend.url, backend.error_count)
            backend.disabled_until = time.time() + cooldown_seconds
            backend.error_count = 0

        REQ_COUNT.labels(backend=backend.url, status=str(resp.status_code)).inc()
        REQ_LATENCY.labels(backend=backend.url).observe(latency)
        BACKEND_SCORE.labels(backend=backend.url).set(backend.score())

        return resp

    if metrics_enabled:
        @app.get(metrics_path)
        async def metrics():
            return metrics_response()

    return app
