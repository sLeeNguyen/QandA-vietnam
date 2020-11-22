from io import StringIO
from html.parser import HTMLParser
from .exceptions import HTMLStripErrorException


class QAStripper(HTMLParser):
    def error(self, message):
        raise HTMLStripErrorException(message)

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


def strip_tags(html):
    """
    Strips HTML elements from a text and replaces HTML entities
    with their decoded value

    Example:
        Input:
            "<p>I&apos;m so <b>happy</b>!</p>"

        Output:
            "I'm so happy!"
    """
    s = QAStripper()
    s.feed(html)
    return s.get_data()
