import mock
from mock import MagicMock
from nose.tools import set_trace
import dev_modules.cl_ports as cl_ports
from asserts import assert_equals, mod_args_generator
from datetime import date, datetime


@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_module_args(mock_module):
    """ cl_ports - Test module argument specs"""
    cl_ports.main()
    mock_module.assert_called_with(
        argument_spec={'speed_10g': {'type': 'list'},
                       'speed_40g': {'type': 'list'},
                       'speed_40g_div_4': {'type': 'list'},
                       'speed_4_by_10g': {'type': 'list'}})




