import glob
import pandas as pd
from datetime import date

today = date.today()


# Get data file names
def get_transformed_data(path):
    filenames = glob.glob(path + "/*.csv")

    dfs = []
    for filename in filenames:
        dfs.append(pd.read_csv(filename))

    # Concatenate all data into one DataFrame
    big_frame = pd.concat(dfs, ignore_index=True)

    data_for_upload = big_frame[['Tender ID :', 'Tender Title :', 'Work Description', 'Organisation Chain', 'Title',
                                 'Tender Value in ₹', 'Tender Ref No :', 'Published Date', 'Bid Validity(Days)',
                                 'Is Multi Currency Allowed For BOQ',
                                 'Bid Opening Date', 'Tender Category', 'Tender Type', 'Form of contract',
                                 'Product Category', 'Allow Two Stage Bidding', 'Allow Preferential Bidder',
                                 'Payment Mode', 'Status', 'Bid Number', 'Contract Date :', 'Awarded Value']]

    data_for_upload['Status'] = data_for_upload['Status'].drop_duplicates(keep='first')
    data_for_upload['department'] = data_for_upload['Organisation Chain'].str.split("|", expand=True)[0]
    #data_for_upload = data_for_upload.drop(["Bid Number"], axis=1)
    data_for_upload.dropna(axis=0, how='all', inplace=True)
    data_temp = data_for_upload[['Tender ID :', 'Bid Number']]
    data_temp['Tender ID :'] = data_temp['Tender ID :'].fillna(method='ffill')
    no = pd.DataFrame()
    no = data_temp.groupby("Tender ID :").size().reset_index(drop=True)
    data_for_upload['no of bids received'] = no
    data_to_upload_final = pd.DataFrame()
    data_to_upload_final['ocid'] = "ocds-kjhdrl" + "-" + data_for_upload['Tender ID :']
    data_to_upload_final['initiationType'] = "tender"
    data_to_upload_final['tag'] = "tender"
    data_to_upload_final['id'] = 1
    data_to_upload_final['date'] = today
    data_to_upload_final['ocid'] = data_for_upload['Tender ID :'] + "-" + "ocds-kjhdrl"
    data_to_upload_final['initiationType'] = "tender"
    data_to_upload_final['tag'] = "tender"
    data_to_upload_final['id'] = 1
    data_to_upload_final['date'] = today
    data_to_upload_final['tender/id'] = data_for_upload['Tender ID :']
    data_to_upload_final['tender/externalReference'] = data_for_upload['Tender Ref No :']
    data_to_upload_final['tender/title'] = data_for_upload['Tender Title :']
    data_to_upload_final['tender/mainProcurementCategory'] = data_for_upload['Tender Category']
    data_to_upload_final['tender/procurementMethod'] = data_for_upload['Tender Type']
    data_to_upload_final['tender/contractType'] = data_for_upload['Form of contract']
    data_to_upload_final['tenderclassification/description'] = data_for_upload['Product Category']
    data_to_upload_final['tender/submissionMethodDetails'] = ""
    data_to_upload_final['tender/participationFee/0/multiCurrencyAllowed'] = data_for_upload[
        'Is Multi Currency Allowed For BOQ']
    data_to_upload_final['tender/allowTwoStageTender'] = data_for_upload["Allow Two Stage Bidding"]
    data_to_upload_final['tender/value/amount'] = data_for_upload['Tender Value in ₹']
    data_to_upload_final['tender/datePublished'] = data_for_upload['Published Date']
    data_to_upload_final['tender/milestones/title'] = "PreBid Meeting Date"
    data_to_upload_final['tender/milestones/code'] = "PreBid Meeting Date"
    data_to_upload_final['tender/milestones/type'] = "engagement"
    data_to_upload_final['tender/milestones/dueDate'] = data_for_upload['Bid Opening Date']
    data_to_upload_final['tender/tenderPeriod/durationInDays'] = data_for_upload['Bid Validity(Days)']
    data_to_upload_final['tender/allowPreferentialBidder'] = data_for_upload['Allow Preferential Bidder']
    data_to_upload_final['Payment Mode'] = data_for_upload['Payment Mode']
    data_to_upload_final['tender/status'] = data_for_upload['Status']
    data_to_upload_final['tender/stage'] = ""
    data_to_upload_final['tender/numberOfTenderers'] = data_for_upload['no of bids received']
    data_to_upload_final['tender/bidOpening/date'] = data_for_upload['Bid Opening Date']
    data_to_upload_final['tender/milestones/type'] = "assessment"
    data_to_upload_final['tender/milestones/title'] = "Price Bid Opening Date"
    data_to_upload_final['tender/milestones/dueDate'] = ""
    data_to_upload_final['tender/documents/id'] = ""
    data_to_upload_final['buyer/name'] = data_for_upload['department']
    data_to_upload_final['Fiscal Year'] = pd.to_datetime(data_to_upload_final['tender/bidOpening/date']).dt.to_period(
        'Q-APR').dt.qyear.apply(lambda x: str(x - 1) + "-" + str(x))

    data_to_upload_final.to_csv("data_to_upload_latest.csv", index=False)


if __name__ == "__main__":
    get_transformed_data("path/to/folder")