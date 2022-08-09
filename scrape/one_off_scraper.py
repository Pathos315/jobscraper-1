import re
from contextlib import suppress
from time import sleep

from requests import RequestException
from requests_html import HTMLResponse, HTMLSession

from scrape.configs import CompanyResult
from scrape.log import logger

GREENHOUSE_PATTERN = re.compile(r".*(greenhouse).*")


def one_time_scraper() -> CompanyResult:  # type: ignore
    """Takes the params provided in main.py and generates dataclasses for
    each job listing in BuiltInNYC, the job name, company info, and so forth.
    """
    logger.info("Performing one off scrape...")
    with suppress(RequestException):
        link: str = input("Please paste the URL here, then Press Enter...")
        session = HTMLSession()
        sleep(2.0)
        response: HTMLResponse = session.get(link)  # type: ignore
        logger.info(response.status_code)
        page_title: str = response.html.find("title", first=True).text  # type: ignore
        logger.info(page_title)
        ghousePattern = GREENHOUSE_PATTERN.search(response.url)
        matchObj = (
            re.search(r"(?:Job Application for)(\b.*\b)(?:at)(\b.*)", page_title)
            if ghousePattern
            else re.search(r"(\b.*\b)(?:at)(\b.*)(?:[\|\-])", page_title)
        )
        try:
            page_content = response.html.xpath("//*[@id='content']", first=True).text  # type: ignore
        except:
            page_content = "job_desc"
        logger.info(page_content)
        company_dict = {
            "company_name": matchObj.group(2) if matchObj else "",
            "job_name": matchObj.group(1) if matchObj else "",
            "job_description": page_content,
            "url": response.url,
        }
        return CompanyResult(**company_dict)
