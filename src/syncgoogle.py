import time
from typing import Any, Generator
from selectolax.parser import HTMLParser
import datetime
import httpx

from urllib.parse import quote_plus, urlparse, parse_qs
from src.log import logger

# URL templates to make Google searches.

url_home = "https://www.google.%(tld)s/"
url_search = (
    "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&"
    "btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&"
    "cr=%(country)s"
)
url_next_page = (
    "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&"
    "start=%(start)d&tbs=%(tbs)s&safe=%(safe)s&"
    "cr=%(country)s"
)
url_search_num = (
    "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&"
    "num=%(num)d&btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&"
    "cr=%(country)s"
)
url_next_page_num = (
    "https://www.google.%(tld)s/search?hl=%(lang)s&"
    "q=%(query)s&num=%(num)d&start=%(start)d&tbs=%(tbs)s&"
    "safe=%(safe)s&cr=%(country)s"
)
url_parameters = ("hl", "q", "num", "btnG", "start", "tbs", "safe", "cr")


def get_tbs(
    from_date: datetime.date,
    to_date: datetime.date,
) -> str:
    """
    Helper function to format the tbs parameter.

    :param datetime.date from_date: Python date object.
    :param datetime.date to_date: Python date object.

    :rtype: str
    :return: Dates encoded in tbs format.
    """
    from_date = from_date.strftime("%m/%d/%Y")
    to_date = to_date.strftime("%m/%d/%Y")
    return "cdr:1,cd_min:%(from_date)s,cd_max:%(to_date)s" % vars()


def get_page(url: str) -> bytes:
    """
    Requests the given URL and return the response page.

    :param str url: The requested url.

    :rtype: bytes
    :return: The response content.
    """
    with httpx.Client() as client:
        response = client.get(url)
        html = response.read()
    return html


def parse_google_links(link: str) -> str | None:
    """
    Filter links found in the Google result pages HTML code.

    :param str link: The unparsed link.

    :rtype: str or None
    :return: The parsed link. Returns None if the link doesn't yield a valid result.
    """
    try:
        decoded_link = decode_hidden_url(link)
        if decoded_link and is_valid_result(decoded_link):
            return decoded_link
    except (ValueError, KeyError) as exception:
        logger.error("An error occurred while parsing the link: %s", exception)
    return None


def decode_hidden_url(link: str) -> str | None:
    """
    Decode hidden URLs starting with "/url?".

    :param str link: The unparsed link.

    :rtype: str or None
    :return: The decoded URL if it starts with "/url?", otherwise None.
    """
    if not link.startswith("/url?"):
        return None
    parsed_url = urlparse(link, "http")
    query_params = parse_qs(parsed_url.query)
    if not "q" in query_params:
        return None
    return query_params["q"][0]


def is_valid_result(link: str) -> bool:
    """
    Check if the link is a valid result.

    :param str link: The parsed link.

    :rtype: bool
    :return: True if the link is a valid result, False otherwise.
    """
    parsed_url = urlparse(link, "http")
    return bool(parsed_url.netloc) and bool("google" not in parsed_url.netloc)


def search(
    query,
    tld="com",
    lang="en",
    tbs="0",
    safe="off",
    num=10,
    start=0,
    stop=2,
    pause=2.0,
    country="",
    extra_params=None,
    user_agent=None,
    verify_ssl=True,
) -> Generator:
    """
    Search the given query string using Google.

    :param str query: Query string. Must NOT be url-encoded.
    :param str tld: Top level domain.
    :param str lang: Language.
    :param str tbs: Time limits (i.e "qdr:h" => last hour,
        "qdr:d" => last 24 hours, "qdr:m" => last month).
    :param str safe: Safe search.
    :param int num: Number of results per page.
    :param int start: First result to retrieve.
    :param int stop: Last result to retrieve. Use None to keep searching forever.
    :param float pause: Lapse to wait between HTTP requests.
        A lapse too long will make the search slow, but a lapse too short may
        cause Google to block your IP. Your mileage may vary!
    :param str country: Country or region to focus the search on. Similar to
        changing the TLD, but does not yield exactly the same results.
        Only Google knows why...
    :param dict extra_params: A dictionary of extra HTTP GET
        parameters, which must be URL encoded. For example if you don't want
        Google to filter similar results you can set the extra_params to
        {'filter': '0'} which will append '&filter=0' to every query.
    :param str user_agent: User agent for the HTTP requests.
        Use None for the default.
    :param bool verify_ssl: Verify the SSL certificate to prevent
        traffic interception attacks. Defaults to True.

    :rtype: generator of str
    :return: Generator (iterator) that yields found URLs.
        If the stop parameter is None, then the iterator will loop forever.
    """
    global search_params
    search_params = vars()

    count: int = 0

    # Prepare the search string.
    query: str = quote_plus(query)

    # If no extra_params is given, create an empty dictionary.
    # We should avoid using an empty dictionary as a default value
    # in a function parameter in Python.
    extra_params: dict[str, Any] = dict() if not extra_params else extra_params

    overlapping_param_check(extra_params)

    url: str = (
        proceed_to_next_page_check(num, url_next_page, url_next_page_num)
        if start
        else proceed_to_next_page_check(
            num,
            url_search,
            url_search_num,
        )
    )

    # Loop until we reach the maximum result, if any (otherwise, loop forever).
    while not stop or count < stop:
        last_count = count

        url = append_extra_get_params(extra_params, url)

        # Sleep between requests.
        # Keeps Google from banning you due to making too many requests.
        time.sleep(pause)

        # Request the Google Search results page.
        html = get_page(url)

        # Turning it into a set removes duplicates
        filtered_names = set(fetch_anchored_urls(html))

        for names in filtered_names:
            yield names
            count += 1

        # End if there are no more results.
        if last_count == count:
            break

        # Prepare the URL for the next request.
        start += num
        url = proceed_to_next_page_check(
            num,
            url_next_page,
            url_next_page_num,
        )


def append_extra_get_params(extra_params: dict[str, Any], url: str) -> str:
    """
    Appends extra GET parameters to the URL.

    :param dict extra_params: A dictionary of extra HTTP GET
        parameters, which must be URL encoded. For example if you don't want
        Google to filter similar results you can set the extra_params to
        {'filter': '0'} which will append '&filter=0' to every query.
    :param str url: A google search query URL.

    :rtype str
    :return: An amended URL with the extra HTTP GET parameters appended.
    """
    for k, v in extra_params.items():
        k = quote_plus(k)
        v = quote_plus(v)
        url = url + ("&%s=%s" % (k, v))
    return url


def proceed_to_next_page_check(
    num: int,
    template_if: str,
    template_else: str,
    __pagination_count: int = 10,
) -> str:
    """
    Check if proceeding to next page, and update URL accordingly.

    :param int num: The number of the query.
    :param str template_if: The template of the url if the condition of `num == __pagination_count` is True.
    :param str template_else: The template of the url if the condition of `num == __pagination_count` is False.
    :param int __pagination_count: The condition against which `num` is evaluated. Represents the maximum results per a Google page. Defaults to 10.
    :rtype: str
    :return: A str with the formatted url.
    """
    url_template = template_if if num == __pagination_count else template_else
    return url_template % search_params


def fetch_anchored_urls(html: bytes) -> list[str]:
    """
    Parse the response and get the name from every search result on a Google page.

    :param bytes html: The content from a Google search page.

    :rtype: list[str]
    :return: A list of names based on the usual metadata format for LinkedIn profiles.
    """
    names = []
    dom = HTMLParser(html)
    for tag in dom.tags("h3"):
        raw_name = tag.text()  # Get text from Google homepage
        name = raw_name.split(" - ")[
            0
        ]  # LinkedIn domains follow a set pattern of `<name> - <position> - <company>`; this gets the name.
        names.append(name)  # Appends name to list
    return names


def overlapping_param_check(extra_params: dict[str, str]) -> None:
    """Checks `extra_params` argument for overlapping entries."""
    for builtin_param in url_parameters:
        if builtin_param in extra_params.keys():
            raise ValueError(
                'GET parameter "%s" is overlapping with \
                the built-in GET parameter',
                builtin_param,
            )


def lucky(*args, **kwargs) -> str:
    """
    Shortcut to single-item search.

    Evaluates the iterator to return the single URL as a string.

    :rtype: str
    :return: URL found by Google.
    """
    try:
        name = next(search(*args, **kwargs))
    except StopIteration:
        name = "Recruiter"
    return name
