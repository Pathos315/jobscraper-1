import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

UTF = "utf-8"

NOW = datetime.now()
DATE = NOW.strftime("%B %d, %Y")

FONT_NAMES = [
    "IBMPlex",
    "IBMPlexBd",
    "IBMPlexIt",
    "IBMPlexBI",
]
FONT_STYLE = "Main"


@dataclass
class JobScrapeConfig:
    """A dataclass containing information on both the job query and cover letter settings."""

    export_directory: str
    logging_file_path: str
    letter_format_path: str
    font_regular: str
    font_bold: str
    font_italic: str
    font_bolditalic: str
    google_search_query: str
    number_results_wanted: int
    persona_path: str
    linkedin_credentials_path: str
    job_boards: list[str] = field(default_factory=list)


def read_config(
    config_file: str | Path,
) -> JobScrapeConfig:
    """read_config takes the json configuration file and returns the
    configuration and information about you, the applicant.

    Args:
        config_file (str): a .json file containing the configuration information.

    Returns:
        Both the JobScrapeConfig and the PersonaConfig
    """
    with open(config_file, mode="r", encoding=UTF) as file:
        data = json.load(file)
        return JobScrapeConfig(**data)


CONFIG = read_config(Path("src/config.json").resolve())
