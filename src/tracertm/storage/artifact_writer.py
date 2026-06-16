"""Generic artifact writer interface with in-memory implementation."""

from typing import List
from tracertm.models.artifact import Artifact


class ArtifactWriter:
    def write(self, artifact: Artifact) -> None:
        raise NotImplementedError


class InMemoryArtifactWriter(ArtifactWriter):
    def __init__(self):
        self._store: List[Artifact] = []

    def write(self, artifact: Artifact) -> None:
        self._store.append(artifact)

    def all(self) -> List[Artifact]:
        return list(self._store)
