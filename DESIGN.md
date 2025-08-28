# DESIGN.md — Anagram Finder

## Goal
Group words that are anagrams and print each group on a single line. Keep output deterministic and easy to test.

---

## I/O & Ordering
- **Input:** one word per line (text file).
- **Output:** groups printed as space-separated words, one group per line.
- **Order rules:**
  1. Multi-word groups first, then singletons.
  2. Both lists ordered by the group’s **first appearance** in the input.
  3. Inside a group, words are sorted **alphabetically (case-insensitive)**.

---

## Core Approach
1. **Normalization**
   - Lowercase.
   - Remove diacritics via `unicodedata.normalize("NFKD", ...)`.
   - Keep only letters `a–z`.
2. **Signature**
   - 26-length frequency vector for `a..z`.
   - Store as an immutable key (e.g., `tuple[int, ...]` or `bytes`).
3. **Grouping**
   - Dict: `signature -> list[str]`, plus `first_occurrence_index`.
4. **Emission**
   - Sort each group with `key=str.lower`.
   - Split into multi vs single.
   - Stable-sort by `first_occurrence_index`.
   - Print multi first, then single.

**Complexity:** `O(N·L)` time (N = words, L = avg length), memory ~ `O(#signatures + total words)`.

---

## Implementation Notes
- Stream input with a large buffer; maintain a running index for first-appearance.
- Defensive normalization: ignore anything outside `a–z` post-NFKD.
- Minimal CLI flags for clarity:
  - `--no-single` (hide singletons),
  - `--min-length N` (post-normalization).
- Deterministic output for easy diffs and tests.

---

## Testing
- Unit tests:
  - Normalization (digits/punct/diacritics).
  - Signature equality (anagrams) vs inequality.
  - Grouping + inner-group sort.
  - `--no-single`, `--min-length`.
- Golden test on a small fixture to validate full output.

---

## Scalability Considerations

### A) ~10 million words (single machine)
**Objective:** fast and memory-safe.
- **Stream once**; track `first_occurrence_index`.
- **Compact keys:** store the 26 counts as `bytes` (26B) or a tiny tuple to cut dict overhead.
- **On-demand spill for large groups:**
  - Keep a small in-RAM buffer per signature.
  - If a group grows too large, spill its words to a temp file; retain only handle + counters.
- **Finalize:** load words (RAM or spill), **sort case-insensitively**, output.
- Fits typical 8–16 GB RAM systems: only small metadata stays resident.

### B) ~100 **billion** words (distributed)
**Objective:** partition by signature and preserve first-appearance order globally.
- **Global order key per token:** `(shard_id, local_index)` or `(file_id, byte_offset)`.
- **Map:** normalize → signature → emit `(sig, (word, global_order_key))`.
- **Partition:** hash by `sig` so all anagrams meet at the same reducer.
- **Reduce (per signature):**
  - Compute earliest `global_order_key` (group rank).
  - **External sort** words if needed (chunk sort + k-way merge).
  - Output `(earliest_key, size, [sorted_words…])`.
- **Final assembly:**
  - Global **k-way merge** of multi-word records by earliest key,
  - Then the same for singletons,
  - Concatenate multi → single.
- **Skew:** detect hot signatures, apply **salting** (split across reducers) then local merge.
- **I/O discipline:** binary records + compression (e.g., LZ4/ZSTD) to reduce shuffle volume and GC pressure.

---

## Limitations & Future Work
- ASCII-centric by design; a Unicode mode would switch to a different signature (e.g., sorted codepoints or `Counter`) at some performance cost.
- Optional UX add-ons (stdin `-`, `.gz` input, JSON output, `--top N`) can be layered without changing the core.

---

## Summary
A simple, deterministic pipeline:
- NFKD → ASCII normalization,
- fast 26-count signature,
- streaming dict-based grouping with stable ordering.
Scales on one machine via spill files; scales to massive corpora via signature-partitioned MapReduce/Spark with external sorts and global merges.
