# Custom-Theme-Scripts

Wordlist processing and crossword clue-management scripts used to build and maintain a personal
crossword word list, and to move clues in and out of puzzle files.

## Overview

The repository is split into two independent toolchains:

- **`wordlist_tools/`** — a pipeline for scraping, filtering, and mining a scored crossword word
  list for theme material.
- **`clue_tools/`** — utilities for extracting clues from existing puzzle files and reusing them
  in new ones.

Both read and write shared data files under `data/`.

## Repository structure

```
custom-theme-scripts/
├── README.md
├── requirements.txt
├── wordlist_tools/
│   ├── scrape_words.py       # scrape high-scoring entries from xwordinfo.com
│   ├── merge_new_words.py    # diff scraped words against your master dictionary
│   ├── filter_by_score.py    # filter the master dictionary by score/length
│   └── state_swap_finder.py  # find letter-swap word pairs (e.g. state codes)
├── clue_tools/
│   ├── extract_clues.py      # compile clues from .puz/.cfp files into a CSV
│   └── inject_clues.py       # fill empty clue slots in a .cfp file from that CSV
└── data/
    ├── states.txt
    ├── newWords.txt
    ├── additionalWords.txt
    └── results.txt
```

## Requirements

- Python 3.9+
- Google Chrome and a matching Chromedriver (for `scrape_words.py` only)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## wordlist_tools/

A pipeline for building up a scored word list (in the XWord Info `WORD;SCORE` format) and mining
it for theme material.

1. **`scrape_words.py`** — Selenium scraper that pulls high-scoring (60-point) entries off
   [xwordinfo.com/Finder](https://www.xwordinfo.com/Finder) for every letter and length, and
   appends them to `data/newWords.txt`. Requires a local Chromedriver.
2. **`merge_new_words.py`** — Diffs `data/newWords.txt` against your master list
   (`data/XwiWordList.dict`, not included in this repo) and writes only the genuinely new entries
   to `data/additionalWords.txt`, so you can review before merging them into your master list.
3. **`filter_by_score.py`** — Filters `data/XwiWordList.dict` down to words meeting a minimum
   score and length (`MIN_SCORE` / `MIN_LEN` constants at the top of the file), writing the result
   to `data/filtered_results.txt`.
4. **`state_swap_finder.py`** — Takes the output of `filter_by_score.py` and finds every pair of
   words in it that turn into each other by swapping one two-letter U.S. state postal code for
   another (e.g. `braked` → `brined` via `AK` → `IN`), writing matches to `data/results.txt`.
   Set `INNER_ONLY = False` at the top of the file to allow swaps that touch the first or last
   letter of the word, not just the interior. This logic isn't state-specific — point
   `data/states.txt` at any list of same-length letter groups to search for a different kind of
   swap theme.

Typical run order: `scrape_words.py` → `merge_new_words.py` (review and merge into your dictionary
by hand) → `filter_by_score.py` → `state_swap_finder.py`.

## clue_tools/

Tools for reusing clues across your own puzzle files.

- **`extract_clues.py`** — Walks your home directory for `.puz` and `.cfp` files and compiles
  every (answer, clue, puzzle) triple into `~/Downloads/compiled_all_clues.csv`, skipping
  entries and puzzles it has already recorded on a prior run.
- **`inject_clues.py`** — Given a `.cfp` file, looks up each grid answer in
  `~/Downloads/compiled_all_clues.csv` and fills in any empty clue slots with a previously-used
  clue for that answer. Existing clue text and notes are left untouched.

  ```bash
  python clue_tools/inject_clues.py <filename.cfp>
  ```

## data/

Word lists and generated output shared by the scripts above:

- `states.txt` — the two-letter codes used by `state_swap_finder.py`
- `newWords.txt`, `additionalWords.txt`, `results.txt` — outputs from the pipeline above,
  checked in as examples
- `XwiWordList.dict`, `filtered_results.txt` — user-supplied/generated, gitignored and not
  included in this repo
