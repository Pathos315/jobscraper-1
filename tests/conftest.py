import pytest


@pytest.fixture()
def job_data_full():
    return {
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


@pytest.fixture()
def job_data_one_row():
    return {
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


@pytest.fixture()
def job_missing_data():
    return {
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
