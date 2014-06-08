import mock
from nose.tools import set_trace
from dev_modules.cl_interface import get_iface_type, add_ipv4, \
    add_ipv6, config_changed, modify_switch_config
from asserts import assert_equals

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
              'bondmems': None
              }
    return values[arg]


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_get_iface_type(mock_module):
    """
    Test getting interface type
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_bridgemems
    assert_equals(get_iface_type(instance), 'bridge')
    instance.params.get.called_with('bridgemems')

    instance.params.get.side_effect = mod_args_bondmems
    assert_equals(get_iface_type(instance), 'bond')
    instance.params.get.called_with('bondmems')

    instance.params.get.side_effect = mod_args_mgmt
    assert_equals(get_iface_type(instance), 'mgmt')
    instance.params.get_called_with('eth1')

    instance.params.get.side_effect = mod_args_lo
    assert_equals(get_iface_type(instance), 'loopback')
    instance.params.get_called_with('lo')

    instance.params.get.side_effect = mod_args_swp
    assert_equals(get_iface_type(instance), 'swp')
    instance.params.get_called_with('swp10')

    instance.params.get.side_effect = mod_args_unknown
    get_iface_type(instance)
    assert_equals(instance.fail_json.call_count, 1)
    instance.fail_json.assert_called_with(
        msg='unable to determine interface type gibberish')


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_add_ipv4(mock_module):
    addr = '10.1.1.1/24'
    instance = mock_module.return_value
    instance.params.get.return_value = None
    iface = {}
    add_ipv4(instance, iface)
    assert_equals(iface['config']['address'], None)

    instance.params.get.return_value = addr
    iface = { 'ifacetype': 'lo' }
    add_ipv4(instance, iface)
    assert_equals(iface['config']['address'], addr)


@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_add_ipv6(mock_module):
    addr = '10:1:1::1/127'
    instance = mock_module.return_value

    ## iface addr is None ipv6 is None
    instance.params.get.return_value = None
    iface = {'config': {'address': None }}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'], None)

    ## iface addr is None ipv6 is not None
    instance.params.get.return_value = addr
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'], addr)

    ## iface addr is str ipv6 is str
    instance.params.get.return_value = addr
    iface = {'config': {'address': '10.1.1.1/24' }}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10.1.1.1/24',
                   '10:1:1::1/127'])

    ## iface addr is str ipv6 is list
    instance.params.get.return_value = [addr]
    iface = {'config': {'address': '10.1.1.1/24' }}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10:1:1::1/127',
                   '10.1.1.1/24'])

    ## iface addr is list ipv6 is str
    instance.params.get.return_value = addr
    iface = {'config': {'address': ['10.1.1.1/24'] }}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10.1.1.1/24',
                   '10:1:1::1/127'])

    # iface addr is list ipv6 is list
    instance.params.get.return_value = [addr]
    iface = {'config': {'address': ['10.1.1.1/24'] }}
    add_ipv6(instance, iface)
    assert_equals(iface['config']['address'],
                  ['10.1.1.1/24',
                   '10:1:1::1/127'])

@mock.patch('dev_modules.cl_interface.exec_command')
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
        }
    }
    mock_exec.return_value = ''.join(open('tests/lo.txt').readlines())
    assert_equals(config_changed(instance, iface), True)

def loop_iface():
    iface = {
        'name' : 'lo',
        'ifacetype': 'loopback',
        'config': {
            'address': ["10:3:3::3/128",
                        "10.3.3.3/32"]
        }
    }
    return iface


@mock.patch('dev_modules.cl_interface.exec_command')
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

@mock.patch('dev_modules.cl_interface.exec_command')
@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_config_changed_ifquery_missing(mock_module, mock_exec):
    """
    Test config_changed if ifquery is missing
    """
    instance = mock_module.return_value
    instance.params.get.return_value = 'lo'
    mock_exec.side_effect = Exception
    iface =  loop_iface()
    config_changed(instance, iface)
    _msg = 'Unable to get current config using /sbin/ifquery'
    instance.fail_json.assert_called_with(msg=_msg)

@mock.patch('dev_modules.cl_interface.AnsibleModule')
def test_modify_switch_config(mock_module):
    instance = mock_module.return_value
    testwrite = open('/tmp/test.me', 'w')
    iface = loop_iface()
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = testwrite
        modify_switch_config(instance, iface)
        mock_open.assert_called_with('/etc/network/ansible/lo', 'w')

    fstr = 'auto lo\n'
    fstr += 'iface lo inet loopback\n'
    fstr += '    address 10:3:3::3/128\n'
    fstr += '    address 10.3.3.3/32\n'
    output = open('/tmp/test.me').readlines()
    assert_equals(''.join(output), fstr)


