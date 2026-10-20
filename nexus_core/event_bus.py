from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable


class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[[dict[str, Any]], None]) -> None:
        self._listeners[event_type].append(callback)

    def emit(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        for callback in self._listeners.get(event_type, []):
            callback(payload or {})

    def clear(self) -> None:
        self._listeners.clear()


bus = EventBus()
