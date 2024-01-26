from __future__ import annotations
from http.client import InvalidURL
import time
from urllib.error import HTTPError
from requests import Response
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
    """
    Find job listings, search for hiring managers, and compile job listings with hiring manager information.

    Returns:
    - List[JobListing]: A list of JobListing instances with hiring manager information.

    This function retrieves job listings using the 'pick_jobs' function. If the job listings
    already contain hiring manager information, it proceeds to compile the JobListing instances.
    Otherwise, it searches for hiring managers using the 'get_hiring_manager_queries' and
    'find_vanity_urls' functions, adds hiring manager information to the job listings DataFrame,
    and then compiles the JobListing instances.
    """
    jobs = pick_jobs()
    if "hiring_manager" in jobs:
        logger.info("Writing letters...")
        return compile_jobs(jobs)
    logger.info("No hiring managers found. Searching for hiring managers...")
    companies: list[str] = jobs["company"].to_list()
    search_queries: list[str] = get_hiring_manager_queries(companies)
    vanity_urls: list[str] = find_vanity_urls(search_queries)
    hiring_manager_names: list[str] = [
        hiring_manager_linkedin_search(manager) for manager in vanity_urls
    ]
    jobs: pd.DataFrame = jobs.assign(hiring_manager=hiring_manager_names)
    jobs.to_csv(OUTPUT, index=False)
    return compile_jobs(jobs)


def pick_jobs() -> pd.DataFrame:
    """
    Pick job listings from a CSV file or scrape new job listings if the CSV file is not found.

    Returns:
    - pd.DataFrame: A DataFrame containing job-related data, such as job postings.

    This function attempts to read job listings from a CSV file. If the file is not found,
    it creates a new CSV file by scraping job listings using the 'scrape_jobs' function.
    """

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
    """
    Generate LinkedIn search queries for finding hiring managers based on company names.

    Parameters:
    - companies (List[str]): A list of company names for which hiring managers are to be found.

    Returns:
    - List[str]: A list of LinkedIn search queries for finding hiring managers.

    This function takes a list of company names and generates LinkedIn search queries to
    find hiring managers associated with the specified roles (Director of Design, Product, Marketing,
    or User Experience) and located in New York. The queries are formatted for LinkedIn search.

    Example:
    >>> company_names = ["Tech Co.", "Data Corp"]
    >>> queries = get_hiring_manager_queries(company_names)
    >>> print(queries)
    ['site:linkedin.com/in/ Tech Co. "Director of (Design | Product | Marketing | User Experience)" @gmail.com New York -posts',
     'site:linkedin.com/in/ Data Corp "Director of (Design | Product | Marketing | User Experience)" @gmail.com New York -posts']

    """
    logger.info(companies)
    return [
        f'site:linkedin.com/in/ {company} "Director of (Design | Product | Marketing | User Experience)" @gmail.com New York -posts'
        for company in companies
    ]


def hiring_manager_linkedin_search(vanity_url: str) -> str:
    """hiring_manager_linkedin_search uses requests-html to get the title tag of the LinkedIn page,
    which should contain the hiring manager's name.

    Args:
        vanity_url (str): a vanity url string, e.g. `linkedin.com/in/john-doe`

    Returns:
        str: the formatted name of the hiring manager
    """
    time.sleep(2.0)
    try:
        session = HTMLSession()
        response = session.get(vanity_url)
        response.html.render()
        hiring_manager = format_name_candidate(response)
    except NetworkError as error:
        logger.error(error)
        hiring_manager = "Hiring Manager"
    return hiring_manager


def format_name_candidate(response) -> str:
    """
    Extract and format the name of a hiring manager from an HTML response.

    Parameters:
    - response: A response object containing HTML data.

    Returns:
    - str: The formatted name of the hiring manager extracted from the HTML response.

    This function extracts the title element from the HTML head of the response and
    retrieves the first two words from the title. The extracted words are then combined
    and formatted to title case, representing the hiring manager's name.

    Example:
    >>> html_response = HTMLResponse('<html><head><title>John Doe - LinkedIn</title></head></html>')
    >>> formatted_name = format_name_candidate(html_response)
    >>> print(formatted_name)
    'John Doe'

    """
    hiring_manager_object: Element = response.html.xpath("/html/head/title", first=True)
    hiring_manager_text: str = str(hiring_manager_object.text)
    hiring_manager_first_two_words: list[str] = hiring_manager_text.split(" ")[:2]
    hiring_manager_raw: str = (
        hiring_manager_first_two_words[0] + " " + hiring_manager_first_two_words[1]
    )
    hiring_manager = hiring_manager_raw.title()
    logger.info(hiring_manager)
    return hiring_manager


def find_vanity_urls(search_queries) -> list[str]:
    """
    Search for LinkedIn profiles based on provided search queries and return vanity URLs.

    Parameters:
    - search_queries (List[str]): A list of search queries for finding LinkedIn profiles.

    Returns:
    - List[str]: A list of vanity URLs corresponding to the LinkedIn profiles found.

    This function performs LinkedIn searches using the provided search queries and extracts
    vanity URLs from the search results. It uses the 'lucky' function from the 'googlesearch'
    module with specified headers to simulate a web browser user-agent.

    Note: The 'lucky' function is assumed to be part of the 'googlesearch' module.

    Example:
    >>> queries = ["site:linkedin.com John Doe email", "site:linkedin.com Jane Smith email"]
    >>> vanity_urls = find_vanity_urls(queries)
    >>> print(vanity_urls)
    ['https://www.linkedin.com/in/johndoe', 'https://www.linkedin.com/in/janesmith']

    """
    vanity_urls = []
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    }

    for query in search_queries:
        try:
            result = lucky(query, extra_params=headers)
            logger.info(result)
        except (
            HTTPError,
            StopIteration,
            AttributeError,
            TypeError,
            InvalidURL,
        ) as error:
            logger.info(error)
            result = "Hiring Manager"
            break
        vanity_urls.append(result)
    return vanity_urls


def compile_jobs(jobs: pd.DataFrame) -> list[JobListing]:
    """
    Convert DataFrame rows into a list of JobListing instances.

    Parameters:
    - jobs (pd.DataFrame): A DataFrame containing job-related data, such as job postings.

    Returns:
    - List[JobListing]: A list of JobListing instances created from the DataFrame rows.

    This function iterates over the rows of the provided DataFrame, cleans up column names,
    and creates JobListing instances for each row using the specified fields in the JobListing dataclass.
    The resulting list contains instances populated with data from the DataFrame.

    Note: Ensure that the JobListing dataclass is defined with the required fields matching the DataFrame columns.

    Example:
    >>> jobs_df = pd.DataFrame({'title': ['Software Engineer', 'Data Analyst'],
    ...                          'company': ['Tech Co.', 'Data Corp']})
    >>> job_listings = compile_jobs(jobs_df)
    >>> print(job_listings)
    [JobListing(title='Software Engineer', company='Tech Co.'),
     JobListing(title='Data Analyst', company='Data Corp')]

    """
    job_listings = []
    job_fields = [field.name for field in fields(JobListing)]
    for _, row in jobs.iterrows():
        # Clean up column names
        cleaned_row = {col.strip(): value for col, value in row.items()}

        # Create a dictionary of keyword arguments for JobListing
        job_kwargs: dict[str, Any] = {
            field: cleaned_row.get(field, None) for field in job_fields
        }

        # Create JobListing instance
        job_listing = JobListing(**job_kwargs)

        job_listings.append(job_listing)
    return job_listings
