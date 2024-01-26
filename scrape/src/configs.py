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
class PersonaConfig:
    """A dataclass containing information on you, the applicant."""

    name: str
    email: str
    portfolio: str
    phone: str
    signature: str
    calendly: str


@dataclass
class JobScrapeConfig:
    """A dataclass containing information on both the job query and cover letter settings."""

    export_directory: str
    font_regular: str
    font_bold: str
    font_italic: str
    font_bolditalic: str
    logging_config_file: str
    persona: dict = field(default_factory=dict)


def read_config(config_file: str | Path):
    """read_config takes the json configuration file and returns the
    configuration and information about you, the applicant.

    Args:
        config_file (str): a .json file containing the configuration information.

    Returns:
        Both the JobScrapeConfig and the PersonaConfig
    """
    with open(config_file, mode="r", encoding=UTF) as file:
        data = json.load(file)
        persona = data["persona"]
        return JobScrapeConfig(**data), PersonaConfig(**persona)

main_config = Path("scrape/src/config.json").resolve()
CONFIG, PERSONA = read_config(main_config)
