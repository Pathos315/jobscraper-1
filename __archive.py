def fetch_names_from_page_sources(self, link: str) -> tuple[str, str]:  # type: ignore
    """fetch_names_from_page_sources takes a page source object from BeautifulSoup
        and from it extracts a self.first and self.last name.

    Args:
        soup (BeautifulSoup): a BeautifulSoup object that contains
        the page source info to be assessed.

    Returns:
        tuple[str,str]: A tuple containing a self.first and self.last name.
    """
    self.greeting = "Dear"
    soup: BeautifulSoup = webscrape_results(link, run_beautiful_soup=True)
    soup_text: list[str] = soup.text.split(" ")
    all_text = [word for word in soup_text if word not in self.webtext]
    logger.info("HTML obtained. Searching for first name candidates...")
    first_names = [
        word for word in all_text if word.title() in self.firstnames and len(word)
    ]

    first_candid = max(first_names, key=len, default=" ")
    full_names = seek_lastname_in_html(target_list=all_text, target_name=first_candid)
    logger.info(full_names)
    best_result = [
        name_pair for name_pair in full_names if name_pair[1] not in self.brandnames
    ]
    return best_result[0]


from nltk.corpus import names

firstnames: set[str] = set(sorted(names.words(), key=len, reverse=True))
print(firstnames)


from nltk.corpus import names

test_set = ["jim", "bob", "dale"]
test_links = ["www.bobandjim.com", "www.jeff.com", "www.dalejones.com"]


def term_alternative(links: list[str], firstnames: list[str]):
    fnames = (name for name in firstnames)
    terms = (link for link in links if link.find(next(fnames)) > -1)
    yield from terms


true_names: list[str] = list(names.words())
terms = term_alternative(test_links, true_names)
print(next(terms))
print(next(terms))
print(next(terms))
print(next(terms))

def new_fetch(self,link):
        matchObj = LINK_CHECK.search(link)
        if matchObj:
            scheme, subdomain, domain, tld, partition, name_candidate = matchObj.groups()
            logger.info(f'{scheme} {subdomain} {domain} {tld} {partition} {name_candidate}')
