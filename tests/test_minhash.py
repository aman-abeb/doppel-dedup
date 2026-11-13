"""Tests for deterministic shingling and MinHash signatures."""

import pytest

from doppel.minhash import NUM_PERM, jaccard, minhash_signature, signature_jaccard
from doppel.shingles import hash_token, k_shingles, normalize_text

_UINT64_MAX = 2**64 - 1


def test_hash_token_is_deterministic():
    assert hash_token("hello") == hash_token("hello")
    assert hash_token("hello") != hash_token("world")
    assert 0 <= hash_token("hello") < 2**64


def test_normalize_text_case_and_whitespace():
    assert normalize_text("  Hello   WORLD \n") == "hello world"
    assert normalize_text("") == ""


def test_k_shingles_is_deterministic_set():
    text = "the quick brown fox jumps over the lazy dog"
    first = k_shingles(text, k=5)
    second = k_shingles(text, k=5)
    assert isinstance(first, set)
    assert len(first) > 0
    assert first == second


def test_k_shingles_short_and_empty_text():
    assert k_shingles("", k=5) == set()
    assert k_shingles("abc", k=5) == {hash_token("abc")}


def test_k_shingles_rejects_non_positive_k():
    with pytest.raises(ValueError):
        k_shingles("text", k=0)


def test_minhash_signature_is_deterministic():
    shingles = k_shingles("the quick brown fox", k=5)
    sig1 = minhash_signature(shingles)
    sig2 = minhash_signature(shingles)
    assert len(sig1) == NUM_PERM
    assert all(isinstance(v, int) and 0 <= v <= _UINT64_MAX for v in sig1)
    assert sig1 == sig2


def test_minhash_signature_empty_set():
    sig = minhash_signature(set())
    assert len(sig) == NUM_PERM
    assert all(v == _UINT64_MAX for v in sig)


def test_jaccard_exact_values():
    assert jaccard({1, 2}, {1, 2}) == 1.0
    assert jaccard({1, 2}, {3, 4}) == 0.0
    assert jaccard({1, 2, 3}, {2, 3, 4}) == 0.5
    assert jaccard(set(), set()) == 1.0


def test_identical_texts_have_identical_signatures():
    shingles = k_shingles("identical text here", k=4)
    sig_a = minhash_signature(shingles)
    sig_b = minhash_signature(shingles)
    assert sig_a == sig_b
    assert signature_jaccard(sig_a, sig_b) == 1.0


def test_near_duplicates_signature_close_to_exact_jaccard():
    a = k_shingles("the quick brown fox jumps over the lazy dog", k=5)
    b = k_shingles("the quick brown fox jumps over the lazy dog!", k=5)
    exact = jaccard(a, b)
    estimate = signature_jaccard(minhash_signature(a), minhash_signature(b))
    assert exact > 0.9
    assert abs(estimate - exact) < 0.15


def test_disjoint_texts_have_near_zero_similarity():
    a = k_shingles("aaaa bbbb cccc dddd", k=3)
    b = k_shingles("zzzz yyyy xxxx wwww", k=3)
    assert jaccard(a, b) == 0.0
    estimate = signature_jaccard(minhash_signature(a), minhash_signature(b))
    assert estimate < 0.2


def test_signature_jaccard_rejects_mismatched_shapes():
    sig_a = minhash_signature(k_shingles("some text", k=3))
    sig_b = minhash_signature(k_shingles("other text", k=3), num_perm=64)
    with pytest.raises(ValueError):
        signature_jaccard(sig_a, sig_b)
