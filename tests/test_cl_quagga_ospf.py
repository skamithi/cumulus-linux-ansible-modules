import mock
from mock import MagicMock
from nose.tools import set_trace
from library.cl_quagga_ospf import check_dsl_dependencies, main, \
    has_interface_config, get_running_config, update_router_id, \
    add_global_ospf_config, update_reference_bandwidth, \
    get_interface_addr_config, check_ip_addr_show, enable_int_defaults, \
    config_ospf_interface_config, enable_or_disable_ospf_on_int, \
    update_point2point, update_passive, update_cost, saveconfig, \
    check_if_ospf_is_running
from asserts import assert_equals

global_ospf_config = {
    'area': None,
    'router_id': '10.1.1.1',
    'reference_bandwidth': '40000',
    'interface': None,
    'state': None,
    'cost': None,
    'point2point': None,
    'passive': None
}

int_ospf_config = {
    'interface': 'swp1',
    'cost': None,
    'state':  'present',
    'point2point': 'yes',
    'router_id': '10.1.1.1',
    'area': '0.0.0.0'
}


def mod_args_generator(values, *args):
    def mod_args(args):
        return values[args]
    return mod_args


@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_enable_or_disable_ospf_on_int(mock_module,
                                       mock_run_cl_cmd):
    """
    cl_quagga_ospf - test enabling or disabling ospf
    """
    instance = mock_module.return_value
    # when state is absent and ospf is enabled
    values = int_ospf_config.copy()
    values['state'] = 'absent'
    instance.params.get.side_effect = mod_args_generator(values)
    instance.has_changed = False
    instance.exit_msg = ''
    instance.interface_config.get.return_value = ['ip ospf area 0.0.0.0']
    assert_equals(enable_or_disable_ospf_on_int(instance), False)
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/usr/bin/cl-ospf clear swp1 area')
    assert_equals(instance.exit_msg, 'OSPFv2 now disabled on swp1 ')
    assert_equals(instance.has_changed, True)
    # when state is absent and ospf is disabled
    instance.has_changed = False
    instance.exit_msg = ''
    instance.interface_config.get.return_value = []
    enable_or_disable_ospf_on_int(instance)
    assert_equals(instance.has_changed, False)
    assert_equals(instance.exit_msg, '')
    # when state is present and ospf is disabled and area exists
    values = int_ospf_config.copy()
    values['state'] = 'present'
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    assert_equals(enable_or_disable_ospf_on_int(instance), True)
    assert_equals(instance.exit_msg,
                  'OSPFv2 now enabled on swp1 area 0.0.0.0 ')
    assert_equals(instance.has_changed, True)
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/usr/bin/cl-ospf interface set swp1' +
                                       ' area 0.0.0.0')
    # when state is present and ospf is enabled and area is the same
    instance.has_changed = False
    instance.exit_msg = ''
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = ['ip ospf area 0.0.0.0']
    assert_equals(enable_or_disable_ospf_on_int(instance), True)
    assert_equals(instance.exit_msg, '')
    assert_equals(instance.has_changed, False)
    # return failure message when int is not in kernel
    values['interface'] = 'swp10'
    instance.params.get.side_effect = mod_args_generator(values)
    instance.has_changed = False
    instance.exit_msg = ''
    instance.interface_config.get.return_value = None
    assert_equals(enable_or_disable_ospf_on_int(instance), False)
    instance.fail_json.assert_called_with(msg='swp10 is not found in ' +
                                          'Quagga config. Check that swp10 is active in kernel')


@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_update_p2p(mock_module, mock_run_cl_cmd):
    """
    cl_quagga_ospf - test updating p2p status of ospf int
    """
    instance = mock_module.return_value
    instance.has_changed = False
    instance.exit_msg = ''
    # point2point is not configured but request to set
    values = int_ospf_config.copy()
    values['point2point'] = True
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    update_point2point(instance)
    assert_equals(instance.has_changed, True)
    assert_equals(instance.exit_msg, 'OSPFv2 point2point set on swp1 ')
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/usr/bin/cl-ospf interface set swp1 network point-to-point')
    # point2point is not configured but request set to clear
    instance.has_changed = False
    instance.exit_msg = ''
    values['point2point'] = False
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    update_point2point(instance)
    assert_equals(instance.has_changed, False)
    # point2point is configured and request not set
    instance.has_changed = False
    instance.exit_msg = ''
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = \
        ['ip ospf network point-to-point']
    update_point2point(instance)
    assert_equals(instance.has_changed, True)
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/usr/bin/cl-ospf interface clear swp1 network')
    assert_equals(instance.exit_msg,
                  'OSPFv2 point2point removed on swp1 ')
    # point2point not configured request is set
    instance.has_changed = False
    instance.exit_msg = ''
    values['point2point'] = True
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    update_point2point(instance)
    assert_equals(instance.has_changed, True)
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/usr/bin/cl-ospf interface set swp1 network point-to-point')
    assert_equals(instance.exit_msg,
                  'OSPFv2 point2point set on swp1 ')
    # point2point configured, request is set
    instance.has_changed = False
    instance.exit_msg = ''
    values['point2point'] = True
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = [
        'ip ospf network point-to-point']
    update_point2point(instance)
    assert_equals(instance.has_changed, False)


@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_update_passive(mock_module, mock_run_cl_cmd):
    """
    cl_quagga_ospf - test updating ospfv2 passive status
    """
    instance = mock_module.return_value
    instance.has_changed = False
    instance.exit_msg = ''
    # passive is not configured but request to set
    values = int_ospf_config.copy()
    values['passive'] = True
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    update_passive(instance)
    assert_equals(instance.has_changed, True)
    assert_equals(instance.exit_msg, 'swp1 is now OSPFv2 passive ')
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/usr/bin/cl-ospf interface set swp1 passive')
    # passive-int is not configured but request set to clear
    instance.has_changed = False
    instance.exit_msg = ''
    values['passive'] = False
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    update_passive(instance)
    assert_equals(instance.has_changed, False)
    # passive-int is configured and request not set
    instance.has_changed = False
    instance.exit_msg = ''
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = \
        ['passive-interface']
    update_passive(instance)
    assert_equals(instance.has_changed, True)
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/usr/bin/cl-ospf interface clear swp1 passive')
    assert_equals(instance.exit_msg,
                  'swp1 is no longer OSPFv2 passive ')
    # passive not configured request is set
    instance.has_changed = False
    instance.exit_msg = ''
    values['passive'] = True
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    update_passive(instance)
    assert_equals(instance.has_changed, True)
    mock_run_cl_cmd.assert_called_with(instance,
        '/usr/bin/cl-ospf interface set swp1 passive')
    assert_equals(instance.exit_msg,
                  'swp1 is now OSPFv2 passive ')
    # passive configured, request is set
    instance.has_changed = False
    instance.exit_msg = ''
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = [
        'passive-interface']
    update_passive(instance)
    assert_equals(instance.has_changed, False)


@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_update_cost(mock_module, mock_run_cl_cmd):
    """
    cl_quagga_ospf - test updating ospfv2 cost status
    """
    instance = mock_module.return_value
    instance.has_changed = False
    instance.exit_msg = ''
    # cost is not configured but request to set
    values = int_ospf_config.copy()
    values['cost'] = '32267'
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    update_cost(instance)
    assert_equals(instance.has_changed, True)
    assert_equals(instance.exit_msg,
                  'OSPFv2 cost on swp1 changed to 32267 ')
    mock_run_cl_cmd.assert_called_with(instance,
        '/usr/bin/cl-ospf interface set swp1 cost 32267')
    # cost is not configured but request set to clear
    instance.has_changed = False
    instance.exit_msg = ''
    instance.params.get.side_effect = mod_args_generator(int_ospf_config)
    instance.interface_config.get.return_value = []
    update_cost(instance)
    assert_equals(instance.has_changed, False)
    # cost is configured and request not set
    instance.has_changed = False
    instance.exit_msg = ''
    instance.params.get.side_effect = mod_args_generator(int_ospf_config)
    instance.interface_config.get.return_value = \
        ['ip ospf cost 32267']
    update_cost(instance)
    assert_equals(instance.has_changed, True)
    mock_run_cl_cmd.assert_called_with(instance,
        '/usr/bin/cl-ospf interface clear swp1 cost')
    assert_equals(instance.exit_msg,
                  'OSPFv2 cost on swp1 changed to default ')
    # cost not configured request is set
    instance.has_changed = False
    instance.exit_msg = ''
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = []
    update_cost(instance)
    assert_equals(instance.has_changed, True)
    mock_run_cl_cmd.assert_called_with(instance,
        '/usr/bin/cl-ospf interface set swp1 cost 32267')
    assert_equals(instance.exit_msg,
                  'OSPFv2 cost on swp1 changed to 32267 ')
    # cost configured, request is set
    instance.has_changed = False
    instance.exit_msg = ''
    instance.params.get.side_effect = mod_args_generator(values)
    instance.interface_config.get.return_value = [
        'ip ospf cost 32267']
    update_cost(instance)
    assert_equals(instance.has_changed, False)


@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_saveconfig(mock_module,
                    mock_run_cl_cmd):
    """
    cl_quagga_ospf - test saving config
    """
    instance = mock_module.return_value
    # saveconfig - true has_changed - False
    instance.exit_msg = ''
    instance.params.get.return_value = True
    instance.has_changed = False
    saveconfig(instance)
    assert_equals(instance.exit_msg, '')
    # saveconfig - true has_changed - True
    instance.exit_msg = ''
    instance.params.get.return_value = True
    instance.has_changed = True
    saveconfig(instance)
    mock_run_cl_cmd.assert_called_with(instance, '/usr/bin/vtysh -c "wr mem"')
    assert_equals(instance.exit_msg, 'Saving Config ')
    # saveconfig - False has_changed - True
    instance.exit_msg = ''
    instance.params.get.return_value = False
    instance.has_changed = True
    saveconfig(instance)
    assert_equals(instance.exit_msg, '')
    # saveconfig - False has_changed - False
    instance.exit_msg = ''
    instance.params.get.return_value = False
    instance.has_changed = False
    saveconfig(instance)
    assert_equals(instance.exit_msg, '')


@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_check_ip_addr_show(mock_module,
                            mock_run_cl_cmd):
    """
    cl_quagga_ospf  - test checking for ip address in kernel
    """
    instance = mock_module.return_value
    mock_run_cl_cmd.return_value = \
        ['55: swp52s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc ',
         '    link/ether 44:38:39:00:26:14 brd ff:ff:ff:ff:ff:ff',
         '    inet 10.1.1.1/24 scope global swp52s0']
    assert_equals(check_ip_addr_show(instance), True)
    # no ip address found in ip addr show
    mock_run_cl_cmd.return_value = \
        ['55: swp52s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc ',
         '    link/ether 44:38:39:00:26:14 brd ff:ff:ff:ff:ff:ff']
    assert_equals(check_ip_addr_show(instance), False)


@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_get_interface_address_config(mock_module,
                                      mock_run_cl_cmd):
    """
    cl_quagga_ospf - test if interface addr is present
    """
    instance = mock_module.return_value
    mock_run_cl_cmd.return_value = ''.join(
        ['[', '    {', '        "auto": true,',
         '        "config": {', '            "address": "10.1.1.1/24",',
         '            "mtu": "9000"', '        },',
         '        "addr_method": null,', '        "name": "swp52s0",',
         '        "addr_family": null', '    }', ']'])
    assert_equals(get_interface_addr_config(instance), True)


@mock.patch('library.cl_quagga_ospf.config_ospf_interface_config')
@mock.patch('library.cl_quagga_ospf.add_global_ospf_config')
@mock.patch('library.cl_quagga_ospf.has_interface_config')
@mock.patch('library.cl_quagga_ospf.check_dsl_dependencies')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_check_mod_args(mock_module,
                        mock_check_dsl_dependencies,
                        mock_has_interface_config,
                        mock_add_global_ospf,
                        mock_config_ospf_int):
    """
    cl_quagga_ospf - check mod args
    """
    instance = mock_module.return_value
    instance.params.get.return_value = MagicMock()
    main()
    mock_module.assert_called_with(argument_spec={
        'router_id': {'type': 'str'},
        'area': { 'type': 'str'},
        'reference_bandwidth': {
            'default': '40000',
            'type': 'str'
        },
        'saveconfig': {
            'type': 'bool',
            'default': False,
            'choices': ['yes', 'on', '1', 'true',
                        1, 'no', 'off', '0',
                        'false', 0]},
        'state': {'type': 'str',
                  'choices': ['present', 'absent']},
        'cost': {'type': 'str'}, 'interface': {'type': 'str'},
        'passive': {'type': 'bool',
                    'choices': ['yes', 'on', '1',
                                'true', 1, 'no',
                                'off', '0', 'false', 0]},
        'point2point': {'type': 'bool',
                        'choices': ['yes', 'on', '1',
                                    'true', 1, 'no',
                                    'off', '0', 'false', 0]}},
        mutually_exclusive=[
            ['reference_bandwidth', 'interface'],
            ['router_id', 'interface']]
    )
    assert_equals(mock_check_dsl_dependencies.call_args_list[0],
                  mock.call(instance, ['cost', 'state', 'area',
                                       'point2point', 'passive'],
                            'interface', 'swp1'))
    instance.exit_json.assert_called_with(msg='no change', changed=False)

@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_get_running_config(mock_module,
                            mock_run_cl_cmd):
    """
    cl_quagga_ospf - test getting vtysh running config
    """
    output = open('tests/vtysh.txt').read()
    mock_run_cl_cmd.return_value = output.split('\n')
    instance = mock_module.return_value
    get_running_config(instance)
    assert_equals(instance.global_config,
                  ['ospf router-id 10.100.1.1',
                   'auto-cost reference-bandwidth 40000'])
    # check that interface config is done right
    assert_equals(len(instance.interface_config.keys()), 57)
    assert_equals(instance.interface_config.get('swp52s0'),
                  ['ip ospf area 0.0.0.0',
                   'ip ospf network point-to-point',
                   'ipv6 nd suppress-ra', 'link-detect',
                   'passive-interface'])
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/usr/bin/vtysh -c "show run"')

@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.get_config_line')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_update_router_id(mock_module,
                          mock_get_config_line,
                          mock_run_cl_cmd):
    """
    cl_quagga_ospf - updating router_id
    """
    instance = mock_module.return_value
    instance.exit_msg = ''
    instance.params.get.return_value = '10.1.1.1'
    # no router id defined
    mock_get_config_line.return_value = None
    update_router_id(instance)
    assert_equals(instance.exit_msg, 'router-id updated ')
    assert_equals(instance.has_changed, True)
    cmd_line = '/usr/bin/cl-ospf router-id set 10.1.1.1'
    mock_run_cl_cmd.assert_called_with(instance, cmd_line)
    # router id is different
    instance.exit_msg = ''
    instance.has_changed = False
    mock_get_config_line.return_value = 'ospf router-id 10.2.2.2'
    update_router_id(instance)
    assert_equals(instance.exit_msg, 'router-id updated ')
    assert_equals(instance.has_changed, True)
    cmd_line = '/usr/bin/cl-ospf router-id set 10.1.1.1'
    mock_run_cl_cmd.assert_called_with(instance, cmd_line)
    # router id is the same
    instance.exit_msg = ''
    instance.has_changed = False
    mock_get_config_line.return_value = 'ospf router-id 10.1.1.1'
    update_router_id(instance)
    assert_equals(instance.exit_msg, '')
    assert_equals(instance.has_changed, False)


@mock.patch('library.cl_quagga_ospf.run_cl_cmd')
@mock.patch('library.cl_quagga_ospf.get_config_line')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_update_reference_bandwidth(mock_module,
                                    mock_get_config_line,
                                    mock_run_cl_cmd):
    """
    cl_quagga_ospf - test updating reference bandwidth
    """
    instance = mock_module.return_value
    instance.exit_msg = ''
    instance.params.get.return_value = '40000'
    # no reference bandwidth defined - highly unlikely since default is set
    mock_get_config_line.return_value = None
    change_msg = 'reference bandwidth updated '
    update_reference_bandwidth(instance)
    assert_equals(instance.exit_msg, change_msg)
    assert_equals(instance.has_changed, True)
    cmd_line = '/usr/bin/cl-ospf auto-cost set reference-bandwidth 40000'
    mock_run_cl_cmd.assert_called_with(instance, cmd_line)
    # reference bandwidth is different
    instance.exit_msg = ''
    instance.has_changed = False
    mock_get_config_line.return_value = 'auto-cost reference-bandwidth 45000'
    update_reference_bandwidth(instance)
    assert_equals(instance.exit_msg, change_msg)
    assert_equals(instance.has_changed, True)
    mock_run_cl_cmd.assert_called_with(instance, cmd_line)
    # router id is the same
    instance.exit_msg = ''
    instance.has_changed = False
    mock_get_config_line.return_value = 'auto-cost reference-bandwidth 40000'
    update_reference_bandwidth(instance)
    assert_equals(instance.exit_msg, '')
    assert_equals(instance.has_changed, False)


@mock.patch('library.cl_quagga_ospf.enable_int_defaults')
@mock.patch('library.cl_quagga_ospf.get_running_config')
@mock.patch('library.cl_quagga_ospf.get_interface_addr_config')
@mock.patch('library.cl_quagga_ospf.enable_or_disable_ospf_on_int')
@mock.patch('library.cl_quagga_ospf.update_point2point')
@mock.patch('library.cl_quagga_ospf.update_cost')
@mock.patch('library.cl_quagga_ospf.update_passive')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_config_ospf_interface_config(mock_module,
                                      mock_update_passive,
                                      mock_update_cost,
                                      mock_update_point2point,
                                      mock_ospf_on_int,
                                      mock_get_interface_addr,
                                      mock_get_running_config,
                                      mock_enable_defaults):
    """
    cl_quagga_ospf - test configuring ospf interface
    """
    instance = mock_module.return_value
    manager = mock.Mock()
    manager.attach_mock(mock_get_running_config, 'get_running_config')
    manager.attach_mock(mock_get_interface_addr, 'get_interface_addr_config')
    manager.attach_mock(mock_ospf_on_int, 'enable_or_disable_ospf_on_int')
    manager.attach_mock(mock_update_point2point, 'update_point2point')
    manager.attach_mock(mock_update_cost, 'update_cost')
    manager.attach_mock(mock_update_passive, 'update_passive')
    manager.attach_mock(mock_enable_defaults, 'enable_int_defaults')
    # enable the ospf interface
    expected_calls = [mock.call.enable_int_defaults(instance),
                      mock.call.get_running_config(instance),
                      mock.call.get_interface_addr_config(instance),
                      mock.call.enable_or_disable_ospf_on_int(instance),
                      mock.call.update_point2point(instance),
                      mock.call.update_cost(instance),
                      mock.call.update_passive(instance)]
    config_ospf_interface_config(instance)
    assert_equals(manager.method_calls, expected_calls)
    # disable ospf on the interface
    mock_ospf_on_int.return_value = False
    manager = mock.Mock()
    manager.attach_mock(mock_get_running_config, 'get_running_config')
    manager.attach_mock(mock_get_interface_addr, 'get_interface_addr_config')
    manager.attach_mock(mock_ospf_on_int, 'enable_or_disable_ospf_on_int')
    manager.attach_mock(mock_update_point2point, 'update_point2point')
    manager.attach_mock(mock_update_cost, 'update_cost')
    manager.attach_mock(mock_update_passive, 'update_passive')
    expected_calls = [mock.call.get_running_config(instance),
                      mock.call.get_interface_addr_config(instance),
                      mock.call.enable_or_disable_ospf_on_int(instance)]
    config_ospf_interface_config(instance)
    assert_equals(manager.method_calls, expected_calls)


@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_enable_int_defaults(mock_module):
    instance = mock_module.return_value
    # state param is None. enable_int_defaults should set it to 'present'
    values = int_ospf_config.copy()
    values['state'] = None
    instance.params.get.side_effect = mod_args_generator(values)
    enable_int_defaults(instance)
    assert_equals(instance.params.__setitem__.call_args_list,
                  [mock.call('state', 'present')])
    # when area params is None, enable_int_default should set it to '0.0.0.0'
    mock_module.reset_mock()  # reset mock attrs
    values = int_ospf_config.copy()
    values['area'] = None
    instance.params.get.side_effect = mod_args_generator(values)
    enable_int_defaults(instance)
    assert_equals(instance.params.__setitem__.call_args_list,
                  [mock.call('area', '0.0.0.0')])


@mock.patch('library.cl_quagga_ospf.update_reference_bandwidth')
@mock.patch('library.cl_quagga_ospf.get_running_config')
@mock.patch('library.cl_quagga_ospf.update_router_id')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_add_global_ospf_config(mock_module,
                                mock_update_router_id,
                                mock_get_running_config,
                                mock_reference_bandwidth):
    """
    cl_quagga_ospf - test setting global ospfv2 config
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_generator(global_ospf_config)
    manager = mock.Mock()
    manager.attach_mock(mock_get_running_config, 'get_running_config')
    manager.attach_mock(mock_update_router_id, 'update_router_id')
    manager.attach_mock(mock_reference_bandwidth, 'update_reference_bandwidth')
    add_global_ospf_config(instance)
    expected_calls = [mock.call.get_running_config(instance),
                      mock.call.update_router_id(instance),
                      mock.call.update_reference_bandwidth(instance)]
    # check order of functions called
    assert_equals(manager.method_calls, expected_calls)
    # ensure exit_json is called at the end of the function with a change or no
    # change
    assert_equals(instance.exit_json.call_count, 1)

@mock.patch('library.cl_quagga_ospf.os.path.exists')
@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_check_if_ospf_is_running(mock_module,
                                  mock_path_exists):
    # if ospf is running
    mock_path_exists.return_value = True
    check_if_ospf_is_running(mock_module)
    assert_equals(mock_module.fail_json.call_count, 0)
    mock_module.reset_mock()
    # if ospf is not running
    mock_path_exists.return_value = False
    check_if_ospf_is_running(mock_module)
    assert_equals(mock_module.fail_json.call_count, 1)
    mock_path_exists.assert_called_with('/var/run/quagga/ospfd.pid')




@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_has_int_config(mock_module):
    """
    cl_quagga_ospf - test has interface config
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_generator(int_ospf_config)
    assert_equals(has_interface_config(instance), True)
    values = int_ospf_config.copy()
    values['interface'] = None
    instance.params.get.side_effect = mod_args_generator(values)
    assert_equals(has_interface_config(instance), False)


@mock.patch('library.cl_quagga_ospf.AnsibleModule')
def test_check_dsl_dependencies(mock_module):
    """
    cl_quagga_ospf - check dsl dependencies
    """
    instance = mock_module.return_value
    values = int_ospf_config.copy()
    values['interface'] = None
    instance.params.get.side_effect = mod_args_generator(values)
    _input_options = ['point2point', 'cost']
    _depends = 'interface'
    check_dsl_dependencies(instance, _input_options, _depends, 'swp1')
    instance.fail_json.assert_called_with(
        msg="incorrect syntax. point2point must have an " +
        "interface option. Example 'cl_quagga_ospf: interface=swp1 " +
        "point2point=yes'"
    )
    # check dsl when putting in global config
    mock_module.reset_mock()
    # create a new instance of AnsibleModule
    instance.params.get.side_effect = mod_args_generator(global_ospf_config)
    check_dsl_dependencies(instance, ['cost', 'state', 'area',
                                      'point2point', 'passive'],
                           'interface', 'swp1')
    assert_equals(instance.fail_json.call_count, 0)


