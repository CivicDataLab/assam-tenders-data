## Assam Public Procurement Data [2016 - 2022]

[![][cover]](https://assam.open-contracting.in/)

### About
The fiscal ecosystem operates as a hierarchical system facilitating the flow of funds. At its most granular level, the process involves tendering, where government departments solicit bids for various projects, such as constructing a ramp for a school. In our efforts to enhance the efficiency and transparency of this system, we have created the [Assam Public Procurement Platform](assam.open-contracting.in/), specifically for the state of Assam in India. This platform is designed to promote transparency by consolidating all tender information in one central location.

The Assam government regularly uploads contract data on the [etenders platform](https://assamtenders.gov.in/nicgep/app), with new data added almost daily. Unfortunately, the data on this platform is fragmented and often protected by captchas, creating significant hurdles for users attempting to analyze it effectively. To address this issue, we have employed web scraping techniques to collect and organize the data in a user-friendly and comprehensible format. This involved developing multiple scrapers and implementing various data transformations to achieve our goal.

### Directory Structure
- code
  - scraper
  - transformation_scripts
- data
  - ProcessedData
  - RawData

### Process
- [Data mining](code/scraper/README.md)
- [Data Transformations](data/README.md)

### Data Update Frequecy
We update the platform with new data in every 3 months

### License
All scripts are published under the [GPL v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html#SEC1) license and all datasets are published under the [Open Data Commons Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/summary/).

### Contact Us:
In case of any queries or concerns reach out at open-contracting@civicdatalab.in


[cover]: https://github-production-user-asset-6210df.s3.amazonaws.com/5118689/270608627-f7d654c8-d077-4d03-a616-7e7b682c1fc5.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20230926%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230926T094528Z&X-Amz-Expires=300&X-Amz-Signature=3987f344c411b85b1eb404fc87fb92aa6ad3ec89360af4f81db6d75c365ba5a4&X-Amz-SignedHeaders=host&actor_id=5118689&key_id=0&repo_id=673297437
