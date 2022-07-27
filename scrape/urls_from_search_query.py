from googlesearch import search


def generate_urls_from_search_query(querystring: str):
    """generate_urls_from_search_query searches google
    for urls matching its provided search query.

    Returns:
        A Generator that yields URL paths to be assessed or requested.
    """
    return search(
        query=querystring,
        start=0,
        stop=3,
        pause=4,
        country="US",
        verify_ssl=False,
    )
