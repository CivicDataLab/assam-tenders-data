### Motivation:
Finance department upload variety of fiscal data on internet which is open to use. This data is present on different portals, lacks metadata and is under layer of captchas.
Moreover these datasets are not machine readable.One of the verticals of fiscal ecosystem is contracts data, this data holds information on how Government is procuring projects such as road contruction.We started with the idea of increasing the usability of contract data uploaded by Assam Finance Department and bring all possible information under one roof.
Our motivation was to increase the transparency of contract data, which inturn will increase accountability.

### Data Composition:
* Fiscal year range: 2016-2017 to 2022-2023
* Geography: Assam, India
* Total number of departments that opened tender: 397
* Data dictionary: The file [`raw_data_fy_2016_2022.zip`](https://github.com/CivicDataLab/assam-tender-data/blob/data/data/RawData/raw_data_fy_2016_2022.zip) contains the following fields
  <br>
  
| Field Name | Description | Type |
|------------|-------------|------|
| Tender ID | An id to identify this tender. This can be used to derive the name of the department the tender belongs to. OCID has tender id as its suffix | String |
| Tender Reference No | Adds information on top of tender id describing the purpose of tender and place | String, Integer |
| Tender Title | Title of tender | String |
| Tender Category | The primary classification of the article | String |
| Tender Type | This describes the bidding method. This is a closed code list, therefore Open was converted to limited and global to open. This can be used to gain brief whether the tender is open for international participation. | String |
| Form of Contract | Describes the type of contract this includes: itemRate, Fixed-Rate, ItemWise, EOI, lumpSum, Percentage, Turn-key | String |
| Product Category | Procuring entity needs to select an option from the pre-populated list of product/service categories using a drop-down button. This is basically a classification system but not standardized and not even nearly exhaustive. | String |
| No of Covers | This refers to segregation of qualification information, technical proposal, financial bid, etc. during bid submission. Traditionally called 'cover' or 'envelope', in e-procurement terms it means folders to be created for bidders to upload their corresponding parts of bid. Generally each folder is opened at a different point in time, sequentially, filtering out a number of bidders at each stage. GePNIC (Assam's e-procurement portal) currently allows up to 4 covers. | Integer |
| Is Multi Currency Allowed for BOQ | Whether multi currency is allowed or not | Boolean |
| Two Stage Tender (Y/N) | Two stage tendering is used to allow the early appointment of a contractor, prior to the completion of all the information required to enable them to offer a fixed price. | Boolean |
| Value of Tender (In Rs) | The maximum estimated amount for the contract | Float |
| Published Date | The date on which the tender was published | Date |
| PreBid Meeting Date | This is a meeting prior to bid submission deadline aimed at hearing bidders' comments, queries and suggestions regarding the bidding documents. | Date |
| Tender Validity in Days | Number of days for which bid submission is allowed | Object |
| Preferential Bidding Allowed | A company may select certain investors to offer products or services through the use of contracts. | Boolean |
| Payment Mode | Mode of payment | String |
| Tender Status | Status of tender. This is a closed code list | String |
| Tender Stage | This field gives information about which step is tender in. | String |
| No of Bids Received | Number of bidders participated in the competition | Object |
| Bid Opening Date | Date on which bid is opened | Date |
| Price Bid Opening Date | In case of multiple covers, the financial bid opening date is different than the technical bid opening date. The procuring entity can notify the price bid opening date only after uploading technical evaluation details | Date |
| GeMARPTS ID | GeM Availability Report and Past Transaction Summary' Report. It is mandatory for central govt. organizations to generate this report prior to procuring any goods / non-consulting services outside GeM. (GeM is Government e-Marketplace gem.gov.in where goods and non-consulting services are listed like on e-commerce portals. Suppliers and Service Providers are verified and listed on the GeM platform by the Union (Central) Government. It is mandatory for all central government entities to procure on GeM. If a product or service is not available on GeM, the procuring entity can generate this GeM ARPTS Report - which is valid for 1 month - and can procure the same on e-procurement portal. The e-procurement portal captures and validates this GeMARPTS id. Without this step, a central government procuring entity cannot | Object |
| Organisation Chain | Organisation name chain which uses and pays for the tender. | String |

### Collection Process:
Please refer to scraping documentation https://github.com/CivicDataLab/assam-tender-data/tree/transformation/code/scraper

### Processing the data:
After scraping the dataset, with the help of [Open Contracting Partnership](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwji6Ybj372AAxWscmwGHU85Dj8QFnoECAkQAQ&url=https%3A%2F%2Fwww.open-contracting.org%2F&usg=AOvVaw2Cd-C2RvmJyspYjxMBhj55&opi=89978449) we mapped the data to[ Open Contracting Data Standards](https://standard.open-contracting.org/latest/en/). 
The Open Contracting Data Standard (OCDS) enables organisations to publish contracting process information at 
all the stages. OCDS defines a standard data model for publishing contracting process data and documents with the aim of improving 
transparency and consumability of governmental data. However, the data published by government is not in a consumable format and is behind captchas.
Therefore the importance of implementing OCDS are following

   * Promote the transparency in decision making
   * Provide data in machine readable formats
   * Increase consumption of contracting data across the globe
   * Provide ample amount of metadata to understand the contracting
#### Following are the mapped fields which you can find in https://github.com/CivicDataLab/assam-tender-data/tree/data/data/ProcessedData/ocds-mapped-data:
<br>

| Mapped Field | Title | Description | Type |
|-------|-------|-------------|------|
| tender/id | Tender ID | An id to identify this tender. This can be used to derive the name of the department the tender belongs to. OCID has tender id as its suffix | String |
| tender/externalReference | Tender Reference No | Adds information on top of tender id describing the purpose of tender and place | String, Integer |
| tender/title | Tender Title | Title of tender | String |
| tender/mainProcurementCategory | Tender Category | The primary classification of the article | String |
| tender/procurementMethod | Tender Type | This describes the bidding method. This is a closed code list, therefore Open was converted to limited and global to open. This can be used to gain brief whether the tender is open for international participation. | String |
| tender/contractType | Form of Contract | Describes the type of contract this includes: itemRate, Fixed-Rate, ItemWise, EOI, lumpSum, Percentage, Turn-key | String |
| tender/classification/description | Product Category | Procuring entity needs to select an option from the pre-populated list of product/service categories using a drop-down button. This is basically a classification system but not standardized and not even nearly exhaustive. | String |
| tender/submissionMethodDetails | No of Covers | This refers to segregation of qualification information, technical proposal, financial bid, etc. during bid submission. Traditionally called 'cover' or 'envelope', in e-procurement terms it means folders to be created for bidders to upload their corresponding parts of bid. Generally each folder is opened at a different point in time, sequentially, filtering out a number of bidders at each stage. GePNIC (Assam's e-procurement portal) currently allows up to 4 covers. | Integer |
| tender/participationFee/0/multipleCurrencyAllowed | Is Multi Currency Allowed for BOQ | Whether multi currency is allowed or not | Boolean |
| tender/allowTwoStageTender | Two Stage Tender (Y/N) | Two stage tendering is used to allow the early appointment of a contractor, prior to the completion of all the information required to enable them to offer a fixed price. | Boolean |
| tender/value/amount | Value of Tender (In Rs) | The maximum estimated amount for the contract | Float |
| tender/datePublished | Published Date | The date on which the tender was published | Date |
| tender/milestones/dueDate | PreBid Meeting Date | This is a meeting prior to bid submission deadline aimed at hearing bidders' comments, queries and suggestions regarding the bidding documents. | Date |
| tender/tenderPeriodDurationInDays | Tender Validity in Days | Number of days for which bid submission is allowed | Object |
| tender/allowPreferentialBidder | Preferential Bidding Allowed | A company may select certain investors to offer products or services through the use of contracts. | Boolean |
| Payment Mode | Payment Mode | Mode of payment | String |
| tender/status | Tender Status | Status of tender. This is a closed code list | String |
| tender/stage | Tender Stage | This field gives information about which step is tender in. | String |
| tender/numberOfTenderes | No of Bids Received | Number of bidders participated in the competition | Object |
| tender/bidOpening/date | Bid Opening Date | Date on which bid is opened | Date |
| tender/milestones/dueDate | Price Bid Opening Date | In case of multiple covers, the financial bid opening date is different than the technical bid opening date. The procuring entity can notify the price bid opening date only after uploading technical evaluation details | Date |
| tender/documents/id | GeMARPTS ID | GeM Availability Report and Past Transaction Summary' Report. It is mandatory for central govt. organizations to generate this report prior to procuring any goods / non-consulting services outside GeM. (GeM is Government e-Marketplace gem.gov.in where goods and non-consulting services are listed like on e-commerce portals. Suppliers and Service Providers are verified and listed on the GeM platform by the Union (Central) Government. It is mandatory for all central government entities to procure on GeM. If a product or service is not available on GeM, the procuring entity can generate this GeM ARPTS Report - which is valid for 1 month - and can procure the same on e-procurement portal. The e-procurement portal captures and validates this GeMARPTS id. Without this step, a central government procuring entity cannot | Object |
| buyer/name | Organisation Chain | Organisation name chain which uses and pays for the tender. | String |

For further information on cleaning and mapping the data please refer to https://github.com/CivicDataLab/assam-tender-data/tree/transformation/code/transformation_scripts

## How are we using the data:
OCDS mapped data is uploaded on [Assam Public Procurement Platform](https://assam.open-contracting.in/) under [contracts tab](https://assam.open-contracting.in/datasets?fq=&q=&sort=tender_bid_opening_date%3Aasc&size=&from=).
We have also calculated few Key Performance Indicators using OCDS mapped data under [data-analysis tab](https://assam.open-contracting.in/kpi?fq=&q=), one can filter the visualisatons and also download them.

## Maintenance: 
We are updating the data on the portal in every `three` months

## Links for reference:
* [Publication Policy ](https://docs.google.com/document/d/1O1ScJWqRozlCWNEBDqfwzJ97B6aauCx74CUx76_7DH4/edit?usp=sharing)
* [Assam Public Procurement Portal ](assam.open-contracting.in/)
* [Open Contracting Data Standards ](https://standard.open-contracting.org/latest/en/)
* [Open Contracting Partnership](https://standard.open-contracting.org/latest/en/)




