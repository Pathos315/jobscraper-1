# Unit tests for function `compile_jobs`:

# 1. Test when `jobs` is an empty DataFrame:
import numpy as np
import pandas as pd

from scrape.src.jobspicker import JobListing, compile_jobs


def test_compile_jobs_empty_df():
    jobs = pd.DataFrame()
    result = compile_jobs(jobs)
    assert len(result) == 0


# 2. Test when `jobs` has only one row with all fields filled:


def test_compile_jobs_one_row():
    data = {
        "index": [1],
        "job_url": ["www.example.com"],
        "site": ["Example Site"],
        "title": ["Example Job"],
        "company": ["Example Company"],
        "company_url": ["www.examplecompany.com"],
        "location": ["New York, NY"],
        "job_type": ["Full-time"],
        "date_posted": ["2022-01-01"],
        "interval": [7],
        "min_amount": [50000],
        "max_amount": [80000],
        "currency": ["USD"],
        "is_remote": [False],
        "num_urgent_words": [3],
        "benefits": ["Health insurance"],
        "emails": ["example@example.com"],
        "description": ["Lorem ipsum dolor sit amet"],
        "hiring_manager": ["John Doe"],
    }
    jobs = pd.DataFrame(data)
    result = compile_jobs(jobs)
    assert len(result) == 1
    assert isinstance(result[0], JobListing)
    assert result[0].index == 1
    assert result[0].job_url == "www.example.com"
    assert result[0].site == "Example Site"
    assert result[0].title == "Example Job"
    assert result[0].company == "Example Company"
    assert result[0].company_url == "www.examplecompany.com"
    assert result[0].location == "New York, NY"
    assert result[0].job_type == "Full-time"
    assert result[0].date_posted == "2022-01-01"
    assert result[0].interval == 7
    assert result[0].min_amount == 50000
    assert result[0].max_amount == 80000
    assert result[0].currency == "USD"
    assert result[0].is_remote == False
    assert result[0].num_urgent_words == 3
    assert result[0].benefits == "Health insurance"
    assert result[0].emails == "example@example.com"
    assert result[0].description == "Lorem ipsum dolor sit amet"
    assert result[0].hiring_manager == "John Doe"


# Test when `jobs` has multiple rows with different fields:
def test_compile_jobs_multiple_rows():
    data = {
        "index": [1, 2, 3],
        "job_url": ["www.example1.com", "www.example2.com", "www.example3.com"],
        "site": ["Example Site 1", "Example Site 2", "Example Site 3"],
        "title": ["Example Job 1", "Example Job 2", "Example Job 3"],
        "company": ["Example Company 1", "Example Company 2", "Example Company 3"],
        "company_url": [
            "www.examplecompany1.com",
            "www.examplecompany2.com",
            "www.examplecompany3.com",
        ],
        "location": ["New York, NY", "San Francisco, CA", "Chicago, IL"],
        "job_type": ["Full-time", "Part-time", "Contract"],
        "date_posted": ["2022-01-01", "2022-01-02", "2022-01-03"],
        "interval": [7, 10, 14],
        "min_amount": [50000, 60000, 70000],
        "max_amount": [80000, 90000, 100000],
        "currency": ["USD", "USD", "USD"],
        "is_remote": [False, True, False],
        "num_urgent_words": [3, 1, 5],
        "benefits": ["Health insurance", "Flexible hours", "Remote work"],
        "emails": [
            "example1@example.com",
            "example2@example.com",
            "example3@example.com",
        ],
        "description": [
            "Lorem ipsum dolor sit amet",
            "Consectetur adipiscing elit",
            "Sed do eiusmod tempor incididunt",
        ],
        "hiring_manager": ["John Doe", "Jane Smith", "Tom Johnson"],
    }
    jobs = pd.DataFrame(data)
    result = compile_jobs(jobs)
    assert len(result) == 3
    assert isinstance(result[0], JobListing)
    assert isinstance(result[1], JobListing)
    assert isinstance(result[2], JobListing)
    assert result[0].index == 1
    assert result[1].index == 2
    assert result[2].index == 3
    assert result[0].job_url == "www.example1.com"
    assert result[1].job_url == "www.example2.com"
    assert result[2].job_url == "www.example3.com"


# 4. Test when `jobs` has missing fields for some rows:


def test_compile_jobs_missing_fields():
    data = {
        "index": [1, 2, 3],
        "job_url": ["www.example1.com", "www.example2.com", "www.example3.com"],
        "site": ["Example Site 1", "Example Site 2", "Example Site 3"],
        "title": ["Example Job 1", "Example Job 2", "Example Job 3"],
        "company": [None, "Example Company 2", "Example Company 3"],
        "company_url": [None, None, "www.examplecompany3.com"],
        "location": ["New York, NY", None, "Chicago, IL"],
        "job_type": ["Full-time", None, "Contract"],
        "date_posted": ["2022-01-01", None, "2022-01-03"],
        "interval": [7, None, 14],
        "min_amount": [50000, None, 70000],
        "max_amount": [80000, None, 100000],
        "currency": ["USD", None, "USD"],
        "is_remote": [False, None, False],
        "num_urgent_words": [3, None, 5],
        "benefits": ["Health insurance", None, "Remote work"],
        "emails": ["example1@example.com", None, "example3@example.com"],
        "description": [
            "Lorem ipsum dolor sit amet",
            "Consectetur adipiscing elit",
            None,
        ],
        "hiring_manager": ["John Doe", None, "Tom Johnson"],
    }
    jobs = pd.DataFrame(data)
    result = compile_jobs(jobs)
    assert len(result) == 3
    assert isinstance(result[0], JobListing)
    assert isinstance(result[1], JobListing)
    assert isinstance(result[2], JobListing)
    assert result[0].index == 1
    assert result[1].index == 2
    assert result[2].index == 3
    assert result[0].job_url == "www.example1.com"
    assert result[1].job_url == "www.example2.com"
    assert result[2].job_url == "www.example3.com"
    # Check other fields for each JobListing object
    ...


# 5. Test when `jobs` is a DataFrame with NaN values for all rows:


def test_compile_jobs_nan_values():
    data = {
        "index": [np.nan, np.nan, np.nan],
        "job_url": [np.nan, np.nan, np.nan],
        "site": [np.nan, np.nan, np.nan],
        "title": [np.nan, np.nan, np.nan],
        "company": [np.nan, np.nan, np.nan],
        "company_url": [np.nan, np.nan, np.nan],
        "location": [np.nan, np.nan, np.nan],
        "job_type": [np.nan, np.nan, np.nan],
        "date_posted": [np.nan, np.nan, np.nan],
        "interval": [np.nan, np.nan, np.nan],
        "min_amount": [np.nan, np.nan, np.nan],
        "max_amount": [np.nan, np.nan, np.nan],
        "currency": [np.nan, np.nan, np.nan],
        "is_remote": [np.nan, np.nan, np.nan],
        "num_urgent_words": [np.nan, np.nan, np.nan],
        "benefits": [np.nan, np.nan, np.nan],
        "emails": [np.nan, np.nan, np.nan],
        "description": [np.nan, np.nan, np.nan],
        "hiring_manager": [np.nan, np.nan, np.nan],
    }
    jobs = pd.DataFrame(data)
    result = compile_jobs(jobs)
    assert len(result) == 3
    assert isinstance(result[0], JobListing)
    assert isinstance(result[1], JobListing)
    assert isinstance(result[2], JobListing)
