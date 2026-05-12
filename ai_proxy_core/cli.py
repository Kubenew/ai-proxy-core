from __future__ import annotations

import typer
import uvicorn

from .config import load_config
from .backend import Backend
from .balancer import AdaptiveBalancer
from .anomaly import ZScoreDetector
from .app import create_app

app = typer.Typer(help="ai-proxy-core - AI-assisted adaptive reverse proxy")


@app.command()
def run(config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file")):
    cfg = load_config(config)

    backends = [Backend(url=s.url) for s in cfg.backend_pool.servers]
    balancer = AdaptiveBalancer(backends)

    detector = None
    if cfg.anomaly_detection.enabled:
        detector = ZScoreDetector(threshold=cfg.anomaly_detection.latency_zscore_threshold)

    host, port = "0.0.0.0", 9200
    if ":" in cfg.listen:
        host, port_str = cfg.listen.split(":", 1)
        port = int(port_str)

    app_instance = create_app(
        balancer=balancer,
        detector=detector,
        circuit_breaker_enabled=cfg.circuit_breaker.enabled,
        error_threshold=cfg.circuit_breaker.error_threshold,
        cooldown_seconds=cfg.circuit_breaker.cooldown_seconds,
        metrics_enabled=cfg.metrics.enabled,
        metrics_path=cfg.metrics.path,
    )

    uvicorn.run(app_instance, host=host, port=port)


if __name__ == "__main__":
    app()
