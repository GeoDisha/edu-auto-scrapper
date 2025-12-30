# opens the IRINS instances page, iterates through all pages of institutes,
# visits each institute's page to scrape faculty, publication, patent, and citation data,
# and saves the compiled data into an Excel file with checkpointing for resumption.
# Requires: undetected-chromedriver, pandas, openpyxl, beautifulsoup4, selenium
import time
import os
import pandas as pd
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
START_URL = "https://irins.org/instances"
OUTPUT_FILE = "irins_all_colleges_data_updated.xlsx"
CHECKPOINT_FILE = "checkpoint.txt"

# --------------------------------------------------
# LOAD CHECKPOINT (IF EXISTS)
# --------------------------------------------------
last_processed_url = None
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        last_processed_url = f.read().strip()

resume_skipping = bool(last_processed_url)

# --------------------------------------------------
# START UNDETECTED CHROME
# --------------------------------------------------
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 30)

# --------------------------------------------------
# LOAD EXISTING EXCEL (IF EXISTS)
# --------------------------------------------------
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_excel(OUTPUT_FILE)
    all_rows = df_existing.to_dict("records")
else:
    all_rows = []

# --------------------------------------------------
# OPEN INSTANCES PAGE
# --------------------------------------------------
driver.get(START_URL)
wait.until(EC.presence_of_element_located((By.ID, "orgTable")))
time.sleep(2)

# --------------------------------------------------
# PAGINATION LOOP
# --------------------------------------------------
while True:
    rows = driver.find_elements(By.CSS_SELECTOR, "#orgTable tbody tr")

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 6:
            continue

        institute = {
            "AISHE Code": cols[0].text.strip(),
            "Institute Name": cols[1].text.strip(),
            "Institute Type": cols[2].text.strip(),
            "District": cols[3].text.strip(),
            "State / UT": cols[4].text.strip(),
            "Institute URL": cols[5].find_element(By.TAG_NAME, "a").get_attribute("href")
        }

        # ---------------- RESUME LOGIC ----------------
        if resume_skipping:
            if institute["Institute URL"] != last_processed_url:
                continue
            resume_skipping = False
            continue

        print(f"Scraping: {institute['Institute Name']}")

        # --------------------------------------------------
        # OPEN INSTITUTE PAGE
        # --------------------------------------------------
        driver.get(institute["Institute URL"])
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # ---------------- TOTAL FACULTY ----------------
        total_f = soup.select_one("#total_f")
        institute["Total Faculty / Scientist"] = int(total_f.text.strip()) if total_f else 0

        # ---------------- TOTAL PUBLICATIONS ----------------
        total_p = soup.select_one("#total_p")
        institute["Total Publications"] = int(total_p.text.strip()) if total_p else 0

        # ---------------- PUBLICATION BREAKUP (ALL) ----------------
        for li in soup.select("ul.reseacher-box-ul li"):
            label = li.contents[0].strip()
            count = int(li.find("span", class_="counter-home").text.strip())
            institute[label] = count

        # ---------------- TOTAL PATENTS ----------------
        total_patent = soup.select_one("#total_patent")
        institute["Total Patents"] = int(total_patent.text.strip()) if total_patent else 0

        # ---------------- IMPACT / CITATIONS ----------------
        institute["Google Scholar Citations"] = 0
        institute["Scopus Citations"] = 0

        impact_block = soup.select_one("div.service-block-v3.service-block-sea")
        if impact_block:
            counters = impact_block.select("span.counter")
            if len(counters) >= 2:
                institute["Google Scholar Citations"] = int(counters[0].text.strip())
                institute["Scopus Citations"] = int(counters[1].text.strip())

        # --------------------------------------------------
        # SAVE TO EXCEL + CHECKPOINT
        # --------------------------------------------------
        all_rows.append(institute)
        pd.DataFrame(all_rows).fillna(0).to_excel(OUTPUT_FILE, index=False)

        with open(CHECKPOINT_FILE, "w") as f:
            f.write(institute["Institute URL"])

        print("✔ Saved")

        driver.back()
        time.sleep(2)

    # --------------------------------------------------
    # NEXT PAGE
    # --------------------------------------------------
    try:
        next_btn = driver.find_element(By.ID, "orgTable_next")
        if "disabled" in next_btn.get_attribute("class"):
            break
        next_btn.click()
        time.sleep(3)
    except:
        break

driver.quit()

print("\n✅ COMPLETED ALL PAGES SUCCESSFULLY")
print(f"📄 Output file: {OUTPUT_FILE}")
