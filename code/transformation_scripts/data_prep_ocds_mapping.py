import glob
import pandas as pd
from datetime import date

today = date.today()


def get_transformed_data(path):
    # Get data file names
    filenames = glob.glob(path + "/*.csv")

    dfs = []
    for filename in filenames:
        dfs.append(pd.read_csv(filename))

    # Concatenate all data into one DataFrame
    big_frame = pd.concat(dfs, ignore_index=True)

    # Create an explicit copy of the selected columns
    columns_to_keep = [
        'Tender ID :', 'Tender Title :', 'Work Description', 'Organisation Chain', 'Title',
        'Tender Value in ₹', 'Tender Ref No :', 'Published Date', 'Bid Validity(Days)',
        'Is Multi Currency Allowed For BOQ', 'Bid Opening Date', 'Tender Category',
        'Tender Type', 'Form of contract', 'Product Category', 'Allow Two Stage Bidding',
        'Allow Preferential Bidder', 'Payment Mode', 'Status',
        'Contract Date :', 'Awarded Value'
    ]
    data_for_upload = big_frame[columns_to_keep].copy()

    # Fix the Status column using loc
    data_for_upload.loc[:, 'Status'] = data_for_upload['Status'].drop_duplicates(keep='first')

    # Create department column using loc
    data_for_upload.loc[:, 'department'] = data_for_upload['Organisation Chain'].str.split("|", expand=True)[0]

    # Drop Bid Number column
    #data_for_upload = data_for_upload.drop(["Bid Number"], axis=1)

    # Remove rows where all values are NA
    data_for_upload.dropna(axis=0, how='all', inplace=True)

    # Create temporary dataframe for bid counting
    data_temp = data_for_upload[['Tender ID :']].copy()
    data_temp.loc[:, 'Tender ID :'] = data_temp['Tender ID :'].fillna(method='ffill')

    # Count bids
    no = data_temp.groupby("Tender ID :").size().reset_index(drop=True)
    data_for_upload.loc[:, 'no of bids received'] = no

    # Create final output dataframe
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
        'tender/datePublished': data_for_upload['Published Date'],
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

    # Save to CSV
    data_to_upload_final.to_csv("data_to_upload_latest.csv", index=False)


if __name__ == "__main__":
    get_transformed_data(r"C:\Users\AAKASH\Desktop\go\unmapped_jan-sep2024")