from __future__ import annotations
from http.client import InvalidURL
import time
from urllib.error import HTTPError
from requests_html import HTMLSession, Element
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any
import pandas as pd
from jobspy import scrape_jobs
from googlesearch import lucky
from src.configs import DATE
from src.log import logger
from pyppeteer.errors import NetworkError

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
    description: Any
    hiring_manager: str


def find_jobs() -> list[JobListing]:
    jobs = pick_jobs()
    if 'hiring_manager' in jobs:
        logger.info("Writing letters...")
        return compile_jobs(jobs)
    logger.info("No hiring managers found. Searching for hiring managers...")
    companies: list[str] = jobs['company'].to_list()
    search_queries: list[str] = get_hiring_manager_queries(companies)
    vanity_urls: list[str] = find_vanity_urls(search_queries)
    hiring_manager_names: list[str] = [hiring_manager_linkedin_search(manager) for manager in vanity_urls]
    jobs: pd.DataFrame = jobs.assign(hiring_manager=hiring_manager_names)
    jobs.to_csv(OUTPUT, index=False)
    return compile_jobs(jobs)


def pick_jobs() -> pd.DataFrame:
    try:
        logger.info("Picking jobs from csv...")
        jobs = pd.read_csv(OUTPUT)
    except FileNotFoundError:
        logger.info("No csv found, creating csv...")
        jobs: pd.DataFrame = scrape_jobs(
            results_wanted=2,
            site_name=["indeed", "linkedin"],
            search_term="User Experience Designer",
            location="New York, NY",  # only needed for indeed / glassdoor
        )
    return jobs


def get_hiring_manager_queries(companies: list[str]) -> list[str]:
    logger.info(companies)
    return [f"site:linkedin.com/in/ {company} \"Director of (Design | Product | Marketing | User Experience)\" @gmail.com New York -posts" for company in companies]


def hiring_manager_linkedin_search(vanity_url: str):
    time.sleep(2.0)
    try:
        session = HTMLSession()
        response = session.get(vanity_url)
        response.html.render()
        hiring_manager_object: Element = response.html.xpath('/html/head/title', first=True)
        hiring_manager_text: str = str(hiring_manager_object.text)
        hiring_manager_first_two: list[str] = hiring_manager_text.split(" ")[:2]
        hiring_manager: str = hiring_manager_first_two[0] + " " + hiring_manager_first_two[1]
        hiring_manager = hiring_manager.title()
        logger.info(hiring_manager)
    except NetworkError as error:
        logger.error(error)
        hiring_manager = "Hiring Manager"
    return hiring_manager

def find_vanity_urls(search_queries) -> list[str]:
    hiring_managers = []
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    }

    for query in search_queries:
        try:
            result = lucky(query, extra_params=headers)
            logger.info(result)
        except (HTTPError, StopIteration, AttributeError, TypeError, InvalidURL) as error:
            logger.info(error)
            result = "Hiring Manager"
            break
        hiring_managers.append(result)
    return hiring_managers


def compile_jobs(jobs: pd.DataFrame) -> list[JobListing]:
    job_listings = []
    job_fields = [field.name for field in fields(JobListing)]
    for _, row in jobs.iterrows():
        # Clean up column names
        cleaned_row = {col.strip(): value for col, value in row.items()}

        # Create a dictionary of keyword arguments for JobListing
        job_kwargs: dict[str, Any] = {field: cleaned_row.get(field, None) for field in job_fields}

        # Create JobListing instance
        job_listing = JobListing(**job_kwargs)
        
        job_listings.append(job_listing)
    return job_listings
