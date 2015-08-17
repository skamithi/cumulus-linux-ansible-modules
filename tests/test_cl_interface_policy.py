import mock
from nose.tools import set_trace
import library.cl_interface_policy as cl_int_policy
from asserts import assert_equals


@mock.patch('library.cl_interface_policy.unconfigure_interfaces')
@mock.patch('library.cl_interface_policy.convert_allowed_list_to_port_range')
@mock.patch('library.cl_interface_policy.read_current_int_dir')
@mock.patch('library.cl_interface_policy.AnsibleModule')
def test_module_args(mock_module,
                     mock_read_current,
                     mock_allowed_range,
                     mock_unconfigure):
    """ cl_int_policy - Test module argument specs"""
    cl_int_policy.main()
    mock_module.assert_called_with(
        argument_spec={'allowed': {'type': 'list', 'required': True},
                       'location': {'type': 'str',
                                    'default': '/etc/network/interfaces.d/'}}
    )


@mock.patch('library.cl_interface_policy.os.listdir')
@mock.patch('library.cl_interface_policy.AnsibleModule')
def test_getting_list_of_ports(mock_module, mock_read_dir):
    """ cl_int_policy - get list of current configured ports """
    mock_read_dir.return_value = ['swp1', 'swp2']
    mock_module.params = {'location': '/etc/network/interfaces.d'}
    cl_int_policy.read_current_int_dir(mock_module)
    mock_read_dir.assert_called_with('/etc/network/interfaces.d')
    assert_equals(mock_module.custom_currentportlist, ['swp1', 'swp2'])


@mock.patch('library.cl_interface_policy.AnsibleModule')
def test_breakout_portrange(mock_module):
    """ cl_int_policy - test breaking out port ranges """
    # test single port
    prange = ' swp1'
    assert_equals(cl_int_policy.breakout_portrange(prange), ['swp1'])
    # range of simple ports
    prange = 'bond0-2'
    assert_equals(cl_int_policy.breakout_portrange(prange),
                  ['bond0', 'bond1', 'bond2'])
    # 4x10g interface
    prange = 'swp10-13s0'
    assert_equals(cl_int_policy.breakout_portrange(prange),
                  ['swp10s0', 'swp11s0', 'swp12s0', 'swp13s0'])

    # word with no number at the end like lo or bridge
    prange = 'lo'
    assert_equals(cl_int_policy.breakout_portrange(prange), ['lo'])


@mock.patch('library.cl_interface_policy.AnsibleModule')
def test_convert_allowed_list_to_port_range(mock_module):
    """ cl_int_policy - test getting allow list """
    mock_module.custom_allowedportlist = []
    mock_module.params = {'allowed': ['swp1', 'swp10-11', 'bond0-2']}
    cl_int_policy.convert_allowed_list_to_port_range(mock_module)
    assert_equals(mock_module.custom_allowedportlist,
                  ['swp1', 'swp10', 'swp11', 'bond0', 'bond1', 'bond2'])


@mock.patch('library.cl_interface_policy.AnsibleModule')
def test_int_policy_enforce(mock_module):
    """ cl_int_policy test if enforcing is needed """
    # if current list is found in allowed list
    mock_module.custom_allowedportlist = ['swp1', 'swp2', 'bond0']
    mock_module.custom_currentportlist = ['swp1', 'swp2']
    assert_equals(cl_int_policy.int_policy_enforce(mock_module), False)
    # if current list is not found in allowed list
    mock_module.custom_currentportlist = ['swp1', 'swp2', 'bond1']
    assert_equals(cl_int_policy.int_policy_enforce(mock_module), True)


@mock.patch('library.cl_interface_policy.os.unlink')
@mock.patch('library.cl_interface_policy.AnsibleModule')
def test_unconfigure_interfaces(mock_module, mock_unlink):
    mock_module.custom_currentportlist = ['swp1', 'swp2', 'bond0', 'bond1']
    mock_module.custom_allowedportlist = ['swp1', 'swp2']
    cl_int_policy.unconfigure_interfaces(mock_module)
    assert_equals(mock_unlink.call_count, 2)
    assert_equals(mock_module.msg,
                  'remove config for interfaces bond0, bond1')
