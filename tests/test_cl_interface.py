import mock
from nose.tools import set_trace
import dev_modules.cl_interface as cl_int
from asserts import assert_equals
from mock import MagicMock

@mock.patch('dev_modules.cl_interface.os.path.exists')
@mock.patch('dev_modules.cl_interface.replace_config')
@mock.patch('dev_modules.cl_interface.config_changed')
@mock.patch('dev_modules.cl_interface.build_desired_iface_config')
@mock.patch('dev_modules.cl_interface.current_iface_config')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_module_args(mock_module,
                     mock_curr_config,
                     mock_desired_config,
                     mock_compare,
                     mock_replace,
                     mock_exists):
    """ cl_interface - test module args """
    mock_exists.return_value = True
    cl_int.main()
    mock_module.assert_called_with(
        required_together=[['virtual_ip', 'virtual_mac']],
        argument_spec={
            'addr_method': {
                'type': 'str',
                'choices': ['loopback', 'dhcp']},
            'name': {'required': True, 'type': 'str'},
            'mtu': {'type': 'int'},
            'alias_name': {'type': 'str'},
            'ipv4': {'type': 'list'},
            'ipv6': {'type': 'list'},
            'virtual_mac': {'type': 'str'},
            'virtual_ip': {'type': 'str'},
            'vids': {'type': 'list'},
            'pvid': {'type': 'int'},
            'location': {'type': 'str',
                               'default': '/etc/network/interfaces.d'},
            'link_speed': {'type': 'int'}}
    )

@mock.patch('dev_modules.cl_interface.os.path.exists')
@mock.patch('dev_modules.cl_interface.replace_config')
@mock.patch('dev_modules.cl_interface.config_changed')
@mock.patch('dev_modules.cl_interface.build_desired_iface_config')
@mock.patch('dev_modules.cl_interface.current_iface_config')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_main_integration_test(mock_module,
                     mock_curr_config,
                     mock_desired_config,
                     mock_compare,
                     mock_replace, mock_exists):
    """ cl_interface - basic integration test of main """
    mock_exists.return_value = True
    instance = mock_module.return_value
    # if config_changed == false. no change
    instance.params = {'name': 'swp1'}
    mock_compare.return_value = False
    cl_int.main()
    instance.exit_json.assert_called_with(
        msg='interface swp1 config not changed',
        changed=False)
    # if config_changed == true, change
    mock_compare.return_value = True
    cl_int.main()
    instance.exit_json.assert_called_with(
        msg='interface swp1 config updated',
        changed=True)

@mock.patch('dev_modules.cl_interface.os.path.exists')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_current_iface_config(mock_module, mock_exists):
    """
    cl_interface - test getting current iface config
    """
    mock_module.params = { 'name': 'swp1', 'location': '/etc/network/ansible' }
    mock_exists.return_value = True
    mock_module.run_command = MagicMock()
    # mock AnsibleModule.run_command
    mock_module.run_command.return_value = \
        (1, open('tests/ifquery.json').read(), None)
    cl_int.current_iface_config(mock_module)
    current_config = mock_module.custom_current_config.get('config')
    assert_equals(current_config.get('address'), '10.152.5.10/24')
    mock_exists.assert_called_with('/etc/network/ansible/swp1')

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


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_build_speed(mock_module):
    """
    cl_interface - test building speed config
    """
    mock_module.custom_desired_config = {'config': {}}
    mock_module.params = {'link_speed': 1000}
    cl_int.build_speed(mock_module)
    assert_equals(mock_module.custom_desired_config,
                  {'config': {
                      'link-speed': '1000',
                      'link-duplex': 'full'}})

@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_build_generic_attr(mock_module):
    """
    cl_interface - adding values from module parameters that match
    the ones provided by ifupdown2 json output.
    """
    mock_module.custom_desired_config = {'config': {}}
    mock_module.params = {'mtu': '1000'}
    cl_int.build_generic_attr(mock_module, 'mtu')
    assert_equals(mock_module.custom_desired_config,
                  {'config': {
                      'mtu': '1000'}})

@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_dict_changed(mock_module):
    mock_module.custom_desired_config = {'config': { 'address': '10.1.1.1/24'}}
    mock_module.custom_current_config = {}
    assert_equals(cl_int.config_dict_changed(mock_module), True)

@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_changed(mock_module):
    """
    cl_interface - test config change
    """
    # no change
    mock_module.custom_desired_config = {
        'name': 'swp1',
        'addr_method': None,
        'config':
        {'address': '10.1.1.1/24',
         'mtu': '9000'}
    }
    mock_module.custom_current_config = {
        'name': 'swp1',
        'addr_method': None,
        'config':
        {'address': '10.1.1.1/24',
         'mtu': '9000'}
    }
    assert_equals(cl_int.config_changed(mock_module), False)
    # change
    mock_module.custom_desired_config = {
        'name': 'swp1',
        'addr_method': None,
        'config':
        {'address': '10.1.1.2/24',
         'mtu': '9000'}
    }
    mock_module.custom_current_config = {
        'name': 'swp1',
        'addr_method': None,
        'config':
        {'address': '10.1.1.1/24',
         'mtu': '9000'}
    }
    assert_equals(cl_int.config_changed(mock_module), True)
    # config hash has no changed, but  addr_method has changed
    mock_module.custom_desired_config = {
        'name': 'swp1',
        'addr_method': 'dhcp',
        'config':
        {'mtu': '9000'}
    }
    mock_module.custom_current_config = {
        'name': 'swp1',
        'addr_method': None,
        'config':
        {'mtu': '9000'}
    }
    assert_equals(cl_int.config_changed(mock_module), True)

