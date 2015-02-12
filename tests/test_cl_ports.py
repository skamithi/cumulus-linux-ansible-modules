import mock
from mock import MagicMock
from nose.tools import set_trace
import dev_modules.cl_ports as cl_ports
from asserts import assert_equals, mod_args_generator


@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_module_args(mock_module):
    """ cl_ports - Test module argument specs"""
    cl_ports.main()
    mock_module.assert_called_with(
        argument_spec={'speed_10g': {'type': 'list'},
                       'speed_40g': {'type': 'list'},
                       'speed_40g_div_4': {'type': 'list'},
                       'speed_4_by_10g': {'type': 'list'}},
        required_one_of=[['speed_40g_div_4',
                          'speed_4_by_10g',
                          'speed_10g',
                          'speed_40g']]
    )


@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_generate_new_ports_conf_hash(mock_module):
    """ test generating ports_conf hash based on user added params """
    instance = mock_module.return_value
    instance.params = {
        'speed_40g': ['swp1-2', 'swp5'],
        'speed_4_by_10g': ['swp7-8']
    }
    cl_ports.generate_new_ports_conf_hash(instance)
    assert_equals(instance.new_ports_hash, {1: '40G',
                                            2: '40G',
                                            5: '40G',
                                            7: '4x10G',
                                            8: '4x10G'})

@mock.patch('dev_modules.cl_ports.os.path.exists')
@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_hash_existing_ports_conf_doesntwork(mock_module, mock_exists):
    """ test missing ports.conf """
    instance = mock_module.return_value
    mock_exists.return_value = False
    assert_equals(cl_ports.hash_existing_ports_conf(instance), False)
    instance.fail_json.assert_called_with(
        msg='/etc/cumulus/ports.conf is missing', changed=False)


@mock.patch('dev_modules.cl_ports.os.path.exists')
@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_hash_existing_ports_conf_works(mock_module, mock_exists):
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
