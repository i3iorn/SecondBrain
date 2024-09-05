import unittest
from plugins.test_file.dnb_faker import DnBFaker


class TestDnBFaker(unittest.TestCase):
    def test_duns_number(self):
        dnb_faker = DnBFaker()
        duns_number = dnb_faker.duns_number()
        self.assertIsInstance(duns_number, int)
        self.assertGreaterEqual(duns_number, 10000000)
        self.assertLessEqual(duns_number, 999999999)

    def test_language(self):
        dnb_faker = DnBFaker()
        language = dnb_faker.language()
        self.assertIsInstance(language, dict)
        self.assertIn("code", language)
        self.assertIsInstance(language["code"], str)
        self.assertIn("name", language)
        self.assertIsInstance(language["name"], str)

    def test_addressCountry(self):
        dnb_faker = DnBFaker()
        address_country = dnb_faker.addressCountry()
        self.assertIsInstance(address_country, dict)
        self.assertIn("isoAlpha2Code", address_country)
        self.assertIsInstance(address_country["isoAlpha2Code"], str)
        self.assertIn("name", address_country)
        self.assertIsInstance(address_country["name"], str)
        print(address_country)
