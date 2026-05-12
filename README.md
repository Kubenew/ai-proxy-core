# ai-proxy-core

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

## Roadmap
- Plug-in ML models (sklearn/onnx)
- LLM-based WAF rules generation
- Token bucket rate limiting
- Geo routing
- Request classification + prioritization
- Web dashboard
