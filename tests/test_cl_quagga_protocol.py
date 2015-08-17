import mock
from nose.tools import set_trace
from library.cl_quagga_protocol import main, convert_to_yes_or_no, \
    setting_is_configured, modify_config
from asserts import assert_equals


mod_args = {'name': 'ospfd',
            'state': 'present',
            'activate': False}


def mod_args_generator(values, *args):
    def mod_args(args):
        return values[args]
    return mod_args


@mock.patch('library.cl_quagga_protocol.run_cl_cmd')
@mock.patch('library.cl_quagga_protocol.modify_config')
@mock.patch('library.cl_quagga_protocol.setting_is_configured')
@mock.patch('library.cl_quagga_protocol.AnsibleModule')
def test_restarting_quagga(mock_module,
                           mock_check_setting,
                           mock_modify_config,
                           mock_run_cmd):
    """
    cl_quagga_protocol - test restarting quagga
    """
    instance = mock_module.return_value
    # activate = yes
    values = mod_args.copy()
    values['activate'] = True
    instance.params.get.side_effect = mod_args_generator(values)
    main()
    _msg = 'ospfd protocol setting modified to yes. Restarted Quagga Service'
    instance.exit_json.assert_called_with(msg=_msg, changed=True)
    # activate = no
    values = mod_args.copy()
    values['activate'] = False
    instance.params.get.side_effect = mod_args_generator(values)
    main()
    _msg = 'ospfd protocol setting modified to yes'
    instance.exit_json.assert_called_with(msg=_msg, changed=True)


@mock.patch('library.cl_quagga_protocol.modify_config')
@mock.patch('library.cl_quagga_protocol.setting_is_configured')
@mock.patch('library.cl_quagga_protocol.AnsibleModule')
def test_module_args(mock_module,
                     mock_check_setting,
                     mock_modify_config):
    """ cl_quagga_protocol - Test module argument specs"""
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_generator(mod_args)
    main()
    mock_module.assert_called_with(
        argument_spec={'name':
                       {'type': 'str', 'choices':
                        ['ospfd', 'ospf6d', 'bgpd'],
                        'required': True},
                       'activate': {
                           'type': 'bool',
                           'choices': ['yes', 'on', '1', 'true', 1,
                                       'no', 'off', '0', 'false', 0],
                           'default': False
                       },
                       'state': {'type': 'str',
                                 'choices': ['present', 'absent'],
                                 'required': True}
                       })
    assert_equals(instance.quagga_daemon_file,
                  '/etc/quagga/daemons')


def check_setting_args(arg):
    values = {
        'name': 'ospfd',
        'state': 'present'
    }
    return values[arg]


def check_setting_args_bgp(arg):
    values = {
        'name': 'bgpd',
        'state': 'present'
    }
    return values[arg]


def check_setting_args_state_absent(arg):
    values = {
        'name': 'ospfd',
        'state': 'absent'
    }
    return values[arg]


def check_setting_args_bgp_absent(arg):
    values = {
        'name': 'bgpd',
        'state': 'absent'
    }
    return values[arg]


@mock.patch('library.cl_quagga_protocol.read_daemon_file')
@mock.patch('library.cl_quagga_protocol.AnsibleModule')
def test_setting_is_configured(mock_module,
                               mock_read_daemon_file):
    """
    cl_quagga_protocol - test setting is configured
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = check_setting_args
    daemon_output = open('tests/quagga_daemon.txt').readlines()
    mock_read_daemon_file.return_value = daemon_output
    setting_is_configured(instance)
    instance.exit_json.assert_called_with(
        msg='ospfd is configured and is present', changed=False)
    # all quagga daemons off
    daemon_output = open('tests/quagga_daemon_off.txt').readlines()
    mock_read_daemon_file.return_value = daemon_output
    assert_equals(setting_is_configured(instance), False)
    # all quagga daemons except zebra is off
    daemon_output = open('tests/quagga_daemon_zebra_off.txt').readlines()
    mock_read_daemon_file.return_value = daemon_output
    assert_equals(setting_is_configured(instance), False)
    # state absent, routing protocol is on
    instance.params.get.side_effect = check_setting_args_state_absent
    daemon_output = open('tests/quagga_daemon.txt').readlines()
    mock_read_daemon_file.return_value = daemon_output
    setting_is_configured(instance)
    # if only one daemon is enabled and set to be turned off,
    # set to turn off zebra as well
    assert_equals(instance.disable_zebra, True)


@mock.patch('library.cl_quagga_protocol.read_daemon_file')
@mock.patch('library.cl_quagga_protocol.AnsibleModule')
def test_modify_config(mock_module,
                       mock_read_daemon_file):
    """
    cl_quagga_protocol - test modifying quagga daemon config
    """
    instance = mock_module.return_value
    # ospf is disabled. Should enable zebra and ospf
    instance.params.get.side_effect = check_setting_args
    instance.quagga_daemon_file = 'tests/quagga_output.txt'
    mock_read_daemon_file.return_value = \
        open('tests/quagga_daemon_off.txt').readlines()
    modify_config(instance)
    result = open('tests/quagga_output.txt').readlines()
    assert_equals(result[0].strip(), 'zebra=yes')
    assert_equals(result[1].strip(), 'bgpd=no')
    assert_equals(result[2].strip(), 'ospfd=yes')
    # bgp is disabled enable it
    instance.params.get.side_effect = check_setting_args_bgp
    instance.quagga_daemon_file = 'tests/quagga_output_bgp.txt'
    mock_read_daemon_file.return_value = \
        open('tests/quagga_output.txt').readlines()
    modify_config(instance)
    result = open('tests/quagga_output_bgp.txt').readlines()
    assert_equals(result[0].strip(), 'zebra=yes')
    assert_equals(result[1].strip(), 'bgpd=yes')
    assert_equals(result[2].strip(), 'ospfd=yes')
    instance.params.get.side_effect = check_setting_args_state_absent
    instance.quagga_daemon_file = 'tests/quagga_disable.txt'
    mock_read_daemon_file.return_value = \
        open('tests/quagga_output_bgp.txt').readlines()
    modify_config(instance)
    result = open('tests/quagga_disable.txt').readlines()
    assert_equals(result[0].strip(), 'zebra=yes')
    assert_equals(result[1].strip(), 'bgpd=yes')
    assert_equals(result[2].strip(), 'ospfd=no')
    # remove bgp, it should also remove zebra
    instance.params.get.side_effect = check_setting_args_bgp_absent
    instance.quagga_daemon_file = 'tests/quagga_zebra_turned_off.txt'
    mock_read_daemon_file.return_value = \
        open('tests/quagga_disable.txt').readlines()
    instance.disable_zebra = True
    modify_config(instance)
    result = open('tests/quagga_zebra_turned_off.txt').readlines()
    assert_equals(result[0].strip(), 'zebra=no')
    assert_equals(result[1].strip(), 'bgpd=no')
    assert_equals(result[2].strip(), 'ospfd=no')


def test_convert_to_yes_or_no():
    """
    cl_quagga_protocol - convert state from present/absent to yes/no
    """
    state = 'absent'
    assert_equals(convert_to_yes_or_no(state), 'no')
    state = 'present'
    assert_equals(convert_to_yes_or_no(state), 'yes')
