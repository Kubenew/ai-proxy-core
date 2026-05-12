from __future__ import annotations

import time
from fastapi import FastAPI, Request, HTTPException

from .balancer import AdaptiveBalancer
from .anomaly import ZScoreDetector
from .metrics import (
    REQ_COUNT,
    REQ_LATENCY,
    BACKEND_SCORE,
    ANOMALY_COUNT,
    metrics_response,
)


def create_app(
    balancer: AdaptiveBalancer,
    detector: ZScoreDetector | None,
    circuit_breaker_enabled: bool,
    error_threshold: int,
    cooldown_seconds: int,
    metrics_enabled: bool,
    metrics_path: str,
) -> FastAPI:
    app = FastAPI(title="ai-proxy-core")

    @app.api_route("/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"])
    async def handler(request: Request):
        backend = balancer.choose()
        if not backend:
            raise HTTPException(status_code=503, detail="No healthy backend")

        backend.active_requests += 1
        start = time.perf_counter()
        try:
            from .proxy import forward
            resp = await forward(request, backend.url)
        except Exception:
            backend.error_count += 1
            raise
        finally:
            backend.active_requests -= 1

        latency = (time.perf_counter() - start)
        backend.last_latency_ms = latency * 1000.0

        if detector and detector.add(backend.last_latency_ms):
            ANOMALY_COUNT.labels(backend=backend.url).inc()

        if circuit_breaker_enabled and backend.error_count >= error_threshold:
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
