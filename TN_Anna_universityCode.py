#Open and scrape data from the Anna University TN government engineering colleges page using undetected-chromedriver and Selenium.

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time

# ----------------------------------
# UNDETECTED + HEADLESS OPTIONS
# ----------------------------------
options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, use_subprocess=True)

url = "https://dte.tn.gov.in/government-engineering"

driver.get(url)
time.sleep(5)  # allow DataTable JS to initialize

# ----------------------------------
# GET HEADERS
# ----------------------------------
headers = [
    th.text.strip()
    for th in driver.find_elements(By.CSS_SELECTOR, "#dtable thead th")
]

print("Headers Found:", headers)

all_rows = []

# ----------------------------------
# GET TOTAL PAGES (DataTables API)
# ----------------------------------
total_pages = driver.execute_script("""
    return $('#dtable').DataTable().page.info().pages;
""")

print("Total Pages:", total_pages)

# ----------------------------------
# PAGINATION USING JS API (BEST WAY)
# ----------------------------------
for page in range(total_pages):
    driver.execute_script(f"""
        $('#dtable').DataTable().page({page}).draw('page');
    """)
    time.sleep(1)

    rows = driver.find_elements(By.CSS_SELECTOR, "#dtable tbody tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        all_rows.append([c.text.strip() for c in cols])

# ----------------------------------
# CLEAN EXIT (NO WinError 6)
# ----------------------------------
driver.service.process = None
driver.quit()

# ----------------------------------
# SAVE TO EXCEL
# ----------------------------------
df = pd.DataFrame(all_rows, columns=headers)
df.to_excel("TN_Government_Engineering_Colleges.xlsx", index=False)

print("✅ Scraping completed successfully")
