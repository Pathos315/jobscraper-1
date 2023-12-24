r"Generates a cover letter"
from dataclasses import dataclass, field
from datetime import datetime

import reportlab.rl_config
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate
from src.configs import UTF, JobScrapeConfig, PersonaConfig
from src.jobspicker import JobListing
from src.striptags import strip_tags

reportlab.rl_config.warnOnMissingFontGlyphs = 0  # type: ignore


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
class CoverLetterContents:
    """Generates a cover letter."""

    listing: JobListing
    persona: PersonaConfig
    config: JobScrapeConfig

    @property
    def signature(self):
        return Image(
            filename=self.persona.signature,
            width=80,
            height=40,
            hAlign="LEFT",
        )

    @property
    def letter_title(self) -> str:
        return f"{DATE}_{self.listing.company}_{self.persona.name}.pdf"

    @property
    def subject(self) -> str:
        return f"{self.persona.name}'s Cover Letter for {self.listing.company}"

    def __call__(self) -> str | None:
        """The collection of strings and variables that make up the copy of the cover letter."""

        self.address: str = f"{self.persona.name}<br />\
            {DATE}<br /><br />\
            Dear {self.listing.title} Search Team at {self.listing.company},"

        self.introduction: str = f"I'm applying to join the {self.listing.company} team, \
                            for the {self.listing.title} opening as listed on {(self.listing.site).capitalize()}."

        self.body: str = f"I am a well-rounded and versatile candidate, able to work in most environments.\
                            I have 4+ years of experience in both graphic and user experience design. I also am proficient \
                            with coding in Python, HTML/CSS, Javascript; and I can design in Adobe Photoshop, Illustrator, InDesign,\
                            and even After Effects."

        self.outro: str = f"Thank you for considering my application. I look forward to helping contribute to\
                            {self.listing.company}'s continued success.\
                            Please contact me at {self.persona.email} at your earliest convenience.\
                            My portfolio is available for review upon request.<br />"

        self.close: str = "Warm regards,<br />"

        self.whole_letter: str = f"{self.address} {self.introduction} \
                            {self.body} \
                            {self.outro} {self.close} {self.persona.name}"


@dataclass
class CoverLetterPrinter:
    config: JobScrapeConfig
    persona: PersonaConfig
    cover_letter: CoverLetterContents

    def register_fonts(self):
        """This registers the fonts for use in the PDF, querying them from the config.json file."""
        registerFont(TTFont(FONT_NAMES[0], self.config.font_regular))
        registerFont(TTFont(FONT_NAMES[1], self.config.font_bold))
        registerFont(TTFont(FONT_NAMES[2], self.config.font_italic))
        registerFont(TTFont(FONT_NAMES[3], self.config.font_bolditalic))
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
                fontSize=10,
                leading=12,
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
            author=self.persona.name,
            creator=self.persona.name,
        )

    @property
    def export_directory(self):
        return f"{DATE}_{self.config.export_dir}"

    @property
    def coverletter_as_txt(self) -> str:
        """This creates the cover letter as a .txt file."""
        return strip_tags(self.cover_letter.whole_letter)

    def write_letter_as_txt(self):
        with open(
            f"{DATE}_{self.cover_letter.subject}_CoverLetter.txt",
            "w",
            encoding=UTF,
        ) as text_letter:
            text_letter.write(self.coverletter_as_txt)

    def format_letter(self):
        main_style = self.stylesheet[FONT_STYLE]
        return [
            Paragraph(self.cover_letter.address, style=main_style),
            Paragraph(self.cover_letter.introduction, style=main_style),
            Paragraph(self.cover_letter.body, style=main_style),
            Paragraph(self.cover_letter.outro, style=main_style),
            Paragraph(self.cover_letter.close, style=main_style),
            self.cover_letter.signature,
            Paragraph(self.persona.name, style=main_style),
        ]

    def write_cover_letter(self):
        """This creates the cover letter as .pdf using the ReportLab PDF Library."""
        self.cover_letter()
        self.register_fonts()
        self.add_styles()
        cl_flowables = self.format_letter()
        return self.formatted_letter.build(cl_flowables)
