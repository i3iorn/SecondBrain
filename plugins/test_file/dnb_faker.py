from faker import Faker
from faker.providers import BaseProvider
from plugins.test_file.lang_translate import Language
import pycountry


class DnBProvider(BaseProvider):
    def duns_number(self):
        return self.random_int(min=10000000, max=999999999)

    def addressCountry(self):
        return {
            "isoAlpha2Code": self._locales[0],
            "name": pycountry.countries.get(alpha_2=self._locales[0]).name
        }

    def language(self):
        """
        Generates a json object with a language code and name
        """
        lang = Language.from_locale(self.generator.locale)
        return {
            "code": lang.iso2,
            "name": lang.name,
        }

    def dunsControlStatus(self):
        return {
            "isOutOfBusiness": self.random_element([True, False]),
        }


class DnBFaker(Faker):
    def __init__(self, locale="en_US"):
        super().__init__(locale)
        self.add_provider(DnBProvider)
