import csv
from pathlib import Path


language_path = Path(__file__).parent.joinpath(r"List_of_ISO_639_language_codes_1.csv")
with open(language_path, "r", encoding="utf8") as f:
    country_links = csv.reader(f)
    header = next(country_links)

    languages = {}
    for row in country_links:
        languages[row[1]] = row


DEPRECATED_MAP = {
    "iw": "he"
}


UNASSIGNED = [
    "fu",
    "ma"
]


class Language:
    def __init__(self, iso_639_row):
        self.iso_639_row = iso_639_row

    @property
    def name(self):
        return self.iso_639_row[0]

    @property
    def set1(self):
        return self.iso_639_row[1]

    @property
    def set2T(self):
        return self.iso_639_row[2]

    @property
    def set2B(self):
        return self.iso_639_row[3]

    @property
    def set3(self):
        return self.iso_639_row[4]

    @property
    def iso2(self):
        return self.set1

    @property
    def iso3(self):
        return self.set2T

    @property
    def scope(self):
        return self.iso_639_row[5]

    @property
    def type(self):
        return self.iso_639_row[6]

    @property
    def endonyms(self):
        return self.iso_639_row[7].split(";")

    @property
    def other_names(self) -> list:
        return self.iso_639_row[8].split(";")

    @classmethod
    def from_locale(cls, locale):
        code = locale[:2]
        if code in UNASSIGNED:
            return None

        try:
            return cls(languages[code])
        except KeyError:
            raise