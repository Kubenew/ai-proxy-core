from __future__ import annotations

from typing import List, Optional
from .backend import Backend


class AdaptiveBalancer:
    def __init__(self, backends: List[Backend]):
        self.backends = backends

    def choose(self) -> Optional[Backend]:
        candidates = [b for b in self.backends if b.healthy and not b.disabled()]
        if not candidates:
            return None
        return min(candidates, key=lambda b: b.score())
