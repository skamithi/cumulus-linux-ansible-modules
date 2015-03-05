import mock
from nose.tools import set_trace
import dev_modules.cl_interface as cl_int
from asserts import assert_equals
from mock import MagicMock

@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_module_args(mock_module):
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
            'speed': {'type': 'str'}}
    )

