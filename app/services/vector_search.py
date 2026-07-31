import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ScoredVector:
    item_id: int
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must have the same dimensions")

    dot_product = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot_product / (left_norm * right_norm)


def rank_vectors(
    query_vector: list[float],
    candidates: list[tuple[int, list[float]]],
    *,
    top_k: int,
) -> list[ScoredVector]:
    scores = [
        ScoredVector(item_id=item_id, score=cosine_similarity(query_vector, vector))
        for item_id, vector in candidates
    ]
    scores.sort(key=lambda item: item.score, reverse=True)
    return scores[:top_k]
