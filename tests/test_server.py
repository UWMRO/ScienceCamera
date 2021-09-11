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
        # self.assertTrue(self.parser.parse('tempRange').contains('-'))
        self.assertTrue('-' in self.parser.parse('tempRange'))
        
    @patch('evora.server.server.andor.GetTemperatureRange', return_value = [5, 10, 15])
    def test_parse_temprange_runs_andor_function(self, get_temp_range_mock):
        res = self.parser.parse('tempRange')
        
        get_temp_range_mock.assert_called_once()
        self.assertTrue('5,10,15' in res)

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
        self.assertTrue(','in self.parser.parse('getTEC'))

    def test_parse_warmup(self):
        self.assertTrue('warmup ' in self.parser.parse('warmup'))

    def test_parse_warmup(self):
        self.assertTrue('warmup ' in self.parser.parse('warmup'))

        with patch('evora.server.server.andor.SetFanMode', return_value=andor.DRV_SUCCESS):
            self.assertTrue('1' in self.parser.parse('warmup'))
                # assert_called_once_with needed?

        failureValues_SetFanMode = [
            andor.DRV_NOT_INITIALIZED,
            andor.DRV_ACQUIRING,
            andor.DRV_I2CTIMEOUT,
            andor.DRV_I2CDEVNOTFOUND,
            andor.DRV_ERROR_ACK,
            andor.DRV_P1INVALID
        ]

        for drv in failureValues_SetFanMode:
            with patch('evora.server.server.andor.SetFanMode', return_value=drv):
                self.assertTrue('0' in self.parser.parse('warmup'))
                # assert_called_once_with needed?
                

    def test_parse_status(self):
        # self.assertTrue(self.parser.parse('status').isnumeric()) 
        pass
    
    def test_parse_vertStats(self):
        self.assertTrue(self.parser.parse('vertStats') == '') # unfinished

    def test_parse_horzStats(self):
        self.assertTrue(self.parser.parse('horzStats') == '') # unfinished

    def test_parse_abort(self):
        self.assertTrue(self.parser.parse('abort') == 'abort 1') 

    def test_parse_expose(self):
        self.assertTrue('expose ' in self.parser.parse('expose')) 

    def test_parse_real(self):
        self.assertTrue(self.parser.parse('real') == 'real 1') 
        
    def test_parse_series(self):
        self.assertTrue('series 1,' in self.parser.parse('series'))

if __name__ == '__main__':
    unittest.main() 
