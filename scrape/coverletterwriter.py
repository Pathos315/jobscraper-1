r"Generates a cover letter"
import random
from datetime import datetime

import reportlab.rl_config
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate

from scrape.company_result import CompanyResult
from scrape.configs import JobScrapeConfig, PersonaConfig
from scrape.dir import change_dir
from scrape.log import logger
from scrape.namefetcher import BusinessCard
from scrape.striptags import strip_tags

reportlab.rl_config.warnOnMissingFontGlyphs = 0  # type: ignore


now = datetime.now()
date = now.strftime("%y%m%d")


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
            {self.persona.name}_{random.randint(0,100)}.pdf"
        self.export_dir = f"{date}_{config.export_dir}"

        self.industry_type: str = f"{self.company.industries[0].lower()} industry"
        self.len_company_adjectives: int = len(self.company.adjectives)
        self.address = ""
        self.intro = ""
        self.salut = ""
        self.body = ""
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

    def create_heresay(self) -> str:
        """ingratiate _summary_

        Returns:
            str: _description_
        """

        logger.info("Spilling the tea on the company...")

        grapevine: dict[int, str] = {
            0: self.heresay_none(),
            1: self.heresay_len_one(),
            2: self.heresay_len_two(),
        }

        heresay: str = grapevine.get(
            self.len_company_adjectives, self.heresay_len_large()
        )
        return heresay

    def heresay_none(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return f"I've heard great things about {self.company.company_name}'s \
            impact on the {self.industry_type}."

    def heresay_len_one(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:
            return f"I've heard great things about \
                {self.company.company_name}'s impact on the {self.industry_type}, \
                along with its reputation for being {self.company.adjectives[0].lower()}."
        except IndexError as index:
            logger.error(index)
            return self.heresay_none()

    def heresay_len_two(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:
            return f"I've heard great things about {self.company.company_name}'s \
                impact on the {self.industry_type}, along with its reputation \
                for being {self.company.adjectives[0].lower()} and \
                {self.company.adjectives[1].lower()}."
        except IndexError as index:
            logger.error(index)
            return self.heresay_none()

    def heresay_len_large(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:
            return f"I've heard great things about {self.company.company_name}'s \
                impact on the {self.industry_type}, along with its reputation for being\
                {self.company.adjectives[1].lower()}, {self.company.adjectives[2].lower()},\
                and {self.company.adjectives[0].lower()}."
        except IndexError as index:
            logger.error(index)
            return self.heresay_none()

    def letter_construction(self):
        """The collection of strings and variables that make up the copy of the cover letter."""
        excitement_noun: str = random.choice(self.config.excitement_words)
        heresay = self.create_heresay()

        self.address: str = f"<b>{self.company.company_name}</b><br />\
                            {self.company.street_address}<br />\
                            {self.company.city}, {self.company.state}<br /><br />"

        self.intro: str = f"{self.persona.name}<br />\
                        {self.letter_date}<br /><br />\
                        {self.hiring_manager},"

        self.salut: str = f"As a {self.persona.role}, I enjoy seeing how \
            people can come together to generate design solutions.\
            {heresay}\
            That's why I'm writing to express my interest in the \
            <b>{self.job}</b> role at <b>{self.company.company_name}</b>\
            where I believe that my {self.persona.values} will be a \
            major value contribution to the design team \
            at {self.company.company_name}.<br />"

        proficiencies: str = f"I am proficient in \
            {(self.persona.tools[random.randint(0,1)]).title()}, \
            {(self.persona.tools[random.randint(1,2)]).title()}, \
            and {(self.persona.tools[random.randint(3,4)]).title()}"

        self.body: str = f'As requested on {self.reference}, {proficiencies}. \
            I also am a Community Advisor for the Anti-Defamation League\'s new \
            <a href="https://socialpatterns.adl.org/about/" color="blue">Social Patterns Library</a>\
            and I\'m the co-founder of the <a href="https://www.prosocialdesign.org/" color="blue">Prosocial Design Network</a>,\
            a 501(c)3 that explores how digital media \
            might bring out the best in human nature through behavioral science.'

        self.outro: str = f'I\'d be {excitement_noun} to have the opportunity to\
            further discuss the position and your needs for the role.\
            My phone number is {self.persona.phone_number}, and my email is {self.persona.email}.\
            My portfolio may be found at <a href="https://{self.persona.portfolio}" \
            color="blue">{self.persona.portfolio}</a>.<br />'

        self.close: str = "Thank You For Your Consideration,<br />"

        self.whole_letter: str = f"{self.address} {self.intro} \
            {self.salut} {self.body} {self.outro} \
            {self.close} {self.persona.name}"

    def register_fonts(self):
        """This registers the fonts for use in the PDF, querying them from the config.json file."""
        self.pdfmetrics.registerFont(TTFont("IBMPlex", self.config.font_regular))
        self.pdfmetrics.registerFont(TTFont("IBMPlexBd", self.config.font_bold))
        self.pdfmetrics.registerFont(TTFont("IBMPlexIt", self.config.font_italic))
        self.pdfmetrics.registerFont(TTFont("IBMPlexBI", self.config.font_bolditalic))
        self.pdfmetrics.registerFontFamily(
            "IBMPlex",
            normal="IBMPlex",
            bold="IBMPlexBd",
            italic="IBMPlexIT",
            boldItalic="IBMPlexBI",
        )

    def add_styles(self):
        """This registers the styles for use in the PDF."""
        self.styles.add(
            ParagraphStyle(
                "Main",
                parent=self.styles["Normal"],
                fontName="IBMPlex",
                spaceBefore=16,
                fontSize=12,
                leading=16,
                firstLineIndent=0,
            )
        )

        self.styles.add(
            ParagraphStyle("MainBody", parent=self.styles["Main"], firstLineIndent=16)
        )

        self.styles.add(
            ParagraphStyle(
                "ListItem",
                parent=self.styles["Main"],
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

    def make_coverletter_pdf(self):
        """This creates the cover letter as .pdf using the ReportLab PDF Library."""
        self.cl_flowables = [
            Paragraph(self.address, style=self.styles["Main"]),
            Paragraph(self.intro, style=self.styles["Main"]),
            Paragraph(self.salut, style=self.styles["Main"]),
            Paragraph(self.body, style=self.styles["MainBody"]),
            Paragraph(self.outro, style=self.styles["MainBody"]),
            Paragraph(self.close, style=self.styles["Main"]),
            self.signature,
            Paragraph(self.persona.name, style=self.styles["Main"]),
        ]

        return self.cover_letter.build(self.cl_flowables)
