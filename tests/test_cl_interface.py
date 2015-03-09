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
            'virtual_mac': { 'type': 'str' },
            'virtual_ip': { 'type': 'str' },
            'vids': { 'type': 'list' },
            'pvid': { 'type': 'int' },
            'speed': {'type': 'str'}}
    )


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_current_iface_config(mock_module):
    mock_module.run_command = MagicMock()
    # mock AnsibleModule.run_command
    mock_module.run_command.return_value = (1, open('tests/ifquery.json').read(), None)
    cl_int.current_iface_config(mock_module)
    current_config = mock_module.custom_curr_config.get('config')
    assert_equals(current_config.get('address'), '10.152.5.10/24')




