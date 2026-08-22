import sys
from pathlib import Path

from filter_by_score import MIN_LEN

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class ExitWithMessage(Exception):
    pass

INNER_ONLY = True

try:
    with open(DATA_DIR / "states.txt") as s_file:
        states = [line.strip().lower() for line in s_file if line.strip()]

    with open(DATA_DIR / "filtered_results.txt") as f:
        word_set = {line.strip().lower() for line in f if line.strip()}

    with open(DATA_DIR / "results.txt", "w") as out_file:
        for word in word_set:
            if len(word) >= MIN_LEN:
                # Determine which part of the word we are allowed to search
                if INNER_ONLY:
                    start = word[0]
                    middle_part = word[1:-1]
                    end = word[-1]
                else:
                    middle_part = word

                for state_to_remove in states:
                    if state_to_remove in middle_part:
                        for state_to_add in states:
                            if state_to_remove == state_to_add:
                                continue 
                            
                            # Logic: Letters must differ at both positions
                            if state_to_remove[0] == state_to_add[0] or state_to_remove[1] == state_to_add[1]:
                                continue
                                
                            # Create the new middle and reassemble the word
                            new_middle = middle_part.replace(state_to_remove, state_to_add, 1)
                            
                            if INNER_ONLY:
                                new_word = start + new_middle + end
                            else:
                                new_word = new_middle
                            
                            # Final validation
                            if new_word in word_set:
                                # Prevents printing the same pair twice (A->B and B->A)
                                if word < new_word:
                                    print(f"Original: {word} | Swapped: {state_to_remove}->{state_to_add} | Result: {new_word}", file=out_file)

except FileNotFoundError:
    print("Error: Required files missing.")
    sys.exit()
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit()