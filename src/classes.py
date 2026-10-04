from collections import defaultdict
from dataclasses import dataclass, field
from typing import TypedDict


class EdgeRecord(TypedDict):
    source: str
    target: str
    weight: float


@dataclass
class CardGraph:
    adj: defaultdict[str, defaultdict[str, float]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(float))
    )

    def add(self, a: str, b: str, w: float) -> None:
        if a == b:
            return
        self.adj[a][b] += w
        self.adj[b][a] += w

    def weight(self, a: str, b: str) -> float:
        return self.adj.get(a, {}).get(b, 0.0)

    def neighbors(self, a: str) -> dict[str, float]:
        return dict(self.adj.get(a, {}))

    def edges(self, threshold: float = 0.0) -> list[EdgeRecord]:
        return [
            {"source": a, "target": b, "weight": w}
            for a, nbrs in self.adj.items()
            for b, w in nbrs.items()
            if a < b and w >= threshold
        ]