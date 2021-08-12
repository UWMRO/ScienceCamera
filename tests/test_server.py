import unittest
from evora.server.server import Evora, EvoraParser


# Example, does not run currently due to imports
class TestEvoraParser(unittest.TestCase):
    def setUp(self):
        self.evora = Evora()
        self.parser = EvoraParser(self.evora)

    def test_parse_temp(self):
        self.assertTrue(self.parser.parse('temp').isnumeric())

    def test_parse_temprange(self):
        self.assertTrue(self.parser.parse('tempRange').contains('-'))


if __name__ == '__main__':
    unittest.main()
