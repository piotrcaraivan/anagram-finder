# 🔠 Anagram Finder

A lightweight **Python 3 CLI utility** for searching and grouping anagrams from a text file.  
Built with clarity and determinism in mind — **simple, portable, no external dependencies.**

---

## ✨ Features
- Reads words **line by line** from a text file.
- Groups **anagrams on the same line** (space-separated).
- Deterministic output order:
  1. Multi-word groups first (in order of first appearance).
  2. Then singletons (also by first appearance).
- Words inside each group are sorted **alphabetically (case-insensitive)**.
- Clean CLI interface with helpful flags:
  - `--no-single` → hide singletons
  - `--min-length N` → filter by normalized word length
- Works out of the box — **no third-party libraries**.

---

## 📂 Project structure

anagram-finder/
├── src/
│ └── anagram_finder.py # main code + CLI
├── tests/
│ └── test_anagram_finder.py # unit tests
├── sample.txt # example input
├── README.md
└── DESIGN.md # design decisions



---

## 🚀 Usage

```bash
# Clone the repo
git clone https://github.com/piotrcaraivan/anagram-finder
cd anagram-finder

# Run on sample.txt
python src/anagram_finder.py

# Run on a custom file
python src/anagram_finder.py path/to/words.txt

# Hide singletons
python src/anagram_finder.py sample.txt --no-single

# Filter by length (after normalization)
python src/anagram_finder.py sample.txt --min-length 3

# Save results to a file
python src/anagram_finder.py sample.txt > output.txt
``` 

---

## Example:

### Input (sample.txt):
```bash
act
cat
tree
race
care
acre
bee
```

### Output:
```bash
act cat
acre care race
tree
bee
```

Normalization

Words are lowercased.

Diacritics are removed (Café → cafe) using unicodedata.normalize("NFKD", ...).

Only letters a–z are kept; digits, spaces, and symbols are ignored.


##🧪 Tests

Unit tests are written with Python’s built-in unittest.

# Run all tests
```
python -m unittest discover -s tests -p "test_*.py"
```
# Run a specific module
```
python -m unittest tests.test_anagram_finder
```
⚡ Performance & Scalability

Time complexity: O(N·L) (N words, L avg. length).

Handles millions of words on a single machine by streaming input.

See DESIGN.md
 for details on scaling to 10M and even 100B words (via spill files or MapReduce/Spark).

## 📦 Requirements

Python 3.8+

No external dependencies (standard library only).

## 📝 License

MIT — feel free to use, modify, and share.
