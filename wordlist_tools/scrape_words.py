import time
import random
import string
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
TARGET_URL = "https://www.xwordinfo.com/Finder"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "newWords.txt"

def human_type(element, text):
    """Simulates a human typing by adding random micro-delays between keystrokes."""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.25))

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Uncomment to run invisibly
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_words():
    driver = setup_driver()
    driver.get(TARGET_URL)
    
    wait = WebDriverWait(driver, 10)
    
    # 1. Ensure "Sort finds: by score" is selected 
    try:
        score_radio = wait.until(EC.element_to_be_clickable((By.ID, "rbScore")))
        if not score_radio.is_selected():
            score_radio.click()
    except Exception:
        print("Could not click 'Sort by score', assuming it is already checked.")

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        # Iterate lengths from 21 down to 3
        for length in range(21, 2, -1):
            
            # Iterate alphabet a through z
            for letter in string.ascii_lowercase:
                search_term = f"{letter}*"
                length_str = str(length)
                
                print(f"Scraping: Length {length}, Pattern '{search_term}'...")
                
                try:
                    # Select the 'only length' radio button
                    length_radio = driver.find_element(By.ID, "rbLen")
                    if not length_radio.is_selected():
                        length_radio.click()
                    
                    search_input = driver.find_element(By.ID, "WordBox")
                    length_input = driver.find_element(By.ID, "LenBox")
                    search_button = driver.find_element(By.ID, "SearchBut")
                    
                    # Simulate human typing
                    human_type(search_input, search_term)
                    time.sleep(random.uniform(0.2, 0.6))
                    human_type(length_input, length_str)
                    time.sleep(random.uniform(0.3, 0.8))
                    
                    # Click search
                    search_button.click()
                    
                    # Wait for the results table container to update
                    wait.until(EC.presence_of_element_located((By.ID, "Tables"))) 
                    time.sleep(random.uniform(1.0, 2.0)) 
                    
                    tables_div = driver.find_element(By.ID, "Tables")
                    
                    try:
                        # THE FIX: Use find_elements (plural) to get ALL '60' rows across ALL tables
                        rows_60 = tables_div.find_elements(By.XPATH, ".//tr[td[contains(@class, 'count') and contains(., '60')]]")
                        words_saved_this_page = 0
                        
                        # Loop through every single 60-point row found on the page
                        for row in rows_60:
                            word_links = row.find_elements(By.TAG_NAME, "a")
                            
                            for link in word_links:
                                # Use innerText to bypass CSS hiding
                                word_text = link.get_attribute("innerText").strip()
                                
                                if word_text:
                                    f.write(f"{word_text};60\n")
                                    f.flush() # Forces the save to the hard drive immediately
                                    words_saved_this_page += 1
                                    
                        if words_saved_this_page > 0:
                            print(f"   -> Saved {words_saved_this_page} words.")
                        else:
                            print("   -> No 60-point words found.")

                    except Exception:
                        print("   -> No 60-point words found.")
                                    
                except Exception as e:
                    print(f"Error on {search_term} (Length {length}). Refreshing page...")
                    driver.get(TARGET_URL) 
                    time.sleep(2)
                
                # Take a breather between alphabet letters to avoid rate limiting
                time.sleep(random.uniform(2.5, 4.0))
                
    print(f"\nScraping complete. All words saved to {OUTPUT_FILE}.")
    driver.quit()

if __name__ == "__main__":
    scrape_words()