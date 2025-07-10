import os
import json
import requests

#URLs
VIEW_MORE_BASE = "https://etender.up.nic.in/nicgep/app?component=view&page=WebTenderStatusLists&service=direct&session=T&sp="
STAGE_SUMMARY_BASE = "https://etender.up.nic.in/nicgep/app?component=$DirectLink_0&page=WebTenderStatus&service=direct&session=T&sp="

# Paths in local
SP_TOKEN_FILE = r"C:\Users\cdl\Desktop\Scrapper\assam-tenders-data\code\scraper\scraped_recent_tenders\sp_tokens.json"
OUTPUT_DIR = r"D:\CDL\saved-html"
COOKIE_FILE = r"C:\Users\cdl\Desktop\Scrapper\assam-tenders-data\code\scraper\scraped_recent_tenders\cookies.json"

def load_cookies_as_dict(cookie_file):
    with open(cookie_file, "r") as f:
        cookies = json.load(f)
    return {cookie['name']: cookie['value'] for cookie in cookies}

def save_html_responses():
    with open(SP_TOKEN_FILE, "r") as f:
        sp_data = json.load(f)

    cookies_dict = load_cookies_as_dict(COOKIE_FILE)

    session = requests.Session()
    session.cookies.update(cookies_dict)

    for page, tenders in sp_data.items():
        page_folder = os.path.join(OUTPUT_DIR, page)
        os.makedirs(page_folder, exist_ok=True)

        for tender_id, sp_token in tenders.items():
            view_url = VIEW_MORE_BASE + sp_token
            summary_url = STAGE_SUMMARY_BASE + sp_token

            try:
                view_response = session.post(view_url, timeout=30)
                view_path = os.path.join(page_folder, f"{tender_id}_view.html")
                with open(view_path, "w", encoding="utf-8") as f:
                    f.write(view_response.text)
            except Exception as e:
                print(f"Error fetching view page for {tender_id}: {e}")

            try:
                summary_response = session.post(summary_url, timeout=30)
                summary_path = os.path.join(page_folder, f"{tender_id}_summary.html")
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(summary_response.text)
            except Exception as e:
                print(f"Error fetching summary page for {tender_id}: {e}")

    print(f"HTML scraping complete. All files saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    save_html_responses()