import re

from lxml import etree

from goarch_api.client import HTTPClient
from goarch_api.models import Translation, LectionaryReading, Icon, Hymn


def remove_html_tags(raw):
    regex = re.compile('<.*?>')
    return re.sub(regex, " ", raw)


def saint_get_data(self):
    client = HTTPClient()

    resp = client.get(self.path)

    if resp is not None:
        tree = etree.fromstring(resp.encode())
        self.date = tree.find("date").text

        self.title = tree.find("title").text
        self.display_date = tree.find("displaydate").text
        self.date = tree.find("date").text

        self.icons = []

        for icon in tree.find("icons").iterchildren():
            _id = icon.get("id")
            file_path = icon.find("filepath").text
            _copyright = icon.find("copyright").text

            converted_icon = Icon(_id, file_path, _copyright)

            self.icons.append(converted_icon)

        self.lectionary = []

        for reading in tree.find("lectionary").iterchildren():
            _id = reading.find("id").text
            _type = reading.get("type")

            lectionary_reading = LectionaryReading(_id, _type)

            self.lectionary.append(lectionary_reading)

        self.readings = []

        for reading in tree.find("readings").iterchildren():
            lang = reading.get("xml:lang")
            title = reading.find("title").text
            short_title = reading.find("shorttitle").text
            body = remove_html_tags(reading.find("body").text).strip()
            _copyright = reading.find("copyright").text

            converted_translation = Translation(title=title, short_title=short_title, lang=lang,
                                                body=body, _copyright=_copyright)

            self.readings.append(converted_translation)

        self.hymns = []

        for hymn in tree.find("hymns").iterchildren():
            _type = hymn.find("type").text
            title = hymn.find("title").text
            short_title = hymn.find("shorttitle").text
            tone = hymn.find("tone").text

            translation = hymn.find("translation")
            t_lang = translation.get("xml:lang")
            t_body = translation.find("body").text
            t_copyright = translation.find("copyright").text

            converted_translation = Translation(lang=t_lang, body=t_body, _copyright=t_copyright)

            converted_hymn = Hymn(_type, title, short_title, tone, converted_translation)

            self.hymns.append(converted_hymn)


class Saint:
    def __init__(self, _id):
        self.id = _id
        self.path = f"/saints.asp?contentid={_id}"
        self.public_url = f"https://www.goarch.org/chapel/saints?contentid={_id}"

        saint_get_data(self)