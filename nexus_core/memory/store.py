from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MemoryItem:
    id: str
    category: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryStore:
    def __init__(self) -> None:
        self._items: dict[str, MemoryItem] = {}

    def store_memory(self, category: str, content: str, metadata: dict[str, Any] | None = None) -> MemoryItem:
        item_id = str(len(self._items) + 1)
        item = MemoryItem(id=item_id, category=category, content=content, metadata=metadata or {})
        self._items[item_id] = item
        return item

    def retrieve_memory(self, memory_id: str) -> MemoryItem | None:
        return self._items.get(memory_id)

    def search_memory(self, query: str, category: str | None = None) -> list[MemoryItem]:
        q = query.lower()
        result: list[MemoryItem] = []
        for item in self._items.values():
            if category and item.category != category:
                continue
            haystack = f"{item.category} {item.content} {' '.join(str(v) for v in item.metadata.values())}".lower()
            if q in haystack:
                result.append(item)
        return result

    def update_memory(self, memory_id: str, *, category: str | None = None, content: str | None = None, metadata: dict[str, Any] | None = None) -> MemoryItem | None:
        item = self._items.get(memory_id)
        if item is None:
            return None
        if category is not None:
            item.category = category
        if content is not None:
            item.content = content
        if metadata is not None:
            item.metadata.update(metadata)
        return item

    def forget_memory(self, memory_id: str) -> bool:
        existed = memory_id in self._items
        self._items.pop(memory_id, None)
        return existed

    def list_memories(self) -> list[MemoryItem]:
        return list(self._items.values())


memory_store = MemoryStore()
