from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque
import math


@dataclass
class ZScoreDetector:
    window_size: int = 50
    threshold: float = 3.0

    def __post_init__(self):
        self.samples: Deque[float] = deque(maxlen=self.window_size)

    def add(self, value: float) -> bool:
        self.samples.append(value)
        if len(self.samples) < 10:
            return False

        mean = sum(self.samples) / len(self.samples)
        var = sum((x - mean) ** 2 for x in self.samples) / len(self.samples)
        std = math.sqrt(var) if var > 0 else 0.0

        if std == 0:
            return False

        z = abs(value - mean) / std
        return z > self.threshold
