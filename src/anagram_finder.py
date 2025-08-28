"""
A utility for searching and grouping anagrams from a text file.
"""
from collections import defaultdict
import argparse, sys, unicodedata
from typing import Iterator, List, Tuple, Dict, Optional
from pathlib import Path



def normalize_word(word: str) -> str:
    """
    Converts the word to lowercase, removes diacritics (Café -> cafe),
    leaves only letters a-z.
    """
    w = unicodedata.normalize("NFKD", word.lower())
    return "".join(ch for ch in w if "a" <= ch <= "z")



def compute_frequency_key(word: str) -> Tuple[int, ...]:
    """
    Creates a 26-element tuple — the frequency of each letter (a-z).
    Used as a key for grouping anagrams.
    """
    freq = [0] * 26
    base = ord('a')
    for ch in word:
        freq[ord(ch) - base] += 1
    return tuple(freq)


def read_words(path: str) -> Iterator[str]:
    """
    Lazily reads lines from a file, returning non-empty lines.
    """
    try:
        with open(path, 'r', encoding='utf-8', buffering=1 << 20) as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    yield stripped
    except FileNotFoundError:
        print(f"Error: File not found — {path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def find_anagram_groups(
    path: str,
    exclude_singles: bool = False,
    min_length: int = 1
) -> List[List[str]]:
    """
    Main logic: loads words, groups anagrams.

    Args:
        path: path to the file
        exclude_singles: do not include single words
        min_length: minimum length of the word after normalization

    Returns:
        List of groups (each group is a list of words)
    """
    groups = defaultdict(list)
    first_occurrence = {}

    for idx, raw_word in enumerate(read_words(path)):
        cleaned = normalize_word(raw_word)
        if not cleaned or len(cleaned) < min_length:
            continue
        key = compute_frequency_key(cleaned)
        groups[key].append(raw_word)
        if key not in first_occurrence:
            first_occurrence[key] = idx

    # Sort words in groups
    for word_list in groups.values():
        word_list.sort(key=str.lower)

    # Separate into groups and singles
    multi = [(first_occurrence[k], words) for k, words in groups.items() if len(words) >= 2]
    single = [(first_occurrence[k], words) for k, words in groups.items() if len(words) == 1]

    if exclude_singles:
        single = []

    # Sort by order of appearance
    multi.sort()
    single.sort()

    return [words for _, words in multi] + [words for _, words in single]


def print_groups(groups: List[List[str]]) -> None:
    """
    Prints groups: one phrase per line.
    """
    for words in groups:
        print(" ".join(words))


def main():
    parser = argparse.ArgumentParser(description="Groups anagrams from a file.")
    parser.add_argument("path", nargs="?", default=None, help="Path to the word file")
    parser.add_argument("--no-single", action="store_true", help="Do not display single words")
    parser.add_argument("--min-length", type=int, default=1, help="Minimum length of the word (after normalization)")

    args = parser.parse_args()

    # if the path is not specified → search for sample.txt in the project root directory
    if args.path is None:
        root_dir = Path(__file__).resolve().parent.parent
        args.path = str(root_dir / "sample.txt")

    groups = find_anagram_groups(args.path, exclude_singles=args.no_single, min_length=args.min_length)
    print_groups(groups)


if __name__ == "__main__":
    main()