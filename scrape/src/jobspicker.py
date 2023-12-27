import dataclasses
from typing import Any

import pandas as pd
from jobspy import scrape_jobs
from src.configs import DATE


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
    jobs: pd.DataFrame = scrape_jobs(
        site_name=["indeed", "linkedin", "glassdoor"],
        search_term="User Experience Designer",
        location="New York, NY",  # only needed for indeed / glassdoor
    )
    jobs.to_csv(f"{DATE}_joblistings.csv")
    return [JobListing(*listing) for listing in jobs.itertuples()]
