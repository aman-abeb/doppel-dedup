"""Text normalization and deterministic k-shingle extraction."""

from __future__ import annotations

import hashlib
import re
import unicodedata

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize text for shingling.

    Applies Unicode NFKC normalization, case folding, and collapses all
    whitespace runs to single spaces.
    """
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.casefold()
    normalized = _WHITESPACE_RE.sub(" ", normalized).strip()
    return normalized


def hash_token(token: str) -> int:
    """Deterministically hash a token to a 64-bit unsigned integer.

    Uses BLAKE2b, which is stable across processes and platforms, so shingle
    hashes are reproducible across runs.
    """
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def k_shingles(text: str, k: int = 5) -> set[int]:
    """Return the set of hashed character k-shingles for ``text``.

    Character-level shingles are used so that near-duplicates with small edits
    still share most of their shingles. Non-empty text shorter than ``k``
    yields a single shingle of the whole normalized text.
    """
    if k <= 0:
        raise ValueError("k must be a positive integer")
    normalized = normalize_text(text)
    if not normalized:
        return set()
    if len(normalized) < k:
        return {hash_token(normalized)}
    return {hash_token(normalized[i : i + k]) for i in range(len(normalized) - k + 1)}
