import csv
import os
from pathlib import Path
import pypuz
import puz

def extract_all_clues_and_answers():
    home_dir = Path.home()
    downloads_dir = home_dir / "Downloads"
    output_path = downloads_dir / "compiled_all_clues.csv"
    
    seen_entries = set()
    seen_puzzles = set()
    
    if output_path.exists():
        print(f"Found existing spreadsheet at {output_path}. Loading data...")
        with open(output_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    ans, clu, puz_name = row[0], row[1], row[2]
                    seen_entries.add((ans, clu, puz_name))
                    seen_puzzles.add(puz_name)
                    
    print("Scanning your home directory for .cfp and .puz files...")
    
    puzzle_files = []
    for root, dirs, files in os.walk(home_dir):
        for file in files:
            if file.lower().endswith((".cfp", ".puz")):
                puzzle_files.append(Path(root) / file)
    
    if not puzzle_files:
        print("No .cfp or .puz files found.")
        return

    print(f"Found {len(puzzle_files)} total puzzles. Extracting...")
    
    new_extracted_data = []
    new_puzzles_count = 0
    new_clues_count = 0

    for file_path in puzzle_files:
        is_new_puzzle = file_path.name not in seen_puzzles
        if is_new_puzzle:
            new_puzzles_count += 1
            seen_puzzles.add(file_path.name)
            
        try:
            # Handle .puz files using puzpy directly
            if file_path.suffix.lower() == ".puz":
                p = puz.read(str(file_path))
                numbering = p.clue_numbering()
                
                # Extract Across clues
                for clue_dict in numbering.across:
                    clue_text = clue_dict['clue']
                    cell = clue_dict['cell']
                    length = clue_dict['len']
                    # Across answers are contiguous letters in the solution string
                    answer = p.solution[cell : cell + length]
                    
                    entry = (answer, clue_text, file_path.name)
                    if entry not in seen_entries:
                        seen_entries.add(entry)
                        new_extracted_data.append(list(entry))
                        new_clues_count += 1
                        
                # Extract Down clues
                for clue_dict in numbering.down:
                    clue_text = clue_dict['clue']
                    cell = clue_dict['cell']
                    length = clue_dict['len']
                    # Down answers jump by the width of the puzzle row by row
                    answer = "".join([p.solution[cell + (i * p.width)] for i in range(length)])
                    
                    entry = (answer, clue_text, file_path.name)
                    if entry not in seen_entries:
                        seen_entries.add(entry)
                        new_extracted_data.append(list(entry))
                        new_clues_count += 1

            # Handle .cfp files
            elif file_path.suffix.lower() == ".cfp":
                puzzle = pypuz.load(str(file_path))
                for clue_list in puzzle.clues:
                    for clue in clue_list['clues']:
                        if clue.clue and clue.clue.strip():
                            answer = clue.answer or ""
                            clue_text = clue.clue.strip()
                            
                            entry = (answer, clue_text, file_path.name)
                            if entry not in seen_entries:
                                seen_entries.add(entry)
                                new_extracted_data.append(list(entry))
                                new_clues_count += 1
                            
        except Exception as e:
            print(f"Skipping {file_path.name}: {e}")
            continue

    if new_extracted_data:
        file_mode = 'a' if output_path.exists() else 'w'
        with open(output_path, mode=file_mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if file_mode == 'w':
                writer.writerow(["Answer", "Clue", "Puzzle"])
            writer.writerows(new_extracted_data)
            
        print(f"\nSuccess! Added {new_clues_count} NEW clues from {new_puzzles_count} NEW puzzles.")
        print(f"Spreadsheet updated at: {output_path}")
    else:
        print(f"\nFinished! Found {len(puzzle_files)} puzzles, but no new clues were found.")
        print("Your spreadsheet is already up to date.")

if __name__ == "__main__":
    extract_all_clues_and_answers()