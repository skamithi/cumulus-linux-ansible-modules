from mock import call
import mock
from nose.tools import set_trace
from dev_modules.cl_interface import get_iface_type, add_ipv4, \
    add_ipv6, config_changed, modify_switch_config, main, \
    remove_config_from_etc_net_interfaces, config_swp_iface, \
    check_if_applyconfig_name_defined_only, add_bridgeports, \
    config_dhcp, compare_config, merge_config, remove_none_attrs, \
    config_speed, config_mtu, add_bondslaves, config_alias, \
    config_iface
from asserts import assert_equals


def mod_args_none(arg):
    values = {'bridgeports': None,
              'bondslaves': None,
              'name': 'swp10'}
    return values[arg]


def mod_args_bridgeports(arg):
    values = {'bridgeports': '2.0.0'}
    return values[arg]


def mod_args_bondslaves(arg):
    values = {'bondslaves': 'swp56, swp57',
              'bridgeports': None}
    return values[arg]


def mod_args_mgmt(arg):
    values = {'name': 'eth1',
              'bridgeports': None,
              'bondslaves': None
              }
    return values[arg]


def mod_args_lo(arg):
    values = {'name': 'lo',
              'bridgeports': None,
              'bondslaves': None
              }
    return values[arg]


def mod_args_swp(arg):
    values = {'name': 'swp10',
              'bridgeports': None,
              'bondslaves': None
              }
    return values[arg]


def mod_args_unknown(arg):
    values = {'name': 'gibberish',
              'bridgeports': None,
              'bondslaves': None,
              'applyconfig': 'no',
              'ifaceattrs': None,
              'state': 'present',
              }
    return values[arg]


def mod_args_generator(values, *args):
    def mod_args(args):
        return values[args]
    return mod_args


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
    values = {'name': 'gibberish',
              'bridgeports': None,
              'bondslaves': None,
              'applyconfig': 'no',
              'ifaceattrs': None,
              'state': 'present',
              }
    instance.params.get.side_effect = mod_args_generator(values)
    mock_get_iface_type.return_value = 'loopback'
    main()
    mock_module.assert_called_with(
        argument_spec={'bondslaves': {'type': 'list'},
                       'ipv6': {'type': 'list'},
                       'ipv4': {'type': 'list'},
                       'applyconfig': {'type': 'bool',
                                       'choices': ['yes', 'on', '1',
                                                   'true', 1, 'no',
                                                   'off', '0', 'false', 0],
                                       'default': False},
                       'name': {'required': True, 'type': 'str'},
                       'ifaceattrs': {'type': 'dict'},
                       'alias': {'type': 'str'},
                       'speed': {'type': 'str'},
                       'mtu': {'type': 'str'},
                       'dhcp': {'type': 'str', 'choices': ['yes', 'no']},
                       'stp': {'default': True, 'type': 'bool', 'choices':
                               ['yes', 'on', '1', 'true', 1, 'no',
                                'off', '0', 'false', 0]},
                       'state': {'type': 'str',
                                 'choices': ['noconfig', 'hasconfig'],
                                 'default': 'hasconfig'},
                       'bridgeports': {'type': 'list'}},
        mutually_exclusive=[['bridgeports', 'bondslaves'],
                            ['dhcp', 'ipv4'],
                            ['dhcp', 'ipv6']])

global_values = {
    'name': 'gibberish',
    'bridgeports': None,
    'bondslaves': None,
    'applyconfig': 'no',
    'speed': None,
    'mtu': None,
    'alias': None,
    'ifaceattrs': None,
    'state': 'present'
}


@mock.patch('dev_modules.cl_interface.apply_config')
@mock.patch('dev_modules.cl_interface.remove_config_from_etc_net_interfaces')
@mock.patch('dev_modules.cl_interface.modify_switch_config')
@mock.patch('dev_modules.cl_interface.config_lo_iface')
@mock.patch('dev_modules.cl_interface.config_changed')
@mock.patch('dev_modules.cl_interface.get_iface_type')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_applyconfig(mock_module,
                     mock_get_iface_type,
                     mock_config_changed,
                     mock_config_lo_iface,
                     mock_mod_sw_config,
                     mock_remove_config,
                     mock_apply_config):

    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_generator(global_values)
    main()
    assert_equals(mock_apply_config.call_count, 0)
    values = global_values.copy()
    values['applyconfig'] = True
    instance.params.get.side_effect = mod_args_generator(values)
    main()
    assert_equals(mock_apply_config.call_count, 1)


def mod_arg_state_absent(arg):
    values = {'name': 'br0',
              'state': 'absent',
              'ifaceattrs': None,
              'speed': None,
              'mtu': None,
              'alias': None,
              'applyconfig': 'no'
              }
    return values[arg]


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
    instance.params.get.side_effect = mod_args_bridgeports
    assert_equals(get_iface_type(instance, {}), 'bridge')
    instance.params.get.called_with('bridgeports')
    # test for bond
    instance.params.get.side_effect = mod_args_bondslaves
    assert_equals(get_iface_type(instance, {}), 'bond')
    instance.params.get.called_with('bondslaves')
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

    # test if ifaceattr is set for bridge
    instance.params.get_side_effect = mod_args_none
    ifaceattr = {'bridgeports': ''}
    assert_equals(get_iface_type(instance, ifaceattr), 'bridge')

    # test if ifaceattr is set for bond
    instance.params.get_side_effect = mod_args_none
    ifaceattr = {'bondslaves': ''}
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
        'applyconfig': 'yes',
        'state': 'hasconfig'}
    check_if_applyconfig_name_defined_only(instance)
    assert_equals(instance.fail_json.call_count, 0)

    instance.params = {
        'ifaceattrs': {'something': '1'},
        'name': 'sdf',
        'sdfdf': 'dfdf',
        'applyconfig': 'yes',
        'state': 'hasconfig'}

    check_if_applyconfig_name_defined_only(instance)
    instance.fail_json.assert_called_with(
        msg="when ifaceattrs is defined, " +
        "only addition options allowed  are 'name' " +
        "and 'applyconfig'")


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_add_ipv4(mock_module):
    addr = ['10.1.1.1/24']
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
    assert_equals(iface['config']['address'], addr[0])
    # addr is none, array - remove it
    instance.params.get.return_value = ['none']
    iface = {'config': {}}
    add_ipv4(instance, iface)
    assert_equals(iface['config']['address'], None)
    # addr is none , str - remote it
    instance.params.get.return_value = u'none'
    iface = {'config': {}}
    add_ipv4(instance, iface)
    assert_equals(iface['config']['address'], None)
    # addr is not empty. multiple entries
    instance.params.get.return_value = ['1', '2']
    iface = {'config': {}}
    add_ipv4(instance, iface)
    assert_equals(iface['config']['address'], ['1', '2'])


def params_with_ifaceattrs(arg):
    values = {
        'ipv6': None,
        'ifaceattrs': {
            'ipv6': u'10:1:1::1/127'
        }
    }
    return values[arg]


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_add_ipv6(mock_module):
    addr = ['10:1:1::1/127']
    instance = mock_module.return_value

    # iface addr is None ipv6 is None
    instance.params.get.return_value = None
    iface = {'config': {}}
    add_ipv6(instance, iface)
    assert_equals('address' in iface['config'], False)

    # iface addr is None ipv6 is not None
    instance.params.get.return_value = addr
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'], addr[0])

    # iface addr is str
    instance.params.get.return_value = addr
    iface = {'config': {'address': u'10.1.1.1/24'}}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10:1:1::1/127',
                   '10.1.1.1/24'])

    # iface addr is list
    instance.params.get.return_value = addr
    iface = {'config': {'address': ['10.1.1.1/24']}}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10.1.1.1/24',
                   '10:1:1::1/127'])

    # iface addr is in ifaceattrs
    instance.params.get.side_effect = params_with_ifaceattrs
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


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_state_absent_in_config_iface(mock_module):
    """
    cl-interface: if state is absent then set alias to 'noconfig'
    with no other config. setting iface with no config doesn't work
    to keep config idempotent with current code done
    """
    instance = mock_module.return_value
    instance.params.get.return_value = 'noconfig'
    config_iface(instance, {'config': {}}, 'none')
    instance.params.get.assert_called_with('state')


@mock.patch('dev_modules.cl_interface.run_cl_cmd')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_changed_different_state_absent(mock_module,
                                               mock_exec):
    """
    cl-interface - test config_changed with state == noconfig
    """
    instance = mock_module.return_value
    instance.params.get_return_value = 'lo'
    iface = {'name': 'lo', 'ifacetype': 'loopback',
             'config': {
                 'alias': 'noconfig'
             }}
    mock_exec.return_value = ''.join(open('tests/lo.txt').readlines())
    assert_equals(config_changed(instance, iface), True)


def empty_iface():
    iface = {
        'name': 'swp1',
        'ifacetype': 'unknown',
        'config': {}
    }
    return iface


def loop_iface():
    iface = {
        'name': 'lo',
        'ifacetype': 'loopback',
        'config': {
            'address': ["10:3:3::3/128",
                        "10.3.3.3/32"]
        },
        'addr_method': 'loopback',
        'addr_family': 'inet'
    }
    return iface


def swp_iface():
    iface = {
        'name': 'swp10',
        'ifacetype': 'swp',
        'config': {
            'address': ["10:3:3::3/128",
                        "10.3.3.3/32"]
        },
        'addr_method': None,
        'addr_family': None
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
    """
    cl_interface - test with inet method
    """
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

    # test when addr_method is not present
    iface = empty_iface()
    testwrite = open('/tmp/test.me', 'w')
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = testwrite
        modify_switch_config(instance, iface)
        mock_open.assert_called_with('/etc/network/ansible/swp1', 'w')
    fstr = 'auto swp1\n'
    fstr += 'iface swp1\n'
    output = open('/tmp/test.me').readlines()
    assert_equals(''.join(output), fstr)


@mock.patch('dev_modules.cl_interface.os')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_modify_switch_config2(mock_module, mock_os):
    """
    cl_interface - test when no inet method is set
    """
    instance = mock_module.return_value
    mock_os.path.exists.return_value = False
    testwrite = open('/tmp/test.me', 'w')
    iface = swp_iface()
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = testwrite
        modify_switch_config(instance, iface)
        mock_open.assert_called_with('/etc/network/ansible/swp10', 'w')

    mock_os.path.exists.assert_called_with('/etc/network/ansible/')
    fstr = 'auto swp10\n'
    fstr += 'iface swp10\n'
    fstr += '    address 10:3:3::3/128\n'
    fstr += '    address 10.3.3.3/32\n'
    output = open('/tmp/test.me').readlines()
    assert_equals(''.join(output), fstr)


@mock.patch('dev_modules.cl_interface.os')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_modify_switch_config3(mock_module, mock_os):
    """
    cl_interface - test when attr is set to none
    """
    instance = mock_module.return_value
    mock_os.path.exists.return_value = False
    testwrite = open('/tmp/test.me', 'w')
    iface = swp_iface()
    iface['config']['address'] = None
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = testwrite
        modify_switch_config(instance, iface)
        mock_open.assert_called_with('/etc/network/ansible/swp10', 'w')

    mock_os.path.exists.assert_called_with('/etc/network/ansible/')
    fstr = 'auto swp10\n'
    fstr += 'iface swp10\n'
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
    # bridgeports option defined
    instance = mock_module.return_value
    mems = ['swp1', 'swp2', 'swp3.100']
    instance.params = {'bridgeports': mems,
                       'ifaceattrs': None}
    iface = {'name': 'viva', 'config': {}}
    add_bridgeports(instance, iface)
    assert_equals(iface['config']['bridge-ports'], ' '.join(mems))
    # assert_equals(iface['config']['bridge-stp'], 'on')

    # ifaceattr option defined
    mems = ['swp1', 'swp2', 'swp3.100']
    instance.params = {'bridgeports': None,
                       'ifaceattrs': {'bridgeports': mems}}
    iface = {'name': 'viva', 'config': {}}
    add_bridgeports(instance, iface)
    assert_equals(iface['config']['bridge-ports'], ' '.join(mems))
    # assert_equals(iface['config']['bridge-stp'], 'on')

    # no option set
    instance.params = {'bridgeports': None,
                       'ifaceattrs': {}}
    iface = {'name': 'viva', 'config': {}}
    add_bridgeports(instance, iface)
    assert_equals('bridge-ports' in iface['config'], False)

    # bridge ports with ranges
    mems = ['swp1-10', 'swp2', 'swp30-40.100']
    instance.params = {'bridgeports': None,
                       'ifaceattrs': {'bridgeports': mems}}
    iface = {'name': 'viva', 'config': {}}
    add_bridgeports(instance, iface)
    assert_equals(iface['config']['bridge-ports'],
                  'glob swp1-10 swp2 glob swp30-40.100')
    # assert_equals(iface['config']['bridge-stp'], 'on')

    # bridge port set to none
    mems = ['none']
    instance.params = {'bridgeports': None,
                       'ifaceattrs': {'bridgeports': mems}}
    iface = {'name': 'viva', 'config': {}}
    add_bridgeports(instance, iface)
    assert_equals(iface['config']['bridge-ports'], None)
    # single bridge mem
    mems = 'swp1'
    instance.params = {'bridgeports': None,
                       'ifaceattrs': {'bridgeports': mems}}
    iface = {'name': 'viva', 'config': {}}
    add_bridgeports(instance, iface)
    assert_equals(iface['config']['bridge-ports'], mems)


def orig_config():
    return {
        'auto': True,
        'addr_method': None,
        'addr_family': None,
        'name': 'swp1',
        'config': {
            'bridge-ports': 'swp1 swp2',
            'speed': '1000',
            'mtu': '3000'
        }
    }


def test_compare_config():
    """
    cl_interface test compare config. config is new is different
    """
    new_config = {
        'config': {
            'bridge-ports': 'swp2 swp3',
            'address': '10.1.1.1/24'
        }
    }
    assert_equals(compare_config(new_config, orig_config()), False)


def test_compare_config2():
    """
    cl_interface test compare config. addr_method is the same
    """

    new_config = {
        'addr_method': 'dhcp',
        'addr_family': 'inet',
        'config': {
            'speed': '1000'
        }
    }
    orig = orig_config()
    orig['addr_method'] = 'dhcp'
    orig['addr_family'] = 'inet'

    assert_equals(compare_config(new_config, orig), True)


def test_compare_config3():
    """
    cl_interface test compare config.
    addr_method is different. 'config' is empty
    """
    new_config = {
        'addr_method': 'dhcp',
        'addr_family': 'inet',
        'config': {}
    }
    orig = orig_config()
    assert_equals(compare_config(new_config, orig), False)


def test_compare_config4():
    """
    cl_interface test compare config. 'config' is the same
    """
    new_config = {
        'config': {
            'speed': '1000'
        }
    }
    assert_equals(compare_config(new_config, orig_config()), True)


def test_compare_config5():
    """
    cl_interface test compare config. 'config' has new attr
    """
    new_config = {
        'config': {
            'bridge-stp': 'on'
        }
    }
    assert_equals(compare_config(new_config, orig_config()), False)


def test_compare_config6():
    """
    cl_interface attrs are marked for deletion
    """
    new_config = {
        'config': {
            'bridge-stp': None
        }
    }
    orig_config = {
        'config': {
            'speed: 100'
        }
    }
    remove_none_attrs(new_config)
    assert_equals(compare_config(new_config, orig_config), True)


def test_merge_config():
    """
    cl_interface - merge creating new element in object
    """
    new_config = {
        'config': {
            'bridge-stp': 'on'
        }
    }
    orig = orig_config()
    orig_modify = orig_config()
    merge_config(new_config, orig_modify)
    orig['config']['bridge-stp'] = 'on'
    assert_equals(orig_modify, orig)


def test_merge_config2():
    """
    cl_interface - merge config - replace existing config
    """
    new_config = {
        'config': {
            'speed': '3000'
        },
        'addr_family': 'inet',
        'addr_method': 'dhcp'
    }
    orig = orig_config()
    orig_modify = orig_config()
    merge_config(new_config, orig_modify)
    orig['addr_family'] = 'inet'
    orig['addr_method'] = 'dhcp'
    orig['config']['speed'] = '3000'
    assert_equals(orig_modify, orig)


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_speed(mock_module):
    """
    cl_interface - config speed
    """
    instance = mock_module.return_value
    # speed set in module.param not empty
    instance.params = {'speed': 1000}
    iface = {'config': {}}
    config_speed(instance, iface)
    assert_equals(iface, {'config': {'speed': 1000}})
    # speed set in module.param is 'none'
    instance.params = {'speed': 'none'}
    iface = {'config': {}}
    config_speed(instance, iface)
    assert_equals(iface, {'config': {'speed': None}})
    # speed set in ifaceattr not empty
    instance.params = {'speed': None, 'ifaceattrs': {'speed': '1000'}}
    iface = {'config': {}}
    config_speed(instance, iface)
    assert_equals(iface, {'config': {'speed': '1000'}})
    # speed set in ifaceattr is 'none'
    instance.params = {'speed': None, 'ifaceattrs': {'speed': 'none'}}
    iface = {'config': {}}
    config_speed(instance, iface)
    assert_equals(iface, {'config': {'speed': None}})


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_mtu(mock_module):
    """
    cl_interface - config mtu
    """
    instance = mock_module.return_value
    # mtu set in module.param not empty
    instance.params = {'mtu': 1000}
    iface = {'config': {}}
    config_mtu(instance, iface)
    assert_equals(iface, {'config': {'mtu': 1000}})
    # mtu set in module.param is 'none'
    instance.params = {'mtu': 'none'}
    iface = {'config': {}}
    config_mtu(instance, iface)
    assert_equals(iface, {'config': {'mtu': None}})
    # mtu set in ifaceattr not empty
    instance.params = {'mtu': None, 'ifaceattrs': {'mtu': '1000'}}
    iface = {'config': {}}
    config_mtu(instance, iface)
    assert_equals(iface, {'config': {'mtu': '1000'}})
    # mtu set in ifaceattr is 'none'
    instance.params = {'mtu': None, 'ifaceattrs': {'mtu': 'none'}}
    iface = {'config': {}}
    config_mtu(instance, iface)
    assert_equals(iface, {'config': {'mtu': None}})


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_alias(mock_module):
    """
    cl_interface - config alias
    """
    instance = mock_module.return_value
    # alias set in module.param not empty
    instance.params = {'alias': '1000'}
    iface = {'config': {}}
    config_alias(instance, iface)
    assert_equals(iface, {'config': {'alias': '1000'}})
    # alias set in module.param is 'none'
    instance.params = {'alias': 'none'}
    iface = {'config': {}}
    config_alias(instance, iface)
    assert_equals(iface, {'config': {'alias': None}})
    # alias set in ifaceattr not empty
    instance.params = {'alias': None, 'ifaceattrs': {'alias': '1000'}}
    iface = {'config': {}}
    config_alias(instance, iface)
    assert_equals(iface, {'config': {'alias': '1000'}})
    # alias set in ifaceattr is 'none'
    instance.params = {'alias': None, 'ifaceattrs': {'alias': 'none'}}
    iface = {'config': {}}
    config_alias(instance, iface)
    assert_equals(iface, {'config': {'alias': None}})


def bond_config_not_empty():
    return {
        'bond-miimon': '100',
        'bond-lacp-rate': '1',
        'bond-min-links': '1',
        'bond-slaves': 'swp1 swp2',
        'bond-mode': '802.3ad',
        'bond-xmit-hash-policy': 'layer3+4'
    }


def bond_config_empty():
    return {
        'bond-miimon': None,
        'bond-lacp-rate': None,
        'bond-min-links': None,
        'bond-slaves': None,
        'bond-mode': None,
        'bond-xmit-hash-policy': None
    }


def mod_arg_add_bond_slaves_glob(arg):
    values = {'bondslaves': ['swp1-3', 'swp4'],
              'ifaceattrs': None
              }
    return values[arg]


def mod_arg_add_bond_slaves(arg):
    values = {'bondslaves': ['swp1-3', 'swp4'],
              'ifaceattrs': None
              }
    return values[arg]


def mod_arg_add_bond_slaves_none(arg):
    values = {'bondslaves': ['None'],
              'ifaceattrs': None
              }
    return values[arg]


def mod_arg_add_bond_slaves_single(arg):
    values = {'bondslaves': ['swp1', 'swp2'],
              'ifaceattrs': None
              }
    return values[arg]


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_add_bond_slaves(mock_module):
    """
    cl_interface - test add_bond_slaves
    """
    instance = mock_module.return_value
    # bond slaves is swp1-3
    instance.params.get.side_effect = mod_arg_add_bond_slaves_glob
    iface = {'config': bond_config_empty()}
    add_bondslaves(instance, iface)
    assert_equals(iface.get('config').get('bond-slaves'), 'glob swp1-3 swp4')

    # bondslaves set to 'None'
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_arg_add_bond_slaves_none
    add_bondslaves(instance, iface)
    assert_equals(iface.get('config').get('bond-slaves'), None)

    # single interfaces, e.g swp1 , swp2
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_arg_add_bond_slaves_single
    add_bondslaves(instance, iface)
    assert_equals(iface.get('config').get('bond-slaves'), 'swp1 swp2')


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_bond_config(mock_module):
    """
    cl_interface - config bond
    """
    instance = mock_module.return_value
    # bondslaves in module params
    instance.params = {'bondslaves': ['swp1', 'swp2']}
    iface = {'config': {}}
    add_bondslaves(instance, iface)
    assert_equals(iface['config'], bond_config_not_empty())
    # bondslaves in ifaceattr params
    instance.params = {'bondslaves': None,
                       'ifaceattrs': {
                           'bondslaves': ['swp1', 'swp2']
                       }}
    iface = {'config': {}}
    add_bondslaves(instance, iface)
    assert_equals(iface['config'], bond_config_not_empty())
    # bondslaves in module params  - set to 'none'
    instance.params = {'bondslaves': ['none']}
    iface = {'config': {}}
    add_bondslaves(instance, iface)
    assert_equals(iface['config'], bond_config_empty())
    # bondslaves in ifaceattr params  - set to 'none'
    instance.params = {'bondslaves': None,
                       'ifaceattrs': {'bondslaves': 'none'}}
    iface = {'config': {}}
    add_bondslaves(instance, iface)
    assert_equals(iface['config'], bond_config_empty())
