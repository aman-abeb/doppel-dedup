# doppel

<!-- builder:badges:start -->
[![CI](https://github.com/aman-abeb/doppel-dedup/actions/workflows/ci.yml/badge.svg)](https://github.com/aman-abeb/doppel-dedup/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white) ![License: MIT](https://img.shields.io/badge/license-MIT-green)
<!-- builder:badges:end -->


doppel is a deterministic near-duplicate detection toolkit for text. It finds
near-duplicate documents using character-level k-shingles, MinHash signatures,
and (upcoming) LSH banding for scalable clustering. All hashing is seeded and
reproducible, so results are identical across runs and machines.

## Features

- Deterministic text normalization and k-shingle extraction (BLAKE2b-hashed tokens)
- Reproducible MinHash signatures generated from a fixed seed (pure Python, stdlib only)
- Exact Jaccard helpers for verifying signature estimates offline
- Fully offline test suite (pytest) — no network or API keys required

## Installation

```bash
pip install -e .
```

## Usage

```python
from doppel.minhash import jaccard, minhash_signature, signature_jaccard
from doppel.shingles import k_shingles

a = k_shingles("the quick brown fox", k=5)
b = k_shingles("the quick brown fox!", k=5)

print(jaccard(a, b))  # exact Jaccard similarity
print(signature_jaccard(minhash_signature(a), minhash_signature(b)))  # MinHash estimate
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## How it works

1. Text is normalized (Unicode NFKC, case folding, whitespace collapsing).
2. Character k-shingles are hashed with BLAKE2b into 64-bit tokens.
3. A MinHash signature of fixed length is computed with seeded universal hash
   functions `h(x) = (a * x + b) mod 2**64`.
4. The fraction of matching signature components estimates the Jaccard
   similarity of the underlying shingle sets.

## License

MIT

<!-- builder:roadmap:start -->
## Status

**In active development:** 1 of 2 milestones done.

## Roadmap

- [x] **MinHash + LSH core with a runnable scan command**: Implement k-shingle extraction, deterministic MinHash signatures with numpy, LSH banding for candidate pairs, exact-Jaccard verification, and union-find clustering. Ship a typer CLI `doppel scan <dir>` that prints candidate near-duplicate pairs. Add pytest coverage for hash determinism, signature-vs-exact Jaccard error bounds on known near-dups, LSH recall on a synthetic duplicate set, and a CLI smoke test on bundled sample docs. Runnable and green by end of session.
- [ ] **Clustered Rich report, tuning flags, and README demo**: Turn candidate pairs into scored clusters with a representative document, render a sorted Rich table plus optional `--json` export, and add `--threshold`, `--shingle-size`, `--num-perm`, and `--bands` flags with validation. Bundle a 50-file mixed sample corpus (paraphrases, copy-paste, unique docs) and write a README with real captured CLI output showing clusters like doc3.md ~ doc17.md (0.82). Finalize the full offline test suite and verify the showcase command end to end.
<!-- builder:roadmap:end -->
