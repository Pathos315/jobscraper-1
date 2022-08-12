#TODO: replace this entire module with a regex function

from html.parser import HTMLParser
from io import StringIO


class MLStripper(HTMLParser):
    """MLStripper a class to strip a BeautifulSoup object of its html tags

    Args:
        HTMLParser (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html) -> str:
    s = MLStripper()
    s.feed(html)
    return s.get_data()
