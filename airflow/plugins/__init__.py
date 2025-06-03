from airflow.plugins_manager import AirflowPlugin
from operators.web_scraper_operator import WebScraperOperator

class AssamTendersPlugin(AirflowPlugin):
    name = "assam_tenders_plugin"
    operators = [WebScraperOperator]
