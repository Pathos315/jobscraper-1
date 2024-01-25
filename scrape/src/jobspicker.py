from __future__ import annotations
from http.client import InvalidURL
import time
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import pandas as pd
from jobspy import scrape_jobs
import requests
from src.configs import DATE
from src.log import logger

OUTPUT = Path.cwd() / Path(f"{DATE}_joblistings.csv")

@dataclass
class JobListing:
    index: int
    job_url: str
    site: str
    title: str
    company: str
    company_url: str
    location: str
    job_type: Any
    date_posted: Any
    interval: Any
    min_amount: Any
    max_amount: Any
    currency: Any
    is_remote: Any
    num_urgent_words: Any
    benefits: Any
    emails: Any
    description: Any = ""
    hiring_manager: Any = "Hiring Manager"


def find_jobs() -> list[JobListing]:
    jobs = pick_jobs()
    search_queries = get_hiring_manager_queries(jobs)
    hiring_managers = hiring_manager_linkedin_search(search_queries)
    jobs = append_to_df(jobs, hiring_managers)
    jobs.to_csv(OUTPUT, index=False)
    return compile_jobs(jobs)


def pick_jobs() -> pd.DataFrame:
    try:
        logger.info("Picking jobs from csv...")
        jobs = pd.read_csv(OUTPUT)
    except FileNotFoundError:
        logger.info("No csv found, creating csv...")
        jobs: pd.DataFrame = scrape_jobs(
            results_wanted=4,
            site_name=["indeed", "linkedin"],
            search_term="User Experience Designer",
            location="New York, NY",  # only needed for indeed / glassdoor
        )
    return jobs


def get_hiring_manager_queries(jobs: pd.DataFrame) -> list[str]:
    companies: list[str] = jobs['company'].to_list()
    logger.info(companies)
    return [f"site:linkedin.com {company} \"Director of (Design | Product | Marketing | User Experience)\" @gmail.com New York" for company in companies]


def hiring_manager_linkedin_search(search_queries: set[str]) -> pd.Series:
    hiring_managers = []
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    }
    url = "https://www.google.com/search"


    for query in search_queries:
        querystring = {
            "q":f"site:linkedin.com+{query}+\"(Director+|+Head)+of++(Product+|+User+Experience)+\"+@gmail.com+New+York\""
                }
        try:
            time.sleep(2.0)
            result = requests.get(url, headers=headers, params=querystring)
            logger.info(result)
            soup = BeautifulSoup(result.text, features="html.parser")
            result = str(soup.h3.string).capitalize()
            logger.info(result)
        except (HTTPError, StopIteration, AttributeError, TypeError, InvalidURL) as error:
            logger.info(error)
            result = "Hiring Manager"
            break
        hiring_managers.append(result)
    return pd.Series(data=hiring_managers)


def append_to_df(jobs: pd.DataFrame, hiring_managers: pd.Series) -> pd.DataFrame:
    return pd.concat([jobs, hiring_managers.T], ignore_index=True)


def compile_jobs(jobs: pd.DataFrame) -> list[JobListing]:
    return [JobListing(*listing) for listing in jobs.itertuples()]