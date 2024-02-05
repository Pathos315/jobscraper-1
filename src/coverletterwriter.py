r"Generates a cover letter"
from dataclasses import dataclass
from os import rename as move_file
import os
from pathlib import Path
from typing import Any
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


persona = PersonaConfig(os.environ.get(key) for key in ALL_ENVIRON_KEYS)

ALL_ATTR_NAMES = [
    "address",
    "introduction",
    "body",
    "invite",
    "outro",
    "close",
]


@dataclass
class LetterFormat:
    address: str
    date: str
    salutation: str
    introduction: str
    skills: str
    activities: str
    invite: str
    outro: str
    close: str


@dataclass
class CoverLetterContents:
    """Generates a cover letter."""

    listing: JobListing
    config: JobScrapeConfig

    @property
    def signature(self):
        return Image(
            filename=Path.cwd() / persona.signature_path,
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

    def __call__(self) -> str | None:
        """The collection of strings and variables that make up the copy of the cover letter."""

        self.address: str = (
            f"{persona.name}<br />\
            {DATE}<br /><br />\
            Dear {self.listing.hiring_manager},"
        )

        self.introduction: str = (
            f"I'm applying to join the {self.listing.company} team, \
                            for the {self.listing.title} opening <a href={self.listing.job_url} {self.link_color}> as listed on {str(self.listing.site).strip().capitalize()}</a>. \
                            I believe this role reports to you."
        )

        self.body: str = (
            f"Well-rounded, enthusiastic, and able to see the big picture; I can work through any issue {self.listing.company} faces. \
                            I have 4+ years of experience in both graphic and user experience design. \
                            I know Python, HTML/CSS, JavaScript, and I can design in Figma, Photoshop, Illustrator, AfterEffects, and InDesign. \
                            Beyond that, I'm the co-founder of the Prosocial Design Network, a 501(c)3 that looks to redesign the web to \
                            bring out the best in human nature online."
        )

        self.invite: str = (
            f"At a time that works with your schedule, would you be free for a 30 minute \
                            meeting via Zoom or phone? For your convenience, I'm including a \
                            <a href={persona.calendly} {self.link_color}>link</a> to my calendar. \
                            Feel free to select a time that works best for you."
        )

        self.outro: str = (
            f"Thanks for your consideration. I look forward to helping \
                            {str(self.listing.company).strip()}'s continued success.\
                            Feel free to contact me at <a href='mailto:{persona.email}' {self.link_color}>{persona.email}</a>, or by phone at {persona.phone}.\
                            {self.portfolio}<br />"
        )

        self.close: str = "Warm regards,<br />"

        self.whole_letter: str = (
            f"{self.address} {self.introduction} \
                            {self.body} {self.invite}\
                            {self.outro} {self.close} {persona.name}"
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
        output_directory = Path(f"scrape/exports/{DATE}_exports")
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
        registerFont(TTFont(FONT_NAMES[0], Path.cwd() / self.config.font_regular))
        registerFont(TTFont(FONT_NAMES[1], Path.cwd() / self.config.font_bold))
        registerFont(TTFont(FONT_NAMES[2], Path.cwd() / self.config.font_italic))
        registerFont(TTFont(FONT_NAMES[3], Path.cwd() / self.config.font_bolditalic))
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

    def format_letter(self) -> list[Paragraph | Image | Any]:
        """format_letter builds the cover letter.

        Returns:
            list[Paragraph | Image | Any ]: A formatted letter with signature.
        """
        main_style = self.stylesheet[FONT_STYLE]
        paragraphs: list[Paragraph | Image] = [
            getattr(self.cover_letter, attr_name) for attr_name in ALL_ATTR_NAMES
        ]
        paragraphs = [
            Paragraph(paragraph, style=main_style) for paragraph in paragraphs
        ]
        paragraphs.append(self.cover_letter.signature)
        paragraphs.append(Paragraph(persona.name, style=main_style))
        return paragraphs

    def write_cover_letter(self):
        """This creates the cover letter as .pdf using the ReportLab PDF Library."""
        self.cover_letter()
        paragraphs = self.format_letter()
        self.formatted_letter.build(paragraphs)
