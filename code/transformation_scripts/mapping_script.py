import pandas as pd
import os
from datetime import date

today = date.today()

# Path to the folder containing raw CSVs
raw_csv_folder = r'C:\Users\AAKASH\Desktop\go\Assam Tenders json 2023\Assam_tender_data raw FY 21-22'

# List of required columns matching data_prep_ocds_mapping.py
required_columns = [
    'Tender ID :', 'Tender Title :', 'Work Description', 'Organisation Chain', 'Title',
    'Tender Value in ₹', 'Tender Ref No :', 'Publish Date', 'Bid Validity(Days)',
    'Is Multi Currency Allowed For BOQ', 'Bid Opening Date', 'Tender Category',
    'Tender Type', 'Form of contract', 'Product Category', 'Allow Two Stage Bidding',
    'Allow Preferential Bidder', 'Payment Mode', 'Status',
    'Contract Date :', 'Awarded Value'
]

# Fields to be treated as integers
int_fields = ['Bid Validity(Days)']


def safe_int_convert(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def process_tenders_data(raw_csv_folder):
    # Create empty DataFrame with required columns
    data_for_upload = pd.DataFrame(columns=required_columns)

    # Iterate over each CSV in the folder
    for file_name in os.listdir(raw_csv_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(raw_csv_folder, file_name)
            print(f"Processing: {file_name}")

            # Read the raw CSV
            raw_data = pd.read_csv(file_path, dtype=str)

            # Extracting relevant data
            tender_info = {}
            for column in required_columns:
                if column in int_fields:
                    matching_columns = [col for col in raw_data.columns if col.strip() == column]
                    if matching_columns:
                        value = raw_data[matching_columns[0]].dropna().iloc[0] if not raw_data[
                            matching_columns[0]].dropna().empty else None
                        tender_info[column] = safe_int_convert(value)
                    else:
                        tender_info[column] = None
                else:
                    column_data = raw_data[
                        raw_data.columns[raw_data.columns.str.contains(column, case=False, na=False)]]
                    if not column_data.empty:
                        first_value = column_data.iloc[:, 0].dropna().iloc[0] if not column_data.iloc[:,
                                                                                     0].dropna().empty else ''
                        tender_info[column] = first_value.strip() if isinstance(first_value, str) else first_value
                    else:
                        tender_info[column] = ''

            # Append this tender's information
            data_for_upload = data_for_upload.append(tender_info, ignore_index=True)

    # Post-processing steps from data_prep_ocds_mapping.py
    data_for_upload.loc[:, 'Status'] = data_for_upload['Status'].drop_duplicates(keep='first')
    data_for_upload.loc[:, 'department'] = data_for_upload['Organisation Chain'].str.split("|", expand=True)[0]
    #data_for_upload = data_for_upload.drop(["Bid Number"], axis=1)
    data_for_upload.dropna(axis=0, how='all', inplace=True)

    # Handle bid counting
    data_temp = data_for_upload[['Tender ID :']].copy()
    data_temp.loc[:, 'Tender ID :'] = data_temp['Tender ID :'].fillna(method='ffill')
    no = data_temp.groupby("Tender ID :").size().reset_index(drop=True)
    data_for_upload.loc[:, 'no of bids received'] = no

    # Create final OCDS mapping
    data_to_upload_final = pd.DataFrame()

    # Map columns to OCDS format
    mapping = {
        'ocid': "ocds-f5kvwu-" + data_for_upload['Tender ID :'],
        'initiationType': "tender",
        'tag': "tender",
        'id': 1,
        'date': today,
        'tender/id': data_for_upload['Tender ID :'],
        'tender/externalReference': data_for_upload['Tender Ref No :'],
        'tender/title': data_for_upload['Tender Title :'],
        'tender/mainProcurementCategory': data_for_upload['Tender Category'],
        'tender/procurementMethod': data_for_upload['Tender Type'],
        'tender/contractType': data_for_upload['Form of contract'],
        'tenderclassification/description': data_for_upload['Product Category'],
        'tender/submissionMethodDetails': "",
        'tender/participationFee/0/multiCurrencyAllowed': data_for_upload['Is Multi Currency Allowed For BOQ'],
        'tender/allowTwoStageTender': data_for_upload["Allow Two Stage Bidding"],
        'tender/value/amount': data_for_upload['Tender Value in ₹'],
        'tender/datePublished': data_for_upload['Publish Date'],
        'tender/tenderPeriod/durationInDays': data_for_upload['Bid Validity(Days)'],
        'tender/allowPreferentialBidder': data_for_upload['Allow Preferential Bidder'],
        'Payment Mode': data_for_upload['Payment Mode'],
        'tender/status': data_for_upload['Status'],
        'tender/stage': "",
        'tender/numberOfTenderers': data_for_upload['no of bids received'],
        'tender/bidOpening/date': data_for_upload['Bid Opening Date'],
        'tender/milestones/type': "assessment",
        'tender/milestones/title': "Price Bid Opening Date",
        'tender/milestones/dueDate': "",
        'tender/awardedAmount': data_for_upload['Awarded Value'],
        'tender/documents/id': "",
        'buyer/name': data_for_upload['department']

    }

    # Assign all columns at once
    for col, values in mapping.items():
        data_to_upload_final[col] = values

    # Calculate fiscal year
    data_to_upload_final['Fiscal Year'] = pd.to_datetime(
        data_to_upload_final['tender/bidOpening/date']
    ).dt.to_period('Q-APR').dt.qyear.apply(
        lambda x: f"{x - 1}-{x}"
    )

    return data_to_upload_final


if __name__ == "__main__":
    # Process the data
    final_data = process_tenders_data(raw_csv_folder)

    # Save the final DataFrame to a new CSV file
    output_path = r"C:\Users\AAKASH\Desktop\go\Assam Tenders json 2023\Assam Tenders FY 23-24.csv"
    final_data.to_csv(output_path, index=False)
    print(f"CSV created successfully at {output_path}")