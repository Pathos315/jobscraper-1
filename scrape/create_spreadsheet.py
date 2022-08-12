#TODO incorporate this into main.py strategy pattern

import random
from datetime import date

import pandas as pd
from googlesearch import search

from scrape.configs import CompanyResult, JobScrapeConfig  # type: ignore
from scrape.dir import change_dir
from scrape.log import logger  # type: ignore


def export_data(dataframe: pd.DataFrame, export_dir: str):
    """Export data to the specified export directory.
    If it's a dataframe, then it returns a .csv file.
    """
    date_ = date.today().strftime("%y%m%d")
    with change_dir(export_dir):
        print_id = random.randint(0, 100)
        export_name = f"{date_}_sciscraper_{print_id}.csv"
        logger.info(f"A spreadsheet was exported as {export_name} in {export_dir}.")
        if isinstance(dataframe, pd.DataFrame):
            dataframe.to_csv(export_name)
            logger.info(f"\n\n{dataframe.head(10)}")
            logger.info(f"\n\n{dataframe.tail(10)}")


class Spreadsheet:
    """_summary_"""

    def __init__(
        self,
        company: CompanyResult,
        config: JobScrapeConfig,
    ):
        self.company = company
        self.config = config
        self.all_links = list[str]

    def make_data_entries(self) -> dict[str, str | list[str]]:  # type: ignore
        """parse_provided_search_queries searches
        for contact information based on urls
        and source page data."""

        search_results = search(
            query=f'"{self.company.company_name}" \
                        {self.config.search_query}',
            stop=1,
            pause=3,
            country="US",
            verify_ssl=False,
        )
        self.all_links = [link for link in search_results]

        data_entry: dict[str, str | list[str]] = {
            "company": self.company.company_name,
            "job": self.company.job_name,
            "job_desc": self.company.job_description,
            "listings": self.all_links,
        }

        return data_entry


def make_dataframe(all_data_entries: list[dict[str, str | list[str]]]):
    df = pd.DataFrame(all_data_entries)
    return export_data(df, "jobscrape_spreadsheets")
