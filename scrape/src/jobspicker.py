from __future__ import annotations
import dataclasses
from pathlib import Path
from typing import Any

import pandas as pd
from jobspy import scrape_jobs
from src.configs import DATE
from src.log import logger

OUTPUT = Path.cwd() / Path(f"{DATE}_joblistings.csv")


@dataclasses.dataclass
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


def pick_jobs() -> list[JobListing]:
    try:
        logger.info("Picking jobs from csv...")
        jobs = pd.read_csv(OUTPUT)
    except FileNotFoundError:
        logger.info("No csv found, creating csv...")
        jobs: pd.DataFrame = scrape_jobs(
            site_name=["indeed", "linkedin", "glassdoor"],
            search_term="User Experience Designer",
            location="New York, NY",  # only needed for indeed / glassdoor
        )
        jobs.to_csv(OUTPUT, index=False)
    return [JobListing(*listing) for listing in jobs.itertuples()]
