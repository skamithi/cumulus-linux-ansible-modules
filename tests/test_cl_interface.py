import mock
from nose.tools import set_trace
import dev_modules.cl_interface as cl_int
from asserts import assert_equals
from mock import MagicMock

@mock.patch('dev_modules.cl_interface.build_desired_iface_config')
@mock.patch('dev_modules.cl_interface.current_iface_config')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_module_args(mock_module,
                     mock_curr_config,
                     mock_desired_config):
    """ cl_interface - test module args """
    cl_int.main()
    mock_module.assert_called_with(
        required_together=[['virtual_ip', 'virtual_mac']],
        argument_spec={
            'addr_method': {
                'type': 'str',
                'choices': ['loopback', 'dhcp']},
            'name': {'required': True, 'type': 'str'},
            'mtu': {'type': 'str'},
            'alias': {'type': 'str'},
            'state': {'default': 'hasconfig',
                      'type': 'str',
                      'choices': ['noconfig', 'hasconfig']
                      },
            'ipv4': {'type': 'list'},
            'ipv6': {'type': 'list'},
            'virtual_mac': {'type': 'str'},
            'virtual_ip': {'type': 'str'},
            'vids': {'type': 'list'},
            'pvid': {'type': 'int'},
            'speed': {'type': 'str'}}
    )


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_current_iface_config(mock_module):
    """
    cl_interface - test getting current iface config
    """
    mock_module.run_command = MagicMock()
    # mock AnsibleModule.run_command
    mock_module.run_command.return_value = \
        (1, open('tests/ifquery.json').read(), None)
    cl_int.current_iface_config(mock_module)
    current_config = mock_module.custom_curr_config.get('config')
    assert_equals(current_config.get('address'), '10.152.5.10/24')

@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_build_address(mock_module):
    """
    cl_interface: - test building desired address config
    """
    mock_module.custom_desired_config = {'config': {}}
    mock_module.params = {'ipv6': ['1.1.1.1/24']}
    cl_int.build_address(mock_module)
    assert_equals(mock_module.custom_desired_config,
                  {'config': {'address': '1.1.1.1/24'}})


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_build_vids(mock_module):
    """
    cl_interface - test building desired vids config
    """
    mock_module.custom_desired_config = {'config': {}}
    mock_module.params = {'vids': ['1', '10-40']}
    cl_int.build_vids(mock_module)
    assert_equals(mock_module.custom_desired_config,
                  {'config': {'bridge-vids': '1 10-40'}})

@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_build_pvid(mock_module):
    """
    cl_interface - test building desired pvid
    """
    mock_module.custom_desired_config = {'config': {}}
    mock_module.params = {'pvid': 2}
    cl_int.build_pvid(mock_module)
    assert_equals(mock_module.custom_desired_config,
                  {'config': {'bridge-pvid': '2'}})
