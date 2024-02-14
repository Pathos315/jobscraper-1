from html.parser import HTMLParser
from io import StringIO
from typing import Any


class MLStripper(HTMLParser):
    """MLStripper a class to strip a BeautifulSoup object of its html tags

    Args:
        HTMLParser: finds tags and other markup and calls handler functions.
    """

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d: Any) -> None:
        self.text.write(d)

    def get_data(self) -> str:
        return self.text.getvalue()


def strip_tags(html: str) -> str:
    """strip_tags removes tags from the entered HTML string object.

    Arguments:
        html(str): html text to strip tags from.

    Returns str: a string without HTML tags.
    """
    s = MLStripper()
    s.feed(html)
    return s.get_data()
