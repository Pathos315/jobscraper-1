"""_summary_

Returns:
        _type_: _description_
"""
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup
from nltk.corpus import names, webtext
from requests.exceptions import HTTPError, ProxyError, RequestException, Timeout
from tld import get_tld

from scrape.company_result import CompanyResult  # type: ignore
from scrape.configs import JobScrapeConfig  # type: ignore
from scrape.log import logger  # type: ignore
from scrape.urls_from_search_query import generate_urls_from_search_query
from scrape.web_scraper import webscrape_results  # type: ignore


@dataclass(order=True)
class BusinessCard:
    """_summary_"""

    greeting: str
    fname: str
    surname: str
    fullname: str
    workplace: str


class NameFetcher:
    """_summary_"""

    def __init__(
        self,
        company: CompanyResult,
        config: JobScrapeConfig,
    ):
        self.company = company
        self.config = config

        with open(config.brand_names, "r", encoding="utf-8") as brands:
            brand_names = set(brands.readlines())
            self.set_of_brandnames: set[str] = set(
                brand.strip("\n").lower() for brand in brand_names
            )

        self.set_of_firstnames: set[str] = set(names.words())
        self.set_webtext: set[str] = set(webtext.words())

        self.greeting: str = "To"
        self.first: str = "Whom It"
        self.last: str = "May Concern"

    def parse_provided_search_queries(self) -> BusinessCard:  # type: ignore
        """parse_provided_search_queries searches
        for contact information based on urls
        and source page data.

        Returns:
            BusinessCard: A dataclass containing the contact's contact information and company.
        """

        search_results = generate_urls_from_search_query(
            f'"{self.company.company_name}" \
                        {self.config.search_query}'
        )
        valid_links: list[str] = [link for link in search_results]
        logger.info("valid_links: %s", valid_links)

        for link in valid_links:
            logger.info("Getting: %s | %s", link, self.company.company_name)
            if "linkedin" in link:
                logger.info(
                    "Name prospect found via LinkedIn! Proceeding to fetch name..."
                )
                (
                    self.greeting,
                    self.first,
                    self.last,
                ) = self.fetch_names_from_url(link)

            elif (
                self.config.site_queries[1]
                or self.config.site_queries[2]
                or self.config.site_queries[3] in link
            ):
                logger.info(f"The link: {link} is reserved. Proceeding to next item.")
                continue

            else:
                for fname in self.set_of_firstnames:
                    if fname.lower() in link:
                        logger.info(
                            f"Name prospect {fname} found in URL! Proceeding to fetch name..."
                        )
                        (
                            self.greeting,
                            self.first,
                            self.last,
                        ) = self.fetch_names_from_url(link)
                    else:
                        logger.info("No vanity match found. Scraping HTML for clues...")
                        try:
                            soup: BeautifulSoup = webscrape_results(
                                link, run_beautiful_soup=True
                            )
                            if soup is None:
                                continue
                            (
                                self.greeting,
                                self.first,
                                self.last,
                            ) = self.fetch_names_from_page_sources(soup)
                        except (
                            TypeError,
                            AttributeError,
                            HTTPError,
                            ConnectionError,
                            ProxyError,
                            Timeout,
                            IndexError,
                            ValueError,
                            RequestException,
                        ) as query_error:
                            logger.error(
                                f"Scrape unsuccessful while parsing search queries. \
                                The following error was raised:\
                                {query_error}"
                            )

            return BusinessCard(
                greeting=self.greeting,
                fname=self.first,
                surname=self.last,
                fullname=f"{self.first} {self.last}",
                workplace=self.company.company_name,
            )

    def fetch_names_from_page_sources(
        self, soup: BeautifulSoup
    ) -> tuple[str, str, str]:
        """fetch_names_from_page_sources takes a page source object from BeautifulSoup
            and from it extracts a self.first and self.last name.

        Args:
            soup (BeautifulSoup): a BeautifulSoup object that contains
            the page source info to be assessed.

        Returns:
            tuple[str,str]: A tuple containing a self.first and self.last name.
        """
        soup_text: list[str] = soup.text.split(" ")
        entire_body: list[str] = [word.strip() for word in soup_text]
        name_prospects = [word for word in entire_body if word not in self.set_webtext]
        logger.info("HTML obtained. Searching for first name candidates...")
        first_names = [
            word for word in name_prospects if word.title() in self.set_of_firstnames
        ]
        if len(first_names) == 0:
            return "To Whom", "It May", "Concern"
        try:
            first = max(first_names, key=len)
            full_names = seek_lastname_in_html(
                target_list=entire_body, target_name=first
            )
            logger.info(full_names)
            for name_pair in full_names:
                logger.info(name_pair)
                if name_pair[1] in self.set_of_brandnames:
                    logger.info(
                        f"{name_pair} contains a brand name, or is otherwise invalid. \
                        We encourage further review. Proceeding to next name."
                    )
                    break
                else:
                    self.greeting, self.first, self.last = (
                        str("Dear"),
                        name_pair[0],
                        name_pair[1],
                    )
                    break
        except (ValueError, TypeError, IndexError) as pagesource_error:
            logger.error(
                "Scrape unsuccessful while looking through HTML code. \
                            The following error was raised:\
                            %s:"
                % pagesource_error
            )
        return self.greeting, self.first, self.last

    def fetch_names_from_url(self, link: str):
        """fetch_names_from_url takes a URL and,
        assuming it is a vanity sting, extracts the name accordingly.

        Args:
            link (str): A URL

        Returns:
            tuple[str,str,str]: A tuple containing a self.greeting, self.first, and self.last name.
        """
        if "/author/" in link:
            username = isolate_vanity_url(link, "/author/")
        elif "/in/" in link:
            username = isolate_vanity_url(link)
        else:
            logger.info("Examining top level domain...")
            username = get_tld(link, fail_silently=True, as_object=True).domain  # type: ignore

        counter: int = username.count("-")

        first_candidates: list[str] = [
            first_name.strip()
            for first_name in self.set_of_firstnames
            if first_name.lower() in username
        ]

        len_first_candidates: int = len(first_candidates)
        self.greeting = str("Dear")

        if counter == 0:
            candidate_strategies: dict = {
                0: len_first_candidates_is_zero(username),
                1: len_first_candidates_is_one(username, first_candidates),
            }
            first, last = candidate_strategies.get(
                len_first_candidates,
                len_first_candidates_is_greater(username, first_candidates),
            )
        elif counter == 1:

            (
                first,
                last,
            ) = username_hyphencount_is_one(username, counter)
        else:
            (
                first,
                last,
            ) = username_hyphencount_is_greaterthantwo(username, counter)

        return self.greeting, first, last


def username_hyphencount_is_one(username: str, counter: int) -> tuple[str, str]:
    """username_hyphencount_is_one _summary_

    Args:
        username (str): _description_

    Returns:
        _type_: _description_
    """
    first, last = username.split(sep="-", maxsplit=counter)
    return first, last


def username_hyphencount_is_greaterthantwo(
    username: str, counter: int
) -> tuple[str, str]:
    """username_hyphencount_is_greaterthantwo _summary_

    Args:
        username (str): _description_
    """
    first, middle, last, *_ = username.split("-", maxsplit=counter)
    if re.findall(r"\d+", last):
        last = middle
    else:
        first.join(f" {middle}")
        # if the titlecase matches, then it's a match and we can return the result
    return (
        first.title(),
        last.title(),
    )


def len_first_candidates_is_one(
    username: str, first_candidate: list[str]
) -> tuple[str, str]:
    """if only one candidate match found,
    that's the only match so it gets returned"""
    try:
        first = first_candidate[0].title()
        last = username[len(first) + 1 :].title()
    except IndexError as candidate_error:
        logger.error(candidate_error)
        first, last = "Whom It", "May Concern"
    return first, last


def len_first_candidates_is_greater(
    username: str, first_candidates: list[str]
) -> tuple[str, str]:
    """if multiple matches found, then go for the longest
    one as that's likely to be the whole name"""
    logger.info(first_candidates)
    first = max(first_candidates, key=len).title()
    logger.info(first)
    last = username[len(first) :].title()
    logger.info(last)
    return first, last


def len_first_candidates_is_zero(username: str) -> tuple[str, str]:
    """if no other matches, but a username is present,
    split that username down the middle
    as close as possible and edit it later."""
    _fname_len: int = len(username) // 2
    first, last = (
        username[:_fname_len].title(),
        username[_fname_len - 1 :].title(),
    )
    return first, last


def seek_lastname_in_html(
    target_list: list[str], target_name: str, num_grams: int = 1
) -> list[tuple[str, str]]:
    """seek_lastname_in_html

    Args:
        target_list (list): [description]
        target_name (str): [description]
        n (int, optional): [description]. Defaults to 1.

    Returns:
        list[tuple[str,str]]: Return a list of n-grams (tuples of n successive words) for this
    blob, which in this case is the self.first and self.last name.
    """
    return [
        (
            target_list[i],
            (upper_camel_case_split(str(target_list[i + num_grams])))[0],
        )
        for i, word in enumerate(target_list)
        if word is target_name
    ]


def isolate_vanity_url(link: str, separator: str = "/in/") -> str:
    """isolate_vanity_url

    Args:
        link (str): _description_

    Returns:
        str: _description_
    """
    __prefix, __sep, username = link.partition(separator)
    i = min(username.find("?"), username.find("/"))
    username: str = username[:i].strip()
    return username


def upper_camel_case_split(text: str) -> list:
    """camel_case_split splits strings if they're in CamelCase and need to be not Camel Case.

    Args:
        str (str): The target string to be split.

    Returns:
        list: A list of the words split up on account of being Camel Cased.
    """
    return re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", text)
