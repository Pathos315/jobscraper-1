"""_summary_

Returns:
        _type_: _description_
"""
import re
from dataclasses import dataclass
from typing import Generator

from googlesearch import get_random_user_agent, search
from nltk.corpus import LazyCorpusLoader, names
from tld import get_tld

from scrape.configs import CompanyResult, JobScrapeConfig
from scrape.log import logger

DEFAULT_ADDRESSEE = "To", "Whom It", "May Concern"
SEP_CHECK = re.compile(r"/+.{2,6}/")
LINK_CHECK = re.compile(r"(http(?:s?))://([a-z]{2,6}).([a-z]*?).([a-z]+)/(.*?)/(\b[a-z-]*)")
UTF = "utf-8"


@dataclass(order=True)
class BusinessCard:
    """A dataclass containing the structured greeting and workplace of the intended contact.
    This is what gets returned at the end of this module."""

    greeting: str
    fname: str
    surname: str
    fullname: str
    workplace: str


class NameFetcher:
    """The NameFetcher class takes a company name and,
    following a structured google search, uses a mix of
    conditional statements, natural language processing,
    and regex expressions, to identify the most
    likely hiring manager for that company."""

    def __init__(
        self,
        company: CompanyResult,
        config: JobScrapeConfig,
    ):
        self.company = company
        self.config = config
        self.removelist: str = self.config.removelist
        self.firstnames: list[str] = self.preprocess_corpus(names)
        self.name_pattern_generator = (
            re.compile(
                fr"^(.*)({name})(.*)$",
                flags=re.IGNORECASE,
            )
            for name in self.firstnames
        )
        self.greeting, self.first, self.last = DEFAULT_ADDRESSEE
        self.user_agent = get_random_user_agent()

    def preprocess_corpus(self, corpus: LazyCorpusLoader) -> list[str]:
        """Takes the words of an nltk corpus and returns a list of words."""
        corpus_list: list[str] = list(corpus.words())
        corpus_list: list[str] = [word.lower() for word in corpus_list if len(word) > 3]
        with open(self.removelist, "r", encoding=UTF) as names_to_omit:
            remove_list: list[str] = names_to_omit.readlines()
            ready_list: list[str] = [
                word for word in corpus_list if word not in remove_list
            ]
        return ready_list

    def generate_urls_from_search_query(self):
        """generate_urls_from_search_query searches google
        for urls matching its provided search query.

        Returns:
            A Generator that yields URL paths to be assessed or requested.
        """
        return search(
            query=f"{self.company.company_name} \
                            {self.config.search_query}",
            start=0,
            stop=1,
            pause=3,
            country="US",
            verify_ssl=False,
            user_agent=self.user_agent
        )

    def parse_provided_search_queries(self) -> BusinessCard:  # type: ignore
        """Searches for contact information based on urls
        and source page data.

        Returns:
            BusinessCard: A dataclass containing the contact's contact information and the
            company for which they work.
        """
        search_results = self.generate_urls_from_search_query() 
        for link in search_results:
            if re.search(r".*(wiza.co|twitter.com|facebook|\?|\=).*", link):
                logger.debug(
                    f"This link cannot be processed at this time: {link} | \
                    Skipping ahead to next item."
                )
                break

            logger.debug(f"Getting name at: {link} for {self.company.company_name}")
            self.fetch_names_from_url(link)

        return BusinessCard(
            greeting=self.greeting,
            fname=self.first,
            surname=self.last,
            fullname=f"{self.first} {self.last}",
            workplace=self.company.company_name,
        )

    def fetch_names_from_url(self, link: str) -> None:
        """fetch_names_from_url takes a URL and,
        assuming it is a vanity sting, extracts the name accordingly.

        Args:
            link (str): A URL

        Returns:
            tuple[str,str,str]: A tuple containing a self.greeting, self.first, and self.last name.
        """

        link = link.rstrip("/") if link.endswith("/") else link

        matchobj = re.search(r"/+.{2,5}$", link)
        logger.debug(matchobj)
        # drop the regional character path

        link = link.rstrip(matchobj.group()) if matchobj else link
        counter = link.count("-")
        username = link[link.rfind("/") :] if counter >= 4 else isolate_vanity_url(link)

        if counter >= 4:
            self.parse_subdirectory_for_names(username)

        else:
            logger.debug(
                f"Getting names from vanity string at {link} | Hyphen count is {counter}"
            )
            counter = username.count("-")

            if counter == 0:
                first_candidates = list(
                    lookup_terms(target_str=username, terms=self.firstnames)
                )
                len_first_candidates: int = len(first_candidates)

                if len_first_candidates == 0:
                    self.go_with_default()
                elif len_first_candidates == 1:
                    self.len_first_candidates_is_one(username, first_candidates)
                else:
                    self.len_first_candidates_is_greater(username, first_candidates)

            elif counter == 1:
                self.username_hyphencount_is_one(username)

            else:
                self.username_hyphencount_is_two(username)

    def username_hyphencount_is_one(self, username: str) -> None:
        """Updates the first and last name by performing a simple separation of the string
        given the one hyphen present.

        username (str): the parsed domain string which is
        most likely to contain the hiring manager's name.
        """
        first, last = username.split("-")
        self.deliver_terms(first, last)

    def username_hyphencount_is_two(self, username: str) -> None:
        """Updates the first and last name by performing a simple separation of the string,
        based on the two hyphens present. One of the hyphens gets grouped with
        either the first or last name, depending on the
        structure of either the first or last string.

        username (str): the parsed domain string which is
        most likely to contain the hiring manager's name.
        """
        logger.info(
            "Username has two hyphens. Splitting into first, middle, and last names, and parsing accordingly."
        )
        first, middle, last = username.split("-")

        if re.findall(r"\d+", last):
            last = middle
        else:
            first.join(f" {middle}")
            # if the titlecase matches, then it"s a match and we can the result
        self.deliver_terms(first, last)

    def parse_subdirectory_for_names(self, username: str) -> None:
        """Splits the username by all hyphens present.
        Compares each item with names provided by a generator.
        It isolates the longest match — assuming that the
        longest match is the first name, and then
        it gets the item that immediately follows it,
        assuming that that will be the last name.

        username (str): the parsed domain string which is
        most likely to contain the hiring manager's name.
        """
        logger.info("Fetching names from what appears to be a press release...")
        username = re.sub(r"(\d+|.html\Z)", "", username)
        username_as_list = username.split("-")
        matching_list = list(self.generate_names(username))

        try:
            first = sorted(matching_list, key=len, reverse=True)[0]
            logger.debug(first)
            j = username_as_list.index(first)
            # this function slices for the index because it is a list,
            # therefore +1 would get the next term, which is likely to be the last name.
            last = username_as_list[j + 1]
            logger.debug(last)
            self.deliver_terms(first, last)

        except (IndexError, ValueError, AttributeError) as error:
            logger.error(error)
            self.go_with_default()

    def generate_names(self, target_str: str) -> Generator[str, None, None]:
        # TO DO: Update docstring.
        """fetch_username_str_from_link _summary_
        Args:
            link (str): _description_
        Returns:
            str: _description_
        """

        for pattern in self.name_pattern_generator:
            match = pattern.search(target_str)
            if match:
                logger.debug(
                    f"Matches include:\n\
                    Priors: {match.group(1)}\n\
                    Names: {match.group(2)}\n\
                    Remainders: {match.group(3)}"
                )
                yield match.group(2)

    def len_first_candidates_is_one(
        self, username: str, first_candidate: list[str]
    ) -> None:
        # TO DO: Update docstring.
        """if only one candidate match found,
        that"s the only match so it gets returned"""
        logger.info(f"One name candidate found in {username}.")
        first = first_candidate[0]
        last = username[len(first) :]
        self.deliver_terms(first, last)

    def len_first_candidates_is_greater(
        self, username: str, first_candidates: list[str]
    ) -> None:
        # TO DO: Update docstring.
        """if multiple matches found, then go for the longest
        one as that"s likely to be the whole name"""
        logger.info(
            f"Multiple matches found, looking for best among {first_candidates}"
        )
        candidate_indices: list[int] = [
            username.find(candidate) for candidate in first_candidates
        ]
        zipped_indices: list[tuple[str, int]] = list(
            zip(first_candidates, candidate_indices)
        )
        sorted_indices: list[tuple[str, int]] = sorted(
            zipped_indices, key=lambda x: x[1]
        )
        first: str = sorted_indices[0][0]
        _, first, last = username.partition(first)
        self.deliver_terms(first, last)

    def go_with_default(self) -> None:
        """_summary_"""
        # TO DO: Update docstring.
        logger.info("No names found. Addressing letter to Whom It May Concern.")
        self.greeting, self.first, self.last = DEFAULT_ADDRESSEE

    def deliver_terms(self, first: str, last: str) -> None:
        """_summary_

        Args:
            first (str): _description_
            last (str): _description_
        """
        # TO DO: Update docstring.
        self.greeting, self.first, self.last = "Dear", first.title(), last.title()

        self.first = parse_for_slashes(self.first) if "/" in self.first else self.first
        self.last = parse_for_slashes(self.last) if "/" in self.last else self.last

        logger.debug(
            f"Addressing letter to: {self.greeting} {self.first} {self.last}..."
        )

def isolate_vanity_url(link: str) -> str:
    # TO DO: Update docstring.
    """fetch_username_str_from_link _summary_
    Args:
        link (str): _description_
    Returns:
        str: _description_
    """
    logger.debug(link)

    # split up linkedin url so that the vanity content is on the right

    matchobj = SEP_CHECK.search(link)
    logger.debug(matchobj)
    username = (
        link.partition(matchobj.group())[2]
        if matchobj
        else get_tld(link, fail_silently=True, as_object=True).domain  # type: ignore
    )  # type: ignore

    logger.debug(username)
    return username


def lookup_terms(target_str: str, terms: list[str]):
    # TO DO: Update docstring.
    """_summary_

    Args:
        target_str (str): _description_
        terms (list[str]): _description_

    Yields:
        _type_: _description_
    """
    target_str = target_str.lower()
    for term in terms:
        if target_str.find(term.lower()) != -1:
            yield term


def parse_for_slashes(term: str):
    # TO DO: Update docstring.
    """_summary_

    Args:
        term (str): _description_

    Returns:
        _type_: _description_
    """
    return sorted(term.split("/"), key=len, reverse=True)[0]
