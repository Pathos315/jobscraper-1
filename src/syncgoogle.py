import time
from typing import Any, Generator
from selectolax.parser import HTMLParser
import datetime
import httpx

from urllib.parse import quote_plus, urlparse, parse_qs


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


# Helper function to format the tbs parameter.
def get_tbs(
    from_date: datetime.date,
    to_date: datetime.date,
):
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


# Request the given URL and return the response page, using the cookie jar.
def get_page(url: str) -> bytes:
    """ """
    with httpx.Client() as client:
        response = client.get(url)
        html = response.read()
    return html


# Filter links found in the Google result pages HTML code.
# Returns None if the link doesn't yield a valid result.
def filter_result(link: str):
    try:

        # Decode hidden URLs.
        if link.startswith("/url?"):
            o = urlparse(link, "http")
            link = parse_qs(o.query)["q"][0]

        # Valid results are absolute URLs not pointing to a Google domain,
        # like images.google.com or googleusercontent.com for example.
        # TODO this could be improved!
        o = urlparse(link, "http")
        if o.netloc and "google" not in o.netloc:
            return link

    # On error, return None.
    except Exception:
        pass


# Returns a generator that yields URLs.
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
    :param int stop: Last result to retrieve.
        Use None to keep searching forever.
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
        If the stop parameter is None the iterator will loop forever.
    """

    # Count the number of links yielded.
    count: int = 0

    # Prepare the search string.
    query: str = quote_plus(query)

    # If no extra_params is given, create an empty dictionary.
    # We should avoid using an empty dictionary as a default value
    # in a function parameter in Python.
    extra_params: dict[str, Any] = {} if not extra_params else extra_params

    # Check extra_params for overlapping.
    overlapping_param_check(extra_params)

    # Prepare the URL of the first request.
    if start:
        if num == 10:
            url = url_next_page % vars()
        else:
            url = url_next_page_num % vars()
    else:
        if num == 10:
            url = url_search % vars()
        else:
            url = url_search_num % vars()

    # Loop until we reach the maximum result, if any (otherwise, loop forever).
    while not stop or count < stop:
        last_count = count

        # Append extra GET parameters to the URL.
        for k, v in extra_params.items():
            k = quote_plus(k)
            v = quote_plus(v)
            url = url + ("&%s=%s" % (k, v))

        # Sleep between requests.
        # Keeps Google from banning you due to making too many requests.
        time.sleep(pause)

        # Request the Google Search results page.
        html = get_page(url)

        # Turning it into a set removes duplicates
        filtered_links = set(fetch_anchored_urls(html))

        for link in filtered_links:

            # Yield the result.
            yield link
            # Increase the results counter.
            count += 1

        # End if there are no more results.
        if last_count == count:
            break

        # Prepare the URL for the next request.
        start += num
        if num == 10:
            url = url_next_page % vars()
        else:
            url = url_next_page_num % vars()


def fetch_anchored_urls(html) -> list[str]:
    """Parse the response and get every anchored URL."""
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
    for builtin_param in url_parameters:
        if builtin_param in extra_params.keys():
            raise ValueError(
                'GET parameter "%s" is overlapping with \
                the built-in GET parameter',
                builtin_param,
            )


# Shortcut to single-item search.
# Evaluates the iterator to return the single URL as a string.
def lucky(*args, **kwargs):
    """
    Shortcut to single-item search.

    Same arguments as the main search function, but the return value changes.

    :rtype: str
    :return: URL found by Google.
    """
    try:
        name = next(search(*args, **kwargs))
    except StopIteration:
        name = "Recruiter"
    return name
