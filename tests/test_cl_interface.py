from mock import call
import mock
from nose.tools import set_trace
from dev_modules.cl_interface import get_iface_type, add_ipv4, \
    add_ipv6, config_changed, modify_switch_config, main, \
    remove_config_from_etc_net_interfaces, config_swp_iface, \
    check_if_applyconfig_name_defined_only, add_bridgemems, \
    config_dhcp
from asserts import assert_equals


def mod_args_none(arg):
    values = {'bridgemems': None,
              'bondmems': None,
              'name': 'swp10'}
    return values[arg]


def mod_args_bridgemems(arg):
    values = {'bridgemems': '2.0.0'}
    return values[arg]


def mod_args_bondmems(arg):
    values = {'bondmems': 'swp56, swp57',
              'bridgemems': None}
    return values[arg]


def mod_args_mgmt(arg):
    values = {'name': 'eth1',
              'bridgemems': None,
              'bondmems': None
              }
    return values[arg]


def mod_args_lo(arg):
    values = {'name': 'lo',
              'bridgemems': None,
              'bondmems': None
              }
    return values[arg]


def mod_args_swp(arg):
    values = {'name': 'swp10',
              'bridgemems': None,
              'bondmems': None
              }
    return values[arg]


def mod_args_unknown(arg):
    values = {'name': 'gibberish',
              'bridgemems': None,
              'bondmems': None,
              'applyconfig': 'no',
              'ifaceattrs': None
              }
    return values[arg]


@mock.patch('dev_modules.cl_interface.apply_config')
@mock.patch('dev_modules.cl_interface.remove_config_from_etc_net_interfaces')
@mock.patch('dev_modules.cl_interface.modify_switch_config')
@mock.patch('dev_modules.cl_interface.config_lo_iface')
@mock.patch('dev_modules.cl_interface.config_changed')
@mock.patch('dev_modules.cl_interface.get_iface_type')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_module_args(mock_module,
                     mock_get_iface_type,
                     mock_config_changed,
                     mock_config_lo_iface,
                     mock_mod_sw_config,
                     mock_remove_config,
                     mock_apply_config):
    """ Test module argument specs"""
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_unknown
    mock_get_iface_type.return_value = 'loopback'
    main()
    mock_module.assert_called_with(
        argument_spec={'bondmems': {'type': 'list'},
                       'ipv6': {'type': 'list'},
                       'ipv4': {'type': 'list'},
                       'applyconfig': {'required': True, 'type': 'str'},
                       'name': {'required': True, 'type': 'str'},
                       'ifaceattrs': {'type': 'dict'},
                       'dhcp': {'type': 'str', 'choices': ['yes', 'no']},
                       'bridgemems': {'type': 'list'}})


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_dhcp(mock_module):
    working_output = {
        'addr_family': 'inet',
        'addr_method': 'dhcp',
        'config': {}
    }

    instance = mock_module.return_value
    # dhcp is yes in modules.params
    instance.params = {'dhcp': 'yes'}
    iface = {'config': {}}
    config_dhcp(instance, iface)
    assert_equals(iface, working_output)

    # dhcp is no in modules.params
    instance.params = {'dhcp': 'no'}
    iface = {'config': {}}
    config_dhcp(instance, iface)
    assert_equals(iface, {'config': {}})

    # dhcp in ifaceattrs set to yes
    instance.params = {'dhcp': None,
                       'ifaceattrs': {'dhcp': 'yes'}}
    iface = {'config': {}}
    config_dhcp(instance, iface)
    assert_equals(iface, working_output)

    # dhcp in ifaceattrs sett to No
    instance.params = {'dhcp': None,
                       'ifaceattrs': {'dhcp': 'no'}}
    iface = {'config': {}}
    config_dhcp(instance, iface)
    assert_equals(iface, {'config': {}})

    # dhcp options not in params or ifaceattrs
    instance.params = {}
    iface = {'config': {}}
    config_dhcp(instance, iface)
    assert_equals(iface, {'config': {}})


@mock.patch('dev_modules.cl_interface.add_ipv6')
@mock.patch('dev_modules.cl_interface.add_ipv4')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_swp_iface(mock_module, mock_ipv4, mock_ipv6):
    """
    cl_interface - test configuring swp interfaces
    """
    iface = {'name': 'lo', 'ifacetype': 'swp'}
    config_swp_iface(mock_module, iface)
    assert_equals(mock_ipv4.call_count, 1)
    assert_equals(mock_ipv6.call_count, 1)


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_get_iface_type(mock_module):
    """
    cl_interface - test getting iface type
    """
    # test for bridge
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_bridgemems
    assert_equals(get_iface_type(instance, {}), 'bridge')
    instance.params.get.called_with('bridgemems')
    # test for bond
    instance.params.get.side_effect = mod_args_bondmems
    assert_equals(get_iface_type(instance, {}), 'bond')
    instance.params.get.called_with('bondmems')
    # test for mgmt
    instance.params.get.side_effect = mod_args_mgmt
    assert_equals(get_iface_type(instance, {}), 'mgmt')
    instance.params.get_called_with('eth1')
    # test for loopback
    instance.params.get.side_effect = mod_args_lo
    assert_equals(get_iface_type(instance, {}), 'loopback')
    instance.params.get_called_with('lo')
    # test for phy
    instance.params.get.side_effect = mod_args_swp
    assert_equals(get_iface_type(instance, {}), 'swp')
    instance.params.get_called_with('swp10')
    # test if unknown
    instance.params.get.side_effect = mod_args_unknown
    get_iface_type(instance, {})
    assert_equals(instance.fail_json.call_count, 1)
    instance.fail_json.assert_called_with(
        msg='unable to determine interface type gibberish')

    # test if ifaceattr is set for bridge
    instance.params.get_side_effect = mod_args_none
    ifaceattr = {'bridgemems': ''}
    assert_equals(get_iface_type(instance, ifaceattr), 'bridge')

    # test if ifaceattr is set for bond
    instance.params.get_side_effect = mod_args_none
    ifaceattr = {'bondmems': ''}
    assert_equals(get_iface_type(instance, ifaceattr), 'bond')


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_exception_when_using_ifaceattr(mock_module):
    """
    cl_interfaces - test when using ifaceattr that only name,
    and ifaceattr is defined
    otherwise exit module with error
    """
    instance = mock_module.return_value
    instance.params = {
        'ifaceattrs': {'something': '1'},
        'name': 'sdf',
        'applyconfig': 'yes'}
    check_if_applyconfig_name_defined_only(instance)
    assert_equals(instance.fail_json.call_count, 0)

    instance.params = {
        'ifaceattrs': {'something': '1'},
        'name': 'sdf',
        'sdfdf': 'dfdf',
        'applyconfig': 'yes'}

    check_if_applyconfig_name_defined_only(instance)
    instance.fail_json.assert_called_with(
        msg='when ifaceattr is defined, only ' +
        'name and applyconfig options are allowed')


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_add_ipv4(mock_module):
    addr = '10.1.1.1/24'
    # addr is empty
    instance = mock_module.return_value
    instance.params.get.return_value = None
    iface = {'config': {}}
    add_ipv4(instance, iface)
    assert_equals('address' in iface['config'], False)
    # addr is not empty
    instance.params.get.return_value = addr
    iface = {'ifacetype': 'lo', 'config': {}}
    add_ipv4(instance, iface)
    assert_equals(iface['config']['address'], addr)


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_add_ipv6(mock_module):
    addr = '10:1:1::1/127'
    instance = mock_module.return_value

    # iface addr is None ipv6 is None
    instance.params.get.return_value = None
    iface = {'config': {}}
    add_ipv6(instance, iface)
    assert_equals('address' in iface['config'], False)

    # iface addr is None ipv6 is not None
    instance.params.get.return_value = addr
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'], addr)

    # iface addr is str ipv6 is str
    instance.params.get.return_value = addr
    iface = {'config': {'address': '10.1.1.1/24'}}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10.1.1.1/24',
                   '10:1:1::1/127'])

    # iface addr is str ipv6 is list
    instance.params.get.return_value = [addr]
    iface = {'config': {'address': '10.1.1.1/24'}}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10:1:1::1/127',
                   '10.1.1.1/24'])

    # iface addr is list ipv6 is str
    instance.params.get.return_value = addr
    iface = {'config': {'address': ['10.1.1.1/24']}}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10.1.1.1/24',
                   '10:1:1::1/127'])

    # iface addr is list ipv6 is list
    instance.params.get.return_value = [addr]
    iface = {'config': {'address': ['10.1.1.1/24']}}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10.1.1.1/24',
                   '10:1:1::1/127'])


@mock.patch('dev_modules.cl_interface.run_cl_cmd')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_changed_lo_config_different(mock_module,
                                            mock_exec):
    """
    Test config changed loopback config is different
    """
    instance = mock_module.return_value
    instance.params.get.return_value = 'lo'
    iface = {
        'ifacetype': 'loopback',
        'config': {
            'address': "10.3.3.4/32",
            'speed': '1000'
        },
        'name': 'lo'
    }
    mock_exec.return_value = ''.join(open('tests/lo.txt').readlines())
    assert_equals(config_changed(instance, iface), True)


def loop_iface():
    iface = {
        'name': 'lo',
        'ifacetype': 'loopback',
        'config': {
            'address': ["10:3:3::3/128",
                        "10.3.3.3/32"]
        }
    }
    return iface


@mock.patch('dev_modules.cl_interface.run_cl_cmd')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_changed_lo_config_same(mock_module, mock_exec):
    """ Test config change loopback config the same"""
    instance = mock_module.return_value
    instance.params.get.return_value = 'lo'
    mock_exec.return_value = ''.join(open('tests/lo.txt').readlines())
    iface = loop_iface()
    assert_equals(config_changed(instance, iface), False)
    _msg = 'no change in interface lo configuration'
    instance.exit_json.assert_called_with(
        msg=_msg, changed=False)


@mock.patch('dev_modules.cl_interface.os')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_modify_switch_config(mock_module, mock_os):
    instance = mock_module.return_value
    mock_os.path.exists.return_value = False
    testwrite = open('/tmp/test.me', 'w')
    iface = loop_iface()
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = testwrite
        modify_switch_config(instance, iface)
        mock_open.assert_called_with('/etc/network/ansible/lo', 'w')

    mock_os.path.exists.assert_called_with('/etc/network/ansible/')
    fstr = 'auto lo\n'
    fstr += 'iface lo inet loopback\n'
    fstr += '    address 10:3:3::3/128\n'
    fstr += '    address 10.3.3.3/32\n'
    output = open('/tmp/test.me').readlines()
    assert_equals(''.join(output), fstr)


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_remove_config_from_etc_net_interfaces(mock_module):
    instance = mock_module.return_value
    origfile = open('tests/interface.txt', 'r')
    newfile = open('tests/output.txt', 'w')
    mock_open = mock.Mock(side_effect=[origfile, newfile])
    iface = {'name': 'swp2'}
    with mock.patch('__builtin__.open', mock_open):
        remove_config_from_etc_net_interfaces(instance, iface)
    expected = [call('/etc/network/interfaces', 'r'),
                call('/etc/network/interfaces', 'w')]
    assert_equals(mock_open.call_args_list, expected)
    f = open('tests/output.txt')
    output = f.readlines()
    assert_equals(output,
                  ['auto lo\n', 'iface lo inet loopback\n',
                   '  address 1.1.1.1/32\n',
                   '\n',
                   'auto eth0\n',
                   'iface eth0 inet dhcp\n',
                   '\n',
                   'auto swp1\n',
                   'iface swp1\n',
                   '   speed 1000\n',
                   '\n',
                   '## Ansible controlled interfaces found here\n',
                   'source /etc/network/ansible/*\n'])


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_appending_ansible_to_etc_network_interface(mock_module):
    instance = mock_module.return_value
    origfile = open('tests/interface_with_ansible.txt', 'r')
    newfile = open('tests/output.txt', 'w')
    mock_open = mock.Mock(side_effect=[origfile, newfile])
    iface = {'name': 'swp2'}
    with mock.patch('__builtin__.open', mock_open):
        remove_config_from_etc_net_interfaces(instance, iface)
    expected = [call('/etc/network/interfaces', 'r'),
                call('/etc/network/interfaces', 'w')]
    assert_equals(mock_open.call_args_list, expected)
    f = open('tests/output.txt')
    output = f.readlines()
    assert_equals(output,
                  ['auto lo\n', 'iface lo inet loopback\n',
                   '  address 1.1.1.1/32\n',
                   '\n',
                   'auto eth0\n',
                   'iface eth0 inet dhcp\n',
                   '\n',
                   'auto swp1\n',
                   'iface swp1\n',
                   '   speed 1000\n',
                   '\n',
                   '## Ansible controlled interfaces found here\n',
                   'source /etc/network/ansible/*\n'])


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_adding_bridgemem(mock_module):
    """
    cl_interface - test adding bridge members
    """
    # bridgemems option defined
    instance = mock_module.return_value
    mems = ['swp1', 'swp2', 'swp3.100']
    instance.params = {'bridgemems': mems,
                       'ifaceattrs': None}
    iface = {'name': 'viva', 'config': {}}
    add_bridgemems(instance, iface)
    assert_equals(iface['config']['bridge-ports'], ' '.join(mems))
    assert_equals(iface['config']['bridge-stp'], 'on')

    # ifaceattr option defined
    mems = ['swp1', 'swp2', 'swp3.100']
    instance.params = {'bridgemems': None,
                       'ifaceattrs': {'bridgemems': mems}}
    iface = {'name': 'viva', 'config': {}}
    add_bridgemems(instance, iface)
    assert_equals(iface['config']['bridge-ports'], ' '.join(mems))
    assert_equals(iface['config']['bridge-stp'], 'on')

    # no option set
    instance.params = {'bridgemems': None,
                       'ifaceattrs': {}}
    iface = {'name': 'viva', 'config': {}}
    add_bridgemems(instance, iface)
    assert_equals('bridge-ports' in iface['config'], False)

    # bridge ports with ranges
    mems = ['swp1-10', 'swp2', 'swp30-40.100']
    instance.params = {'bridgemems': None,
                       'ifaceattrs': {'bridgemems': mems}}
    iface = {'name': 'viva', 'config': {}}
    add_bridgemems(instance, iface)
    assert_equals(iface['config']['bridge-ports'], 'glob swp1-10 swp2 glob swp30-40.100')
    assert_equals(iface['config']['bridge-stp'], 'on')
