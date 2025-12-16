import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

URL = "http://www.ipu.ac.in/listinstitute041018.php"

# ---------- Chrome Options ----------
options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)

def scrape_table(table_element):
    rows = table_element.find_elements(By.TAG_NAME, "tr")
    data = []

    for row in rows[2:]:  # skip heading rows
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 3:
            continue

        sno = cols[0].text.strip()
        institute = cols[1].text.strip()

        # Website handling (anchor or plain text)
        try:
            link = cols[2].find_element(By.TAG_NAME, "a")
            website = link.get_attribute("href")
        except:
            website = cols[2].text.strip()

        data.append({
            "S.No": sno,
            "Institute Name & Address": institute,
            "Website": website
        })

    return pd.DataFrame(data)

try:
    driver.get(URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    tables = driver.find_elements(By.TAG_NAME, "table")

    # First table = Part A
    df_A = scrape_table(tables[0])

    # Second table = Part B
    df_B = scrape_table(tables[1])

    # ---------- Save to Excel (2 Sheets) ----------
    with pd.ExcelWriter("Guru_Gobind_Singh_Indraprastha_University_Delhi(2018-2019).xlsx", engine="openpyxl") as writer:
        df_A.to_excel(writer, sheet_name="A_Government_Institutes", index=False)
        df_B.to_excel(writer, sheet_name="B_Self_Financed_Institutes", index=False)

    print("✅ Scraping completed. Excel saved as IPU_Institutes_2018_19.xlsx")

finally:
    driver.quit()
