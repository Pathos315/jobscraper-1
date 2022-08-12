from time import perf_counter
from typing import Any

from tqdm import tqdm

from scrape.builtinscrape import parse_results
from scrape.configs import CompanyResult, read_config
from scrape.coverletterwriter import CoverLetterWriter
from scrape.create_spreadsheet import Spreadsheet, make_dataframe
from scrape.log import logger
from scrape.namefetcher import NameFetcher
from scrape.one_off_scraper import one_time_scraper

config, persona = read_config("./config.json")

querystring: dict[str, str | int | Any] = config.querystring
builtinnyc: str = config.url_builtin
total_pages = config.total_pages


def create_spreadsheets():
    """doc_str"""
    all_data_entries = []
    logger.info("Initializing spreadsheet creation...")
    for page in range(0, total_pages):
        page_dict = {"page": page}
        querystring.update(page_dict)
        company_collection = parse_results(builtinnyc, querystring, page, config)

        for idx, company in enumerate(
            tqdm(company_collection, desc="Creating Spreadsheets", unit="contact")
            ):
            spreadsheet = Spreadsheet(company, config).make_data_entries()
            all_data_entries.append(spreadsheet)
    make_dataframe(all_data_entries)


def create_cover_letter():
    """doc_str"""
    logger.info("Initializing one time scrape...")
    company: CompanyResult = one_time_scraper() #type: ignore
    business_card = NameFetcher(
        company=company, config=config
    ).parse_provided_search_queries()
    logger.info(
        "Writing cover letter to %s at %s for the role of %s",
        business_card.fullname,
        business_card.workplace,
        company.job_name,
    )
    CoverLetterWriter(
        company, contact=business_card, persona=persona, config=config
    ).write()


def create_unfaciliated_cover_letters_in_bulk():
    """doc_str"""
    logger.info("Initializing Jobscraper Program...")

    for page in range(0, total_pages):
        page_dict = {"page": page}
        querystring.update(page_dict)
        company_collection = parse_results(builtinnyc, querystring, page, config)

        for idx, company in enumerate(
            tqdm(company_collection, desc="Writing Letter", unit="contact")
        ):
            business_card = NameFetcher(
                company=company, config=config
            ).parse_provided_search_queries()

            logger.info(
                "Writing cover letter to %s at %s for the role of %s",
                business_card.fullname,
                business_card.workplace,
                company_collection[idx].job_name,
            )
            CoverLetterWriter(
                company, contact=business_card, persona=persona, config=config
            ).write()


def strategy(key: str):
    """doc_str"""
    STRATEGIES = {
        "bulk": create_unfaciliated_cover_letters_in_bulk,
        "once": create_cover_letter,
        "sheet": create_spreadsheets,
    }
    return STRATEGIES[key]()


def main(key: str) -> None:
    """jobscraper takes the provided querystring, searches for job results,
    and for each of those job results generates a cover letter.
    """
    start = perf_counter()
    strategy(key)
    logger.info("Gathering configuration for Jobscraper...")

    elapsed = perf_counter() - start
    logger.info("Job search finished in %s seconds.", elapsed)  # type: ignore


if __name__ == "__main__":
    main("bulk")
