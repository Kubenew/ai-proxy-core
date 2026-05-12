import tempfile
import yaml
from ai_proxy_core.config import load_config, AppConfig


def test_load_config_defaults():
    raw = {}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(raw, f)
        fname = f.name

    cfg = load_config(fname)
    assert isinstance(cfg, AppConfig)
    assert cfg.listen == "0.0.0.0:9200"
    assert cfg.backend_pool.balance == "adaptive"
    assert cfg.circuit_breaker.enabled is True
    assert cfg.circuit_breaker.error_threshold == 5
    assert cfg.anomaly_detection.enabled is True
    assert cfg.anomaly_detection.latency_zscore_threshold == 3.0
    assert cfg.anomaly_detection.window_size == 50
    assert cfg.proxy.timeout_seconds == 30.0
    assert cfg.metrics.enabled is True
    assert cfg.metrics.path == "/metrics"


def test_load_config_custom():
    raw = {
        "listen": "127.0.0.1:8080",
        "backend_pool": {
            "servers": [{"url": "http://localhost:5000"}],
        },
        "circuit_breaker": {"enabled": False, "error_threshold": 10},
        "anomaly_detection": {"enabled": False, "window_size": 100},
        "proxy": {"timeout_seconds": 60.0},
        "metrics": {"enabled": False, "path": "/custom-metrics"},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(raw, f)
        fname = f.name

    cfg = load_config(fname)
    assert cfg.listen == "127.0.0.1:8080"
    assert len(cfg.backend_pool.servers) == 1
    assert cfg.backend_pool.servers[0].url == "http://localhost:5000"
    assert cfg.circuit_breaker.enabled is False
    assert cfg.circuit_breaker.error_threshold == 10
    assert cfg.anomaly_detection.enabled is False
    assert cfg.anomaly_detection.window_size == 100
    assert cfg.proxy.timeout_seconds == 60.0
    assert cfg.metrics.enabled is False
    assert cfg.metrics.path == "/custom-metrics"
