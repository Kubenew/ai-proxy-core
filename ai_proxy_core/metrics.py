from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


REQ_COUNT = Counter(
    "ai_proxy_requests_total",
    "Total requests",
    ["backend", "status"],
)

REQ_LATENCY = Histogram(
    "ai_proxy_request_latency_seconds",
    "Request latency seconds",
    ["backend"],
)

BACKEND_SCORE = Gauge(
    "ai_proxy_backend_score",
    "Backend adaptive score",
    ["backend"],
)

ANOMALY_COUNT = Counter(
    "ai_proxy_anomalies_total",
    "Anomaly detections",
    ["backend"],
)


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
