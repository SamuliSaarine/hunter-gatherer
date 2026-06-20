import random
from game.state import Character, RelationshipDelta


class RelationshipGraph:
    def __init__(self) -> None:
        self._edges: dict[str, dict[str, int]] = {}

    def get_trust(self, from_id: str, to_id: str) -> int:
        return self._edges.get(from_id, {}).get(to_id, 0)

    def set_trust(self, from_id: str, to_id: str, value: int) -> None:
        if from_id not in self._edges:
            self._edges[from_id] = {}
        self._edges[from_id][to_id] = max(-100, min(100, value))

    def update_trust(self, from_id: str, to_id: str, delta: int) -> None:
        current = self.get_trust(from_id, to_id)
        self.set_trust(from_id, to_id, current + delta)

    def get_advocates(self, character_id: str, min_trust: int = 30) -> list[str]:
        advocates = []
        for from_id, targets in self._edges.items():
            if targets.get(character_id, 0) >= min_trust:
                advocates.append(from_id)
        return advocates

    def all_trusts_for(self, character_id: str) -> dict[str, int]:
        return self._edges.get(character_id, {})


_graph = RelationshipGraph()


def get_graph() -> RelationshipGraph:
    return _graph


def initialize_relationships(characters: list[Character]) -> None:
    global _graph
    _graph = RelationshipGraph()
    ids = [c.id for c in characters]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            base = random.randint(-10, 20)
            _graph.set_trust(a, b, base)
            _graph.set_trust(b, a, base + random.randint(-5, 5))


def apply_relationship_delta(delta: RelationshipDelta) -> None:
    _graph.update_trust(delta.from_id, delta.to_id, delta.trust_delta)
