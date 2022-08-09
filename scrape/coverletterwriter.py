r"Generates a cover letter"
import random
from datetime import datetime
from functools import cache

import reportlab.rl_config
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate

from scrape.configs import CompanyResult, JobScrapeConfig, PersonaConfig
from scrape.dir import change_dir
from scrape.namefetcher import BusinessCard
from scrape.striptags import strip_tags

reportlab.rl_config.warnOnMissingFontGlyphs = 0  # type: ignore


now = datetime.now()
date = now.strftime("%y%m%d")


FONT_NAMES = ["IBMPlex", "IBMPlexBd", "IBMPlexIt", "IBMPlexBI"]
FONT_STYLE = "Main"

class CoverLetterWriter:
    """Generates a cover letter."""

    def __init__(
        self,
        company: CompanyResult,
        contact: BusinessCard,
        persona: PersonaConfig,
        config: JobScrapeConfig,
    ):
        self.company = company
        self.job = company.job_name
        self.contact = contact
        self.persona = persona
        self.config = config
        self.hiring_manager = f"{self.contact.greeting} {self.contact.fullname}"
        self.pdfmetrics = pdfmetrics
        self.reference = "BuiltInNYC"
        self.letter_date = now.strftime("%B %d, %Y")
        self.letter_title = f"{date}_{self.company.company_name}_\
            {self.persona.name}_{random.randint(0,1000)}.pdf"
        self.export_dir = f"{date}_{config.export_dir}"
        self.address = ""
        self.intro = ""
        self.salut = ""
        self.strength_1 = ""
        self.strength_2 = ""
        self.strength_3 = ""
        self.outro = ""
        self.close = ""
        self.whole_letter = ""
        self.signature = Image(
            filename=self.persona.signature, width=80, height=40, hAlign="LEFT"
        )

        self.cover_letter = SimpleDocTemplate(
            self.letter_title,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
            title=self.letter_title,
            author=self.persona.name,
            creator=self.persona.name,
            subject=f"{self.persona.name}'s Cover Letter for {self.company.company_name}",
        )
        self.cl_flowables = []
        self.styles = getSampleStyleSheet()

    def write(self):
        """write _summary_"""
        self.register_fonts()
        self.add_styles()
        self.letter_construction()

        with change_dir(self.export_dir):
            with change_dir(f"{self.company.company_name}"):
                self.make_coverletter_pdf()
                self.make_coverletter_txt()

    def letter_construction(self):
        """The collection of strings and variables that make up the copy of the cover letter."""

        self.address: str = f"<b>{self.company.company_name}</b><br />\
                            {self.company.street_address}<br />\
                            {self.company.city}, {self.company.state}<br /><br />"

        self.intro: str = f"{self.persona.name}<br />\
                        {self.letter_date}<br /><br />\
                        {self.hiring_manager},"

        self.salut: str = f"I am interested in {self.company.company_name}'s \
                            open {self.job} position, which I believe reports to you.\
                            After learning \
                            about the opportunity from both {self.reference}, \
                            and the {self.company.company_name} website, \
                            I believe that I could contribute the following \
                            to {self.company.company_name}."

        self.strength_1: str = f"<b>Initiative:</b> I co-founded \
                                the Prosocial Design Network \
                                in response to a need \
                                I saw in the social media industry.\
                                People long to be \
                                meanginfully understood online, \
                                user interfaces were unable \
                                to meet that need. \
                                My ability to start new ventures \
                                mean that I would likely \
                                be a self-starter on projects \
                                while working for {self.company.company_name}."
        self.strength_2: str = f"<b>Craftsmanship:</b> I've designed \
                                over 20 playable characters for \
                                the online game, <b>deeeep.io</b>, \
                                assets that have gone on to garner \
                                over 10,000,000 views on Youtube \
                                gaming streams, while teaching dozens of kids about \
                                design and marine biology. I've also received \
                                praise from Google's Jigsaw team for \
                                my work on the Prosocial Design Network's \
                                website. For {self.company.company_name},\
                                this means that you can expect me \
                                to always deliver quality and impactful contributions."
        self.strength_3: str = f"<b>Adaptability:</b> In addition to the \
                                skills you'd expect for a \
                                {self.job} role, I can also adapt \
                                to meet most unforseen digital needs.\
                                I'm just as comfortable working \
                                in Figma as I am in Illustrator, \
                                or After Effects, or Google Sheets, \
                                or writing Python code; and\
                                that all means {self.company.company_name} \
                                would be adding a competent, well-rounded, \
                                and helpful member to their team."

        self.outro: str = f'In closing, I think the {self.job} role \
                            at {self.company.company_name} would be a great mutual fit.\
                            Please contact me at {self.persona.phone}, \
                            or {self.persona.email}, at your earliest convenience.\
                            My portfolio is available for review at \
                            <a href="https://{self.persona.portfolio}" color="blue">\
                            {self.persona.portfolio}</a>.<br />'

        self.close: str = "Thank You For Your Consideration,<br />"

        self.whole_letter: str = f"{self.address} {self.intro} {self.salut}\
            {self.strength_1} {self.strength_2} {self.strength_3} \
            {self.outro} {self.close} {self.persona.name}"

    @cache
    def register_fonts(self):
        """This registers the fonts for use in the PDF, querying them from the config.json file."""
        self.pdfmetrics.registerFont(TTFont(FONT_NAMES[0], self.config.font_regular))
        self.pdfmetrics.registerFont(TTFont(FONT_NAMES[1], self.config.font_bold))
        self.pdfmetrics.registerFont(TTFont(FONT_NAMES[2], self.config.font_italic))
        self.pdfmetrics.registerFont(TTFont(FONT_NAMES[3], self.config.font_bolditalic))
        self.pdfmetrics.registerFontFamily(
            FONT_NAMES[0],
            normal=FONT_NAMES[0],
            bold=FONT_NAMES[1],
            italic=FONT_NAMES[2],
            boldItalic=FONT_NAMES[3],
        )

    @cache
    def add_styles(self):
        """This registers the styles for use in the PDF."""
        self.styles.add(
            ParagraphStyle(
                FONT_STYLE,
                parent=self.styles["Normal"],
                fontName=FONT_NAMES[0],
                spaceBefore=16,
                fontSize=10,
                leading=12,
                firstLineIndent=0,
            )
        )

        self.styles.add(
            ParagraphStyle(
                "ListItem",
                parent=self.styles[FONT_STYLE],
                spaceBefore=8,
                firstLineIndent=16,
                bulletText="•",
            )
        )

    def make_coverletter_txt(self):
        """This creates the cover letter as a .txt file."""
        self.whole_letter = strip_tags(self.whole_letter).replace("           ", "\n")

        with open(
            f"{date}_{self.company.company_name}_CoverLetter.txt", "w", encoding="utf-8"
        ) as text_letter:
            text_letter.write(self.whole_letter)

    @cache
    def make_coverletter_pdf(self):
        """This creates the cover letter as .pdf using the ReportLab PDF Library."""
        self.cl_flowables = [
            Paragraph(self.address, style=self.styles[FONT_STYLE]),
            Paragraph(self.intro, style=self.styles[FONT_STYLE]),
            Paragraph(self.salut, style=self.styles[FONT_STYLE]),
            Paragraph(self.strength_1, style=self.styles[FONT_STYLE]),
            Paragraph(self.strength_2, style=self.styles[FONT_STYLE]),
            Paragraph(self.strength_3, style=self.styles[FONT_STYLE]),
            Paragraph(self.outro, style=self.styles[FONT_STYLE]),
            Paragraph(self.close, style=self.styles[FONT_STYLE]),
            self.signature,
            Paragraph(self.persona.name, style=self.styles[FONT_STYLE]),
        ]

        return self.cover_letter.build(self.cl_flowables)
