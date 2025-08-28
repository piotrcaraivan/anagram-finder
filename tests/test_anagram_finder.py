import unittest
from unittest.mock import patch
from src.anagram_finder import (
    normalize_word,
    compute_frequency_key,
    find_anagram_groups
)

def sort_like_code(words):
    # In the group code, key=str.lower is sorted — we do the same in expectations.
    
    return sorted(words, key=str.lower)

class TestAnagramFinder(unittest.TestCase):

    def test_normalize_word(self):
        self.assertEqual(normalize_word("Don't!"), "dont")
        self.assertEqual(normalize_word("Café"), "cafe")   # NFKD is required in normalize_word
        self.assertEqual(normalize_word("123"), "")
        self.assertEqual(normalize_word("Hello"), "hello")

    def test_compute_frequency_key(self):
        key1 = compute_frequency_key("race")
        key2 = compute_frequency_key("care")
        key3 = compute_frequency_key("test")
        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key3)

    @patch("src.anagram_finder.read_words")
    def test_find_anagram_groups(self, mock_read):
        mock_read.return_value = iter(["race", "Care", "hello", "elolh", "test", "apple"])
        groups = find_anagram_groups("dummy.txt")

        # Normalize actual groups
        actual = [sort_like_code(g) for g in groups]

        # Check that the required groups are present (regardless of their position)
        self.assertIn(sort_like_code(["race", "Care"]), actual)
        self.assertIn(sort_like_code(["hello", "elolh"]), actual)
        self.assertIn(sort_like_code(["test"]), actual)
        self.assertIn(sort_like_code(["apple"]), actual)

        # And there are only 4 of them
        self.assertEqual(len(groups), 4)

    @patch("src.anagram_finder.read_words")
    def test_exclude_singles(self, mock_read):
        mock_read.return_value = iter(["race", "care", "hello"])
        groups = find_anagram_groups("dummy.txt", exclude_singles=True)

        # Expect only the multi-word group; account for sorting within the group
        expected = [sort_like_code(["race", "care"])]
        actual = [sort_like_code(g) for g in groups]
        self.assertEqual(actual, expected)

    @patch("src.anagram_finder.read_words")
    def test_min_length(self, mock_read):
        mock_read.return_value = iter(["a", "b", "ab", "ba"])
        groups = find_anagram_groups("dummy.txt", min_length=2)

        expected = [sort_like_code(["ab", "ba"])]
        actual = [sort_like_code(g) for g in groups]
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
