import sys
import csv
import pypuz
from pathlib import Path
import xml.etree.ElementTree as ET

def inject_clues(cfp_filename):
    downloads_dir = Path.home() / "Downloads"
    csv_path = downloads_dir / "compiled_all_clues.csv"
    
    cfp_path = Path(cfp_filename)
    if not cfp_path.exists():
         cfp_path = downloads_dir / cfp_filename
         if not cfp_path.exists():
             print(f"Error: Could not find {cfp_filename}")
             return

    # 1. Build the Clue Database from the CSV
    clue_db = {}
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ans = row.get("Answer", "").strip().upper()
                clue = row.get("Clue", "").strip()
                if ans and clue and ans not in clue_db:
                    clue_db[ans] = clue
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
        return
        
    print(f"-> Loaded {len(clue_db)} unique clues from your CSV database.")

    # 2. Read the Answers from the Grid using pypuz
    try:
        puzzle = pypuz.load(str(cfp_path))
    except Exception as e:
        print(f"Error loading {cfp_path.name} with pypuz: {e}")
        return
        
    answer_map = {}
    for c_list in puzzle.clues:
        # Standardize direction as ACROSS or DOWN
        dir_str = "ACROSS" if "across" in c_list['title'].lower() else "DOWN"
        for c in c_list['clues']:
            if c.number and c.answer:
                # Map tuple of (Direction, Number) to the actual grid Answer
                answer_map[(dir_str, str(c.number))] = c.answer.upper()
                
    print(f"-> Traced {len(answer_map)} grid answers from the puzzle.")

    # 3. Parse the XML and inject clues
    try:
        tree = ET.parse(cfp_path)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error: Unable to parse XML structure of {cfp_path.name}")
        return

    injected_count = 0
    skipped_count = 0
    
    # Iterate through the XML to find the WORD tags where clues live
    for elem in root.iter():
        tag_name = elem.tag.split('}')[-1].upper()
        if tag_name == 'WORD':
            
            # Get the tag's direction and number
            attrs = {k.lower(): v for k, v in elem.attrib.items()}
            w_dir = attrs.get('dir', '').upper()
            w_num = attrs.get('num', '')
            
            # If the tag already has text (e.g. your "[STEED?]" note), leave it alone
            current_clue = elem.text.strip() if elem.text else ""
            if current_clue:
                skipped_count += 1
                continue 
                
            # Look up the corresponding answer we pulled from pypuz
            ans = answer_map.get((w_dir, w_num), "")
            
            # If we have a matching clue in the database, inject it!
            if ans in clue_db:
                elem.text = clue_db[ans]
                injected_count += 1

    print(f"-> Left {skipped_count} existing clues/notes untouched.")

    # 4. Save the file back into .cfp format
    if injected_count > 0:
        tree.write(cfp_path, encoding='utf-8', xml_declaration=True)
        print(f"SUCCESS: Injected {injected_count} clues into {cfp_path.name}!")
    else:
        print("FINISHED: No new clues were injected (answers may not be in your CSV yet).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inject.py <filename.cfp>")
    else:
        inject_clues(sys.argv[1])