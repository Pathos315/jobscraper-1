import json
from dataclasses import dataclass, field
from functools import cache


@dataclass
class CompanyResult:
    """dataclass of the company"""

    company_name: str
    job_name: str
    job_description: str
    url: str
    street_address: str = ""
    inner_id: int = 1
    suite: str = ""
    city: str = "New York"
    state: str = "NY"
    zip_code: str = "10001"
    # industries: list[str] = field(default_factory=list)
    # adjectives: list[str] = field(default_factory=list)


@dataclass
class PersonaConfig:
    """A dataclass containing information on you, the applicant."""

    name: str
    email: str
    portfolio: str
    phone: str
    signature: str


@dataclass
class JobScrapeConfig:
    """A dataclass containing information on both the job query and cover letter settings."""

    export_dir: str
    removelist: str
    url_builtin: str
    company_names: str
    total_pages: int
    per_page: int
    search_query: str
    font_regular: str
    font_bold: str
    font_italic: str
    font_bolditalic: str
    querystring: dict = field(default_factory=dict)
    persona: dict = field(default_factory=dict)


@cache
def read_config(config_file: str):
    """read_config takes the json configuration file and returns the
    configuration and information about you, the applicant.

    Args:
        config_file (str): a .json file containing the configuration information.

    Returns:
        Both the JobScrapeConfig and the PersonaConfig
    """
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        persona = data["persona"]
        return JobScrapeConfig(**data), PersonaConfig(**persona)
