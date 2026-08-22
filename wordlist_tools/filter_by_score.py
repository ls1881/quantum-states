# This script reads a word list from data/XwiWordList.dict (an XWord Info
# export - not included in the repo, drop your own copy in data/) and
# prints out words that meet certain criteria:
# - The word's score must be at least MIN_SCORE
# - The word's length must be at least MIN_LEN

import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

MIN_SCORE = 50
MIN_LEN = 5

class ExitWithMessage(Exception):
    pass

try:
    with open(DATA_DIR / "XwiWordList.dict") as f_in, open(DATA_DIR / "filtered_results.txt", "w") as f_out:
        for line in f_in:
            parts = line.split(';') # Split the line into parts, using ";" as the delimiter
            word = parts[0].strip() # Get the first part of the line, the word before ";"
            score = int(parts[1])   # Score isn't used here but this is how you get it
            
            # Check score is >= MIN_SCORE and word length is >= MIN_LEN
            if score >= MIN_SCORE and len(word) >= MIN_LEN:
                print(word, file=f_out) # Write the word to the output file

except ExitWithMessage:
    sys.exit()