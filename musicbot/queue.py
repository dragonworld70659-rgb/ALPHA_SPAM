from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class Track:
    title: str
    url: str
    stream_url: str
    duration: int | None = None
    requested_by: str | None = None


class QueueManager:
    def __init__(self) -> None:
        self._queues: dict[int, deque[Track]] = defaultdict(deque)

    def add(self, chat_id: int, track: Track) -> int:
        self._queues[chat_id].append(track)
        return len(self._queues[chat_id])

    def pop_next(self, chat_id: int) -> Track | None:
        if not self._queues[chat_id]:
            return None
        return self._queues[chat_id].popleft()

    def peek(self, chat_id: int) -> Track | None:
        if not self._queues[chat_id]:
            return None
        return self._queues[chat_id][0]

    def clear(self, chat_id: int) -> None:
        self._queues[chat_id].clear()

    def list(self, chat_id: int) -> list[Track]:
        return list(self._queues[chat_id])


queues = QueueManager()
