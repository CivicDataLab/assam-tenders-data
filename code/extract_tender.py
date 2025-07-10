import os
from bs4 import BeautifulSoup
import pandas as pd

def extract_tender_data(view_file, summary_file):
    with open(view_file, "r", encoding="utf-8") as f:
        view_html = f.read()
    with open(summary_file, "r", encoding="utf-8") as f:
        summary_html = f.read()

    view_soup = BeautifulSoup(view_html, "html.parser")
    summary_soup = BeautifulSoup(summary_html, "html.parser")

    data = {}

    # From view.html
    view_table = view_soup.find("table", class_="list_table")
    if view_table:
        for row in view_table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) == 2:
                label = cols[0].text.strip().replace(":", "")
                value = cols[1].text.strip()
                data[label] = value

    # From summary.html
    summary_tables = summary_soup.find_all("table", class_="table_list")

    for table in summary_tables:
        section_head = table.find("td", class_="section_head")
        if not section_head:
            continue

        section_name = section_head.text.strip()
        if section_name == "Awarded Bids List":
            rows = table.find_all("tr")[2:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 5:
                    data["Awarded Bidder"] = cols[2].text.strip()
                    data["Awarded Value"] = cols[4].text.strip()
                    data["Awarded Currency"] = cols[3].text.strip()
        elif section_name == "AOC":
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) == 2:
                    key = cols[0].text.strip().replace(":", "")
                    value = cols[1].text.strip()
                    data[key] = value

    return data

def process_all_folders(root_dir, output_csv= r"D:\CDL\Tender Data\UP 2024\Jan-Feb\jan-feb.csv"):
    all_rows = []

    for subdir, dirs, files in os.walk(root_dir):
        tenders = {}
        for file in files:
            if file.endswith(".html"):
                tid = file.replace("_view.html", "").replace("_summary.html", "")
                tenders.setdefault(tid, {})[file] = os.path.join(subdir, file)

        for tender_id, file_dict in tenders.items():
            view_path = file_dict.get(f"{tender_id}_view.html")
            summary_path = file_dict.get(f"{tender_id}_summary.html")
            if view_path and summary_path:
                try:
                    row = extract_tender_data(view_path, summary_path)
                    row["Tender ID"] = tender_id
                    all_rows.append(row)
                except Exception as e:
                    print(f"Error processing {tender_id}: {e}")

    # Save to CSV
    df = pd.DataFrame(all_rows)
    df.to_csv(output_csv, index=False)
    print(f"All tenders saved to{output_csv}")


process_all_folders(r"D:\CDL\saved-html")
