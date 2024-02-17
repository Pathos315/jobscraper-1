r"Generates a cover letter"
from dataclasses import dataclass
from json import load as json_load
from os import rename as move_file, environ
from pathlib import Path
from dotenv import load_dotenv

import reportlab.rl_config
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate
from src.configs import (
    DATE,
    FONT_NAMES,
    FONT_STYLE,
    CONFIG,
    JobScrapeConfig,
)
from src.jobspicker import JobListing
from src.striptags import strip_tags

reportlab.rl_config.warnOnMissingFontGlyphs = 0  # type: ignore


load_dotenv(Path(CONFIG.persona_path).resolve())

CWD = Path.cwd()
LETTER_FORMAT_PATH = Path(CONFIG.letter_format_path).resolve()
EOL = "<br />"
ALL_ENVIRON_KEYS = [
    "NAME",
    "EMAIL",
    "PORTFOLIO",
    "LOCATION",
    "DESIRED_ROLE",
    "PHONE",
    "SIGNATURE_PATH",
    "CALENDLY",
]


@dataclass(slots=True, repr=False)
class PersonaConfig:
    name: str | None
    email: str | None
    portfolio: str | None
    location: str | None
    desired_role: str | None
    phone: str | None
    signature_path: str | None
    calendly: str | None


persona = PersonaConfig(**{key.lower(): environ.get(key) for key in ALL_ENVIRON_KEYS})


@dataclass
class CoverLetterContents:
    """Generates a cover letter."""

    listing: JobListing
    config: JobScrapeConfig

    @property
    def signature(self):
        return Image(
            filename=CWD / persona.signature_path,
            width=80,
            height=40,
            hAlign="LEFT",
        )

    @property
    def link_color(self) -> str:
        return "color='blue'"

    @property
    def letter_title(self) -> str:
        return f"{DATE}_{self.listing.company}_{persona.name}.pdf"

    @property
    def subject(self) -> str:
        return f"{persona.name}'s Cover Letter for {self.listing.company}"

    @property
    def portfolio(self) -> str:
        return (
            f"My portfolio is at <a href={persona.portfolio} {self.link_color}>{persona.portfolio}</a>."
            if persona.portfolio != ""
            else "My portfolio is available upon request."
        )

    def __call__(self) -> None:
        """The collection of strings and variables that make up the copy of the cover letter."""
        with open(LETTER_FORMAT_PATH) as letter_format:
            letter_template: dict[str, str] = json_load(letter_format)
        letter_as_string: str = EOL.join(
            f"{value}{EOL}" for value in letter_template.values()
        )
        self.whole_letter = letter_as_string.format(
            name=persona.name,
            date=DATE,
            recruiter=self.listing.recruiter,
            company=self.listing.company,
            job=self.listing.title,
            job_url=self.listing.job_url,
            listing_site=self.listing.site,
            calendly=persona.calendly,
            link_color=self.link_color,
            email=persona.email,
            phone=persona.phone,
            portfolio=self.portfolio,
        )


@dataclass
class CoverLetterPrinter:
    config: JobScrapeConfig
    cover_letter: CoverLetterContents

    @property
    def formatted_letter(self):
        return SimpleDocTemplate(
            self.cover_letter.letter_title,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
            title=self.cover_letter.letter_title,
            author=persona.name,
            creator=persona.name,
            description=self.cover_letter.subject,
        )

    @property
    def coverletter_as_txt(self) -> str:
        """This creates the cover letter as a .txt file."""
        stripped_letter = strip_tags(self.cover_letter.whole_letter)
        return (
            stripped_letter.replace(" " * 28, "\n")
            .replace(" " * 12, "\n\n")
            .replace(" " * 4, "\n")
        )

    def __call__(self):
        self.register_fonts()
        self.add_styles()
        output_directory = Path(f"exports/{DATE}_exports")
        output_directory.mkdir(exist_ok=True)
        letter_txt_path = (
            output_directory / f"{DATE}_{self.cover_letter.subject}_CoverLetter.txt"
        )
        self.write_cover_letter()
        move_file(
            self.cover_letter.letter_title,
            output_directory / self.cover_letter.letter_title,
        )
        with open(letter_txt_path, "w") as txt_file:
            txt_file.write(self.coverletter_as_txt)

    def register_fonts(self):
        """This registers the fonts for use in the PDF, querying them from the config.json file."""
        registerFont(TTFont(FONT_NAMES[0], CWD / self.config.font_regular))
        registerFont(TTFont(FONT_NAMES[1], CWD / self.config.font_bold))
        registerFont(TTFont(FONT_NAMES[2], CWD / self.config.font_italic))
        registerFont(TTFont(FONT_NAMES[3], CWD / self.config.font_bolditalic))
        registerFontFamily(
            FONT_NAMES[0],
            normal=FONT_NAMES[0],
            bold=FONT_NAMES[1],
            italic=FONT_NAMES[2],
            boldItalic=FONT_NAMES[3],
        )

    def add_styles(self):
        """This registers the styles for use in the PDF."""
        self.stylesheet = getSampleStyleSheet()
        self.stylesheet.add(
            ParagraphStyle(
                "Main",
                parent=self.stylesheet["Normal"],
                fontName=FONT_NAMES[0],
                spaceBefore=16,
                fontSize=12,
                leading=20,
                firstLineIndent=0,
            )
        )

        self.stylesheet.add(
            ParagraphStyle(
                "ListItem",
                parent=self.stylesheet[FONT_STYLE],
                spaceBefore=8,
                firstLineIndent=16,
                bulletText="•",
            )
        )

    def format_letter(self) -> list[Paragraph | Image]:
        """format_letter builds the cover letter.

        Returns:
            list[Paragraph | Image | Any ]: A formatted letter with signature.
        """
        main_style = self.stylesheet[FONT_STYLE]
        return [
            Paragraph(self.cover_letter.whole_letter, style=main_style),
            self.cover_letter.signature,
        ]

    def write_cover_letter(self) -> None:
        """
        This creates the cover letter as .pdf using the ReportLab PDF Library.
        """
        self.cover_letter()
        paragraphs = self.format_letter()
        self.formatted_letter.build(paragraphs)
