# ai-proxy-core

[![PyPI version](https://img.shields.io/pypi/v/kubenew-ai-proxy)](https://pypi.org/project/kubenew-ai-proxy/)
[![Python versions](https://img.shields.io/pypi/pyversions/kubenew-ai-proxy)](https://pypi.org/project/kubenew-ai-proxy/)
[![License](https://img.shields.io/pypi/l/kubenew-ai-proxy)](https://github.com/Kubenew/aiproxy/blob/main/LICENSE)
[![CI](https://github.com/Kubenew/aiproxy/actions/workflows/ci.yml/badge.svg)](https://github.com/Kubenew/aiproxy/actions/workflows/ci.yml)

**ai-proxy-core** is a Python reverse proxy that adds **AI-driven decision logic**
for routing, anomaly detection, and adaptive traffic shaping.

This is a foundational library for building:
- AI-powered API gateways
- fraud/anomaly-aware reverse proxies
- inference traffic routers
- intelligent load balancers

## MVP Features
- Reverse proxy with backend pools
- Adaptive backend scoring based on:
  - latency
  - active connections
  - error rate
- Basic anomaly detection (moving average / z-score)
- Circuit breaker auto-disable for failing backends
- Prometheus metrics
- Connection pooling (reused httpx.AsyncClient)
- Graceful shutdown with cleanup hooks
- Configurable request timeout per proxy instance

## Quickstart

```bash
pip install -e .
ai-proxy run -c examples/config.yml
```

Test:
```bash
curl http://localhost:9200/
curl http://localhost:9200/metrics
```

## Changelog

### 0.1.1 (2025-XX-XX)
- Migrated build system to hatchling
- Added connection pooling via module-level httpx.AsyncClient
- Added graceful shutdown (startup/shutdown events in FastAPI app)
- Added logging across proxy, app, and CLI modules
- Added ProxyConfig with configurable timeout_seconds
- Wired window_size from config to ZScoreDetector
- Added --log-level CLI option
- Fixed bare except in app.py (returns JSONResponse 502)
- Expanded test suite (backend, balancer, config, proxy tests)
- Added ruff linting configuration
- Added CI workflow (GitHub Actions)
- Added LICENSE and .gitignore

### 0.1.0 (Initial release)
- Reverse proxy with backend pools
- Adaptive backend scoring
- Z-score anomaly detection
- Circuit breaker
- Prometheus metrics

## Roadmap
- Plug-in ML models (sklearn/onnx)
- LLM-based WAF rules generation
- Token bucket rate limiting
- Geo routing
- Request classification + prioritization
- Web dashboard
