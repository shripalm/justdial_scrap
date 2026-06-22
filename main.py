from scraper import get_driver, get_nct
from config import *
import pandas as pd
from curler import run_agent

def get_nct_top(keyword):
    cats = pd.read_csv(CAT_OUTPUT_FILE)
    if not cats[cats['query'] == keyword].empty:
        print(f"✅ Category for {keyword} already exists. Skipping...")
        nct = cats[cats['query'] == keyword]['nct'].values[0]
    else:    
        driver = get_driver(HEADLESS)
        nct = get_nct(driver, keyword, CITY)
        driver.quit()
    
    return nct

if __name__ == "__main__":
    queries = ["Import Export Services"]
    for query in queries:
        nct = get_nct_top(query).lstrip('nct-')
        print(f"NCT for {query}: {nct}")
        for area in AREAS:
            run_agent(CITY, query, area, nct)
