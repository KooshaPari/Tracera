"""Generic trace-link writer interface with in-memory implementation."""

from typing import List
from tracertm.models.trace_link import TraceLink


class TraceLinkWriter:
    def write(self, link: TraceLink) -> None:
        raise NotImplementedError


class InMemoryTraceLinkWriter(TraceLinkWriter):
    def __init__(self):
        self._store: List[TraceLink] = []

    def write(self, link: TraceLink) -> None:
        self._store.append(link)

    def all(self) -> List[TraceLink]:
        return list(self._store)
