from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def filter_new_words(dict_file, new_words_file, output_file):
    existing_words = set()
    
    # 1. Load existing dictionary words into a set for fast lookup
    try:
        with open(dict_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Split at the semicolon and grab the word
                # Converting to uppercase ensures case-insensitive matching
                word = line.split(';')[0].strip().upper()
                existing_words.add(word)
                
        print(f"Loaded {len(existing_words):,} existing words from {dict_file}.")
    except FileNotFoundError:
        print(f"Error: '{dict_file}' not found. Please ensure it is in the same folder.")
        return

    # 2. Read the scraped words and filter out the ones you already have
    unique_new_entries = []
    try:
        with open(new_words_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                word = line.split(';')[0].strip().upper()
                
                # If the word isn't in the main dictionary, save it
                if word not in existing_words:
                    unique_new_entries.append(line)
                    # Add it to the set to prevent duplicates from the newWords file itself
                    existing_words.add(word) 
                    
        print(f"Found {len(unique_new_entries):,} completely new words to add.")
        
    except FileNotFoundError:
        print(f"Error: '{new_words_file}' not found.")
        return

    # 3. Save the truly new words to the output file
    if unique_new_entries:
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in unique_new_entries:
                f.write(entry + '\n')
        print(f"Success! Saved to {output_file}.")
    else:
        print("No new words to save. Your main dictionary already contains all of them!")

if __name__ == "__main__":
    filter_new_words(
        DATA_DIR / "XwiWordList.dict",
        DATA_DIR / "newWords.txt",
        DATA_DIR / "additionalWords.txt",
    )