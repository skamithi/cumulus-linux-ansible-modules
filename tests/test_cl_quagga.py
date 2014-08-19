import mock
from nose.tools import set_trace
from dev_modules.cl_quagga import main, convert_to_yes_or_no, \
    setting_is_configured, modify_config
from asserts import assert_equals


def mod_args(arg):
    values = {'name': 'ospfd',
              'state': 'present'}
    return values[arg]


@mock.patch('dev_modules.cl_quagga.modify_config')
@mock.patch('dev_modules.cl_quagga.setting_is_configured')
@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_module_args(mock_module,
                     mock_check_setting,
                     mock_modify_config):
    """ cl_quagga - Test module argument specs"""
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    main()
    mock_module.assert_called_with(
        argument_spec={'name':
                       {'type': 'str', 'choices':
                        ['ospfd', 'ospf6d', 'bgp'],
                        'required': True},
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


@mock.patch('dev_modules.cl_quagga.read_daemon_file')
@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_setting_is_configured(mock_module,
                               mock_read_daemon_file):
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
    assert_equals(setting_is_configured(instance), False)


@mock.patch('dev_modules.cl_quagga.read_daemon_file')
@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_modify_config(mock_module,
                       mock_read_daemon_file):
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


def test_convert_to_yes_or_no():
    """
    cl_quagga - convert state from present/absent to yes/no
    """
    state = 'absent'
    assert_equals(convert_to_yes_or_no(state), 'no')
    state = 'present'
    assert_equals(convert_to_yes_or_no(state), 'yes')
