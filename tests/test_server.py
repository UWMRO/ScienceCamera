import unittest
from evora.server.server import Evora, EvoraParser
import evora.server.dummy as andor
from mock import patch

# Example, does not run currently due to imports
class TestEvoraParser(unittest.TestCase):
    def setUp(self):
        self.evora = Evora()
        self.parser = EvoraParser(self.evora)

    def test_parse_temp(self):
        self.assertTrue(self.parser.parse('temp').isnumeric())

    def test_parse_temprange(self):
        self.assertTrue(self.parser.parse('tempRange').contains('-'))
        
    @patch('evora.server.server.andor.GetTemperatureRange', return_value = [5, 10, 15])
    def test_parse_temprange_runs_andor_function(self, get_temp_range_mock):
        res = self.parser.parse('tempRange')
        
        get_temp_range_mock.assert_called_once()
        self.assertTrue(res.contains('5,10,15'))

    def test_parse_shutdown(self):
        self.assertTrue(self.parser.parse('shutdown') == 'shutdown 1')
                
    def test_parse_timings(self):
        self.assertTrue(self.parser.parse('timings') == 'timings')

    def test_parse_setTEC_returns_string_with_input_set_point(self):
        set_point = 32
        split_parse = self.parser.parse('setTEC ' + str(set_point)).split(' ')

        self.assertTrue(split_parse[0] == 'setTEC')
        self.assertTrue(int(split_parse[1]) == set_point)

    @patch('evora.server.server.andor.GetTemperatureF', return_value=[andor.DRV_TEMPERATURE_OFF, 32])
    @patch('evora.server.server.andor.SetTemperature')
    @patch('evora.server.server.andor.CoolerON')
    def test_parse_setTEC_turns_cooler_on_if_it_was_off(self, cooler_on_mock, set_temperature_mock, _):
        set_point = 72
        self.parser.parse('setTEC ' + str(set_point))

        cooler_on_mock.assert_called_once()
        set_temperature_mock.assert_called_once_with(set_point)

    @patch('evora.server.server.andor.GetTemperatureF', return_value=[andor.DRV_TEMPERATURE_STABILIZED, 32])
    @patch('evora.server.server.andor.SetTemperature')
    @patch('evora.server.server.andor.CoolerON')
    def test_parse_setTEC_only_sets_temperature_when_drv_temperature_not_off(self, cooler_on_mock, set_temperature_mock, _):
        set_point = 55
        self.parser.parse('setTEC ' + str(set_point))

        cooler_on_mock.not_called()
        set_temperature_mock.assert_called_once_with(set_point)

    def test_parse_getTEC(self):
        self.assertTrue(self.parser.parse('getTEC').contains(','))

    def test_parse_warmup(self):
        self.assertTrue(self.parser.parse('warmup').contains('warmup '))

    def test_parse_status(self):
        self.assertTrue(self.parser.parse('status').isnumeric()) 
    
    def test_parse_vertStats(self):
        self.assertTrue(self.parser.parse('vertStats') == '') # unfinished

    def test_parse_horzStats(self):
        self.assertTrue(self.parser.parse('horzStats') == '') # unfinished

    def test_parse_abort(self):
        self.assertTrue(self.parser.parse('abort') == 'abort 1') 

    def test_parse_expose(self):
        self.assertTrue(self.parser.parse('expose').contains("expose ")) 

    def test_parse_real(self):
        self.assertTrue(self.parser.parse('real') == 'real 1') 
        
    def test_parse_series(self):
        self.assertTrue(self.parser.parse('series').contains('series 1,'))

if __name__ == '__main__':
    unittest.main() 
