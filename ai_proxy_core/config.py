from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List
import yaml


class BackendConfig(BaseModel):
    url: str


class BackendPoolConfig(BaseModel):
    balance: str = "adaptive"
    servers: List[BackendConfig] = Field(default_factory=list)


class CircuitBreakerConfig(BaseModel):
    enabled: bool = True
    error_threshold: int = 5
    cooldown_seconds: int = 15


class AnomalyDetectionConfig(BaseModel):
    enabled: bool = True
    latency_zscore_threshold: float = 3.0


class MetricsConfig(BaseModel):
    enabled: bool = True
    path: str = "/metrics"


class AppConfig(BaseModel):
    listen: str = "0.0.0.0:9200"
    backend_pool: BackendPoolConfig = Field(default_factory=BackendPoolConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    anomaly_detection: AnomalyDetectionConfig = Field(default_factory=AnomalyDetectionConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return AppConfig.model_validate(raw)
