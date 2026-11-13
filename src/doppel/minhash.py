"""Deterministic MinHash signatures (pure Python, no third-party deps)."""

from __future__ import annotations

import random

# Number of hash functions (signature length) used for every signature.
NUM_PERM = 128

# Fixed seed so signatures are reproducible across runs and processes.
SEED = 20240517

# 64-bit unsigned wraparound mask and maximum value.
_MASK64 = (1 << 64) - 1
_UINT64_MAX = _MASK64


def _hash_params(num_perm: int = NUM_PERM, seed: int = SEED) -> tuple[list[int], list[int]]:
    """Generate the fixed ``(a, b)`` coefficients for ``num_perm`` hash functions.

    ``a`` values are drawn from [1, 2**64) so every hash function is a proper
    universal hash ``h(x) = (a * x + b) mod 2**64``.
    """
    rng = random.Random(seed)
    a = [rng.randrange(1, 1 << 64) for _ in range(num_perm)]
    b = [rng.randrange(0, 1 << 64) for _ in range(num_perm)]
    return a, b


def minhash_signature(shingles: set[int], num_perm: int = NUM_PERM, seed: int = SEED) -> list[int]:
    """Compute a deterministic MinHash signature for a set of hashed shingles.

    Returns a list of length ``num_perm`` where component ``i`` is the minimum
    of ``h_i(x)`` over all shingles ``x``. An empty shingle set yields
    all-``2**64 - 1`` components.
    """
    a, b = _hash_params(num_perm, seed)
    if not shingles:
        return [_MASK64] * num_perm
    tokens = list(shingles)
    return [min((ai * x + bi) & _MASK64 for x in tokens) for ai, bi in zip(a, b, strict=True)]


def jaccard(set_a: set[int], set_b: set[int]) -> float:
    """Exact Jaccard similarity between two sets (1.0 when both are empty)."""
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    return len(set_a & set_b) / len(union)


def signature_jaccard(sig_a: list[int], sig_b: list[int]) -> float:
    """Estimate Jaccard similarity as the fraction of matching signature parts."""
    if len(sig_a) != len(sig_b):
        raise ValueError("signatures must have the same length")
    if not sig_a:
        return 1.0
    matches = sum(1 for x, y in zip(sig_a, sig_b, strict=True) if x == y)
    return matches / len(sig_a)
