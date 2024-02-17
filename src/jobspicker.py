from __future__ import annotations
from os import environ
from pathlib import Path
from dotenv import load_dotenv

from dataclasses import dataclass, fields
from typing import Any
import pandas as pd
from jobspy import scrape_jobs
from src.syncgoogle import lucky
from src.configs import DATE, CONFIG
from src.log import logger


load_dotenv(Path(CONFIG.linkedin_credentials_path).resolve())
HOME_URL = "https://www.linkedin.com/"
KEY = environ.get("SESSION_KEY")
PASSWORD = environ.get("SESSION_PASSWORD")


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
    vanity_urls: str
    recruiter: str


def find_jobs(search_term: str) -> list[JobListing]:
    """
    Find job listings, search for recruiters, and compile job listings with hiring manager information.

    Returns:
    - List[JobListing]: A list of JobListing instances with hiring manager information.

    This function retrieves job listings using the 'pick_jobs' function. If the job listings
    already contain hiring manager information, it proceeds to compile the JobListing instances.
    Otherwise, it searches for recruiters using the 'get_recruiter_queries' and
    'find_vanity_urls' functions, adds hiring manager information to the job listings DataFrame,
    and then compiles the JobListing instances.
    """
    output_path: Path = (
        Path.cwd() / "joblistings" / f"{search_term}_{DATE}_joblistings.csv"
    )
    jobs = pick_jobs(search_term, output_path)
    if "recruiter" in jobs:
        logger.info("Writing letters...")
        return compile_jobs(jobs)
    logger.info("No recruiters found. Searching for recruiters...")
    companies: list[str] = jobs["company"].to_list()
    search_queries: list[str] = get_recruiter_queries(companies, search_term)
    jobs: pd.DataFrame = jobs.assign(queries_in_use=search_queries)
    recruiters_names = find_recruiters(search_queries)
    try:
        jobs: pd.DataFrame = jobs.assign(recruiter=recruiters_names)
    except ValueError as warning:
        logger.warning(f"{warning} | Recruiters will be excluded from this .csv file.")

    jobs.to_csv(output_path, index=False)
    return compile_jobs(jobs)


def pick_jobs(search_term: str, output_path: Path) -> pd.DataFrame:
    """
    Pick job listings from a CSV file or scrape new job listings if the CSV file is not found.

    Returns:
    - pd.DataFrame: A DataFrame containing job-related data, such as job postings.

    This function attempts to read job listings from a CSV file. If the file is not found,
    it creates a new CSV file by scraping job listings using the 'scrape_jobs' function.
    """
    results_cap = 5
    results_wanted = CONFIG.number_results_wanted
    if results_wanted > results_cap:
        logger.warning(
            f"Capping results count at {results_cap} to prevent 429 Error Codes."
        )
        results_wanted = results_cap
    try:
        logger.info("Picking jobs from csv...")
        jobs = pd.read_csv(output_path)
    except FileNotFoundError:
        logger.info("No csv found, creating csv...")
        jobs: pd.DataFrame = scrape_jobs(
            results_wanted=results_wanted,
            site_name=CONFIG.job_boards,
            search_term=search_term,
            location="New York, NY",  # only needed for indeed / glassdoor
        )
    return jobs


def get_recruiter_queries(companies: list[str], search_term: str) -> list[str]:
    """
    Generate LinkedIn search queries for finding recruiters based on company names.

    Parameters:
    - companies (List[str]): A list of company names for which recruiters are to be found.

    Returns:
    - List[str]: A list of LinkedIn search queries for finding recruiters.

    This function takes a list of company names and generates LinkedIn search queries to
    find recruiters associated with the specified roles (Director of Design, Product, Marketing,
    or User Experience) and located in New York. The queries are formatted for LinkedIn search.

    Example:
    >>> company_names = ["Tech Co.", "Data Corp"]
    >>> queries = get_recruiter_queries(company_names)
    >>> print(queries)
    ['site:linkedin.com/in/ Tech Co. "Director of (Design | Product | Marketing | User Experience)" @gmail.com New York -posts',
     'site:linkedin.com/in/ Data Corp "Director of (Design | Product | Marketing | User Experience)" @gmail.com New York -posts']

    """
    logger.info(companies)
    return [
        CONFIG.google_search_query.format(
            company.strip().replace(" ", "+"),
            search_term.strip(),
        )
        for company in companies
    ]


def find_recruiters(search_queries) -> list[str]:
    """
    Search for LinkedIn profiles based on provided search queries and return names

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
    names = []
    for query in search_queries:
        result = lucky(
            query,
        )
        names.append(result)

    return names


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
        cleaned_row = {str(col).strip(): value for col, value in row.items()}

        # Create a dictionary of keyword arguments for JobListing
        job_kwargs: dict[str, Any] = {
            field: cleaned_row.get(field, None) for field in job_fields
        }

        # Create JobListing instance
        job_listing = JobListing(**job_kwargs)

        job_listings.append(job_listing)
    return job_listings
