import json
from dataclasses import dataclass, field
from typing import Any

UTF = "utf-8"


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
    querystring: dict[str, str | int | Any] = field(default_factory=dict)
    persona: dict = field(default_factory=dict)


def read_config(config_file: str):
    """read_config takes the json configuration file and returns the
    configuration and information about you, the applicant.

    Args:
        config_file (str): a .json file containing the configuration information.

    Returns:
        Both the JobScrapeConfig and the PersonaConfig
    """
    with open(config_file, mode="r", encoding="utf-8") as file:
        data = json.load(file)
        persona = data["persona"]
        return JobScrapeConfig(**data), PersonaConfig(**persona)


CONFIG, PERSONA = read_config(
    "/Users/johnfallot/Documents/all_venvs/jobscraper/scrape/src/config.json"
)
