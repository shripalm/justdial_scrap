from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pandas import DataFrame as pd
from storage import save_to_csv
from config import CAT_OUTPUT_FILE

def get_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)

def get_nct(driver, query, city):
    base = "https://www.justdial.com/"
    url = f"{base}{city}/{query}"
    print(f"🔍 Navigating to: {url}")
    driver.get(url)

    try:
        # Wait until at least one result card is visible
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".resultbox"))
        )
    except:
        print("⚠️ Timeout: No business results found.")
    
    # scroll down to trigger lazy loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    
    # get the redirected/final URL
    final_url = driver.current_url
    chuncks = final_url.lstrip(base).split('?')[0].split('/')
    nct = chuncks[2] if len(chuncks) > 2 else None
    chunckDF = pd.from_dict({
        'city': [chuncks[0]], 
        'query': [query],
        'cat': [chuncks[1]],
        'nct': [chuncks[2]]
    })
    save_to_csv(chunckDF, CAT_OUTPUT_FILE)
    return nct