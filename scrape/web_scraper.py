from json import loads
from json.decoder import JSONDecodeError
from time import sleep
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, RequestException

from scrape.log import logger


def webscrape_results(
    target_url: str, run_beautiful_soup: bool = False, querystring: str | None = None
) -> BeautifulSoup | Any:
    """webscrape_results takes a target_url, run_beautiful_soup,
    and querystring to extract results for further parsing purposes.

    Args:
        - target_url (str): a website to be scraped
        - run_beautiful_soup (bool): an ID that determines the output.
            False is for JSON scraping.
            True is for HTML scraping with BeautifulSoup.
        Defaults to False.
        - querystring (Optional[str], optional):
        A querystring to govern the requested results. Defaults to None.

    Returns:
        Any: Is either text from JSON, text from BeautifulSoup, or None if no results were found.
    """
    sleep(1.5)
    try:
        response = requests.get(target_url, params=querystring)
        logger.info(response.status_code)
        if run_beautiful_soup:
            return BeautifulSoup(response.text, "html.parser")
        return loads(response.text)
    except (JSONDecodeError, RequestException, HTTPError, AttributeError) as exception:
        logger.error(
            f"An error has occurred, moving to next item in sequence.\
            Cause of error: {exception}"
        )
