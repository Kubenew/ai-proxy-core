from __future__ import annotations

import logging

import typer
import uvicorn

from .config import load_config
from .backend import Backend
from .balancer import AdaptiveBalancer
from .anomaly import ZScoreDetector
from .app import create_app

app = typer.Typer(help="ai-proxy-core - AI-assisted adaptive reverse proxy")


@app.command()
def run(
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file"),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Logging level"),
):
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger("ai_proxy_core")

    cfg = load_config(config)
    logger.info("Loaded config from %s", config)

    backends = [Backend(url=s.url) for s in cfg.backend_pool.servers]
    balancer = AdaptiveBalancer(backends)
    logger.info("Registered %d backends", len(backends))

    detector = None
    if cfg.anomaly_detection.enabled:
        detector = ZScoreDetector(
            window_size=cfg.anomaly_detection.window_size,
            threshold=cfg.anomaly_detection.latency_zscore_threshold,
        )

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
        proxy_timeout=cfg.proxy.timeout_seconds,
    )

    logger.info("Starting server on %s:%d", host, port)
    uvicorn.run(app_instance, host=host, port=port, log_level=log_level.lower())


if __name__ == "__main__":
    app()
