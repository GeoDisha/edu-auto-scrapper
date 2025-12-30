#open the browser and go to the Sarvajanik University Surat colleges page and scrape the list of colleges along with their categories and URLs, then save the data to an Excel file.
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

URL = "https://www.ses-surat.org/pages/colleges/"

# ---------- Chrome Options ----------
options = uc.ChromeOptions()
options.add_argument("--headless=new")   # headless
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

# ---------- Start Driver ----------
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)

try:
    driver.get(URL)

    # wait for table
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))

    rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")

    data = []
    current_category = None

    for row in rows:
        # Category row
        if "active" in row.get_attribute("class"):
            current_category = row.text.strip()
            continue

        # College rows
        try:
            link = row.find_element(By.TAG_NAME, "a")
            college_name = link.text.strip()
            college_url = link.get_attribute("href")

            data.append({
                "Category": current_category,
                "College Name": college_name,
                "URL": college_url
            })

        except:
            continue

    # ---------- Save to Excel ----------
    df = pd.DataFrame(data)
    df.to_excel("SES_Surat_Colleges.xlsx", index=False)

    print("✅ Scraping completed. File saved as SES_Surat_Colleges.xlsx")

finally:
    driver.quit()
