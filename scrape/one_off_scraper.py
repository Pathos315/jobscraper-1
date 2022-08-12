import re
from json import loads
from time import sleep

from googlesearch import get_random_user_agent
from requests import request
from requests_html import HTMLResponse, HTMLSession

from scrape.configs import CompanyResult
from scrape.log import logger

WHITESPACE_CLEANING = re.compile(r"(\s+)")
JSON_CLEANING_PATTERN = re.compile(
    r"(?:(\\n)|(\\)|(<.{0,5}>)|(\>{1})|(<a))|(xa0)|[\]\[]",
    flags=re.IGNORECASE,
)
GREENHOUSE_PATTERN = re.compile(r"(?P<reference>greenhouse)")
GREENHOUSE_TITLE = re.compile(
    r"(?:Job Application for)(?P<job>\b.*\b)(?:at)(?P<company>\b.*)"
)
WORKDAY_PATTERN = re.compile(r"(?P<reference>workday)", flags=re.IGNORECASE)
ORACLE_TITLE = re.compile(r"(?P<job>\b.*\b)(?:at)(?P<company>\b.*)(?:[\|\-])")
WORKDAY_COMPANY = re.compile(r"(?P<company>.*) (?:is committed to a)")


def one_time_scraper():
    """Takes the params provided in main.py and generates dataclasses for
    each job listing in BuiltInNYC, the job name, company info, and so forth.
    """
    logger.info("Performing one off scrape...")
    link: str = input("Please paste the URL here, then Press Enter...")
    session = HTMLSession()
    sleep(2.0)
    response: HTMLResponse = session.get(link)  # type: ignore
    logger.info(response.status_code)
    page_title: str = response.html.find("title", first=True).text  # type: ignore
    logger.info(page_title)
    if GREENHOUSE_PATTERN.search(page_title):
        return greenhouse_scrape(GREENHOUSE_TITLE, page_title, response)
    elif WORKDAY_PATTERN.search(page_title):
        return workday_scrape(link)
    else:
        pass  # will need to circle back to this one


def workday_scrape(link: str):
    random_user_agent = get_random_user_agent()
    sleep(2.0)
    payload = ""
    headers = {
        "User-Agent": random_user_agent,
        "Accept": "application/json,application/xml",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": link,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Workday-Client": "2022.32.10",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    workday_resp = request("GET", link, data=payload, headers=headers)
    all_data = loads(workday_resp.text)
    unpacked_data = loads(all_data["structuredDataAttributes"]["data"])
    init_desc = str(re.findall(r"<li>.*</li>", unpacked_data["description"]))
    cleaned_desc = JSON_CLEANING_PATTERN.sub(" ", init_desc)
    job_description = WHITESPACE_CLEANING.sub(" ", cleaned_desc).strip()
    company_dict = {
        "company_name": re.sub(r"\d", "", unpacked_data["hiringOrganization"]["name"]),
        "job_name": unpacked_data["title"],
        "job_description": job_description,
        "url": link,
        "street_address": re.sub(
            r"(\(.*\))", "", unpacked_data["jobLocation"]["address"]["addressLocality"]
        ).strip(),
    }
    return CompanyResult(**company_dict)


def greenhouse_scrape(
    pattern: re.Pattern[str], page_title: str, html_resp: HTMLResponse
) -> CompanyResult:
    matchObj = pattern.search(page_title)
    page_content = html_resp.html.xpath("//*[@id='content']", first=True).text  # type: ignore
    init_desc = str(re.findall(r"<li>.*</li>", page_content))
    cleaned_desc = JSON_CLEANING_PATTERN.sub(" ", init_desc)
    job_description = WHITESPACE_CLEANING.sub(" ", cleaned_desc).strip()
    logger.info(page_content)
    company_dict = {
        "company_name": matchObj.group("company") if matchObj else "",
        "job_name": matchObj.group("job") if matchObj else "",
        "job_description": job_description,
        "url": html_resp.url,
    }
    return CompanyResult(**company_dict)


def oracle_scrape():  # will need to circle back to this one
    pass
