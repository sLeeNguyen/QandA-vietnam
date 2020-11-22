# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#     Copyright 2020 QandA-vietnam.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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
