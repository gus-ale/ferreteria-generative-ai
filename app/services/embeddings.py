import hashlib
import math
import re
from typing import Protocol

from openai import AsyncOpenAI

TOKEN_PATTERN = re.compile(r"[\wáéíóúüñ]+", re.IGNORECASE)


class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Create one vector for every input text."""


class HashEmbeddingProvider:
    """Deterministic offline vectors for tests and zero-cost demonstrations.

    This provider is lexical rather than truly semantic. Production RAG should
    use a real embedding model or a managed vector store.
    """

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = TOKEN_PATTERN.findall(text.lower())

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            vector = [value / norm for value in vector]
        return vector

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]


class OpenAIEmbeddingProvider:
    def __init__(
        self,
        client: AsyncOpenAI,
        model: str,
    ) -> None:
        self.client = client
        self.model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in ordered]
