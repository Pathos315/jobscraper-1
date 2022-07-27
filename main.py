from time import perf_counter
from typing import Any

from tqdm import tqdm

from scrape.builtinscrape import parse_results
from scrape.configs import read_config
from scrape.coverletterwriter import CoverLetterWriter
from scrape.create_spreadsheet import Comptroller, make_dataframe
from scrape.log import logger
from scrape.namefetcher import NameFetcher


def main(write_cover_letters: bool = False) -> None:
    """jobscraper takes the provided querystring, searches for job results,
    and for each of those job results generates a cover letter.
    """
    start = perf_counter()

    logger.info("Gathering configuration for Jobscraper...")
    config, persona = read_config("./config.json")
    querystring: dict[str, str | int | Any] = config.querystring
    builtinnyc: str = config.url_builtin

    logger.info("Initializing Jobscraper Program...")

    for page in range(0, config.total_pages):
        page_dict = {"page": page}
        querystring.update(page_dict)
        company_collection = parse_results(builtinnyc, querystring, page, config)

        if write_cover_letters:
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
                )  # type: ignore
                CoverLetterWriter(
                    company, contact=business_card, persona=persona, config=config
                ).write()

        else:
            all_data = []
            for idx, company in enumerate(
                tqdm(company_collection, desc="Generating Wrap Sheet", unit="listing")
            ):

                data = Comptroller(company=company, config=config).make_data_entries()
                all_data.append(data)
            make_dataframe(all_data)

    elapsed = perf_counter() - start
    logger.info("Job search finished in %s seconds.", elapsed)  # type: ignore


if __name__ == "__main__":
    main()
