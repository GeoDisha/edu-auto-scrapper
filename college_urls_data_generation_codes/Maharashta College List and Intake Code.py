"""
fetch_institutes_to_excel.py

Fetch institute list from:
https://fe2025.mahacet.org/StaticPages/frmInstituteList?did=1884

Follow each institute link like:
frmInstituteSummary.aspx?InstituteCode=01002

Write results into Excel: institutes.xlsx
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

BASE_PAGE = "https://fe2025.mahacet.org/StaticPages/frmInstituteList?did=1884"
BASE_ROOT = "https://fe2025.mahacet.org/StaticPages/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InstituteScraper/1.0; +https://example.com/bot)"
}

def get_soup(url, session, retry=3, backoff=1.0):
    for attempt in range(retry):
        try:
            r = session.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            if attempt == retry - 1:
                raise
            time.sleep(backoff * (attempt + 1))
    raise RuntimeError("unreachable")

def parse_list_table(soup):
    """
    Looks for table with id or class similar to the sample:
    id="rightContainer_ContentTable1_gvInstituteList" or class="DataGrid"
    Returns list of dict rows.
    """
    table = soup.find("table", id=lambda x: x and "gvInstituteList" in x) \
            or soup.find("table", class_="DataGrid") \
            or soup.find("table")

    rows_out = []
    if not table:
        return rows_out

    tbody = table.find("tbody") or table
    rows = tbody.find_all("tr")
    # header detection: skip the first header row (th)
    for tr in rows:
        # skip header rows
        if tr.find_all("th"):
            continue
        tds = tr.find_all("td")
        if not tds:
            continue

        # Defensive parsing: some pages may have different td counts
        try:
            sr_no = tds[0].get_text(strip=True)
            inst_code_td = tds[1]
            inst_code_a = inst_code_td.find("a")
            if inst_code_a:
                inst_code = inst_code_a.get_text(strip=True)
                inst_rel_link = inst_code_a.get("href", "").strip()
                inst_url = urljoin(BASE_ROOT, inst_rel_link)
            else:
                inst_code = inst_code_td.get_text(strip=True)
                inst_url = ""

            inst_name = tds[2].get_text(strip=True) if len(tds) > 2 else ""
            status = tds[3].get_text(strip=True) if len(tds) > 3 else ""
            total_intake = tds[4].get_text(strip=True) if len(tds) > 4 else ""

            rows_out.append({
                "SrNo": sr_no,
                "InstituteCode": inst_code,
                "InstituteURL": inst_url,
                "InstituteName": inst_name,
                "Status": status,
                "TotalIntake": total_intake
            })
        except Exception:
            # skip malformed row but continue
            continue

    return rows_out

def fetch_summary_text(url, session):
    """
    Fetch the summary page and return short cleaned text + raw_html.
    If the page contains structured fields, you could extend parsing here.
    """
    if not url:
        return {"summary_text": "", "raw_html": ""}

    try:
        soup = get_soup(url, session)
    except Exception as e:
        return {"summary_text": f"ERROR: {e}", "raw_html": ""}

    # collapse visible text
    # remove script/style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.stripped_strings)
    # truncate extremely long text for Excel cell if needed, but we keep full text here
    return {"summary_text": text, "raw_html": str(soup)}

def main():
    session = requests.Session()

    print("Fetching list page:", BASE_PAGE)
    soup_list = get_soup(BASE_PAGE, session)

    print("Parsing institute table...")
    institutes = parse_list_table(soup_list)
    if not institutes:
        print("No rows found in table. Exiting.")
        return

    print(f"Found {len(institutes)} institutes. Fetching individual summaries (may take a while)...")

    # We'll collect summary results in a list
    summaries = []
    for i, inst in enumerate(institutes, start=1):
        code = inst.get("InstituteCode")
        url = inst.get("InstituteURL")
        print(f"[{i}/{len(institutes)}] {code} -> {url or 'NO URL'}")
        summary = fetch_summary_text(url, session) if url else {"summary_text": "", "raw_html": ""}
        summaries.append({
            "InstituteCode": code,
            "InstituteURL": url,
            "SummaryText": summary["summary_text"],
            # raw html can be very large; include anyway in case user wants it
            "SummaryHTML": summary["raw_html"][:1000000]  # cap to 1M chars to avoid memory blowup
        })
        # polite pause to avoid hammering server
        time.sleep(0.5)

    # convert to DataFrames
    df_list = pd.DataFrame(institutes)
    df_summ = pd.DataFrame(summaries)

    out_file = "institutes.xlsx"
    print("Writing to Excel:", out_file)
    with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
        df_list.to_excel(writer, sheet_name="InstituteList", index=False)
        df_summ.to_excel(writer, sheet_name="Summaries", index=False)

    print("Done. Output file:", out_file)

if __name__ == "__main__":
    main()
