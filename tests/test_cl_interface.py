import mock
from nose.tools import set_trace
from dev_modules.cl_interface import get_iface_type, add_ipv4, \
    add_ipv6
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


@mock.patch('dev_modules.cl_img_install.AnsibleModule')
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


@mock.patch('dev_modules.cl_img_install.AnsibleModule')
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


@mock.patch('dev_modules.cl_img_install.AnsibleModule')
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
