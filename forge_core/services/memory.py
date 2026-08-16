from forge_core.contracts.models import MemoryItem


class InMemoryScopedMemory:
    """Development-only scoped memory implementation."""

    def __init__(self) -> None:
        self._items: list[MemoryItem] = []

    def save(self, item: MemoryItem) -> None:
        self._items.append(item)

    def search(self, scope: str, query: str) -> list[MemoryItem]:
        terms = query.lower().split()
        return [item for item in self._items if item.scope == scope and all(term in item.content.lower() or term in item.key.lower() for term in terms)]
