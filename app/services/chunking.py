import re


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, *, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    normalized = normalize_text(text)
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(normalized):
        tentative_end = min(start + chunk_size, len(normalized))
        end = tentative_end

        if tentative_end < len(normalized):
            search_start = start + chunk_size // 2
            candidates = [
                normalized.rfind(separator, search_start, tentative_end)
                for separator in (". ", "; ", ": ", " ")
            ]
            best_break = max(candidates)
            if best_break > start:
                end = best_break + 1

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)

    return chunks
