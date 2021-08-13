import unittest
from random import seed, randint
from time import time as epochtime
from evora.server.server import Evora, EvoraParser


# Example, does not run currently due to imports
class TestEvoraParser(unittest.TestCase):
    def setUp(self):
        seed(epochtime())

        self.evora = Evora()
        self.parser = EvoraParser(self.evora)

    def test_parse_temp(self):
        self.assertTrue(self.parser.parse('temp').isnumeric())

    def test_parse_temprange(self):
        self.assertTrue(self.parser.parse('tempRange').contains('-'))

    def test_parse_shutdown(self):
        self.assertTrue(self.parser.parse('shutdown') == 'shutdown 1')

    def test_parse_timings(self):
        self.assertTrue(self.parser.parse('timings') == 'timings')

    def test_parse_setTEC(self):
        setPoint = randint(-100, -10)
        split_parse = self.parser.parse('setTEC ' + str(setPoint)).split(' ')

        self.assertTrue(split_parse[0] == 'setTEC')
        self.assertTrue(int(split_parse[1]) == setPoint)

    def test_parse_getTEC(self):
        self.assertTrue(self.parser.parse('getTEC') == '') # unfinished

    def test_parse_warmup(self):
        self.assertTrue(self.parser.parse('warmup') == '') # unfinished

    def test_parse_status(self):
        self.assertTrue(self.parser.parse('status') == '') # unfinished
    
    def test_parse_vertStats(self):
        self.assertTrue(self.parser.parse('vertStats') == '') # unfinished

    def test_parse_horzStats(self):
        self.assertTrue(self.parser.parse('horzStats') == '') # unfinished

    def test_parse_abort(self):
        self.assertTrue(self.parser.parse('abort') == '') # unfinished

    def test_parse_expose(self):
        self.assertTrue(self.parser.parse('expose') == '') # unfinished

    def test_parse_real(self):
        self.assertTrue(self.parser.parse('real') == '') # unfinished

if __name__ == '__main__':
    unittest.main() 
