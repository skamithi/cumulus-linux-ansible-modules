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


@mock.patch('dev_modules.cl_ports.os.path.exists')
@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_hash_existing_ports_conf(mock_module, mock_exists):
    """ test putting ports.conf values into a hash """
    # create ansiblemodule mock instance
    instance = mock_module.return_value
    # say that ports.conf exists
    mock_exists.return_value = True
    lf = open('tests/ports.conf')
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = lf
        cl_ports.hash_existing_ports_conf(instance)
        mock_exists.assert_called_with('/etc/cumulus/ports.conf')
        assert_equals(instance.existing_ports[1], '40G')
        assert_equals(instance.existing_ports[11], '4x10G')
