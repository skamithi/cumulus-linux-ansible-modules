import mock
from nose.tools import set_trace
from dev_modules.cl_quagga import main, convert_to_yes_or_no, \
    setting_is_configured
from asserts import assert_equals


def mod_args(arg):
    values = {'name': 'ospfd',
              'state': 'present'}
    return values[arg]


@mock.patch('dev_modules.cl_quagga.setting_is_configured')
@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_module_args(mock_module,
                     mock_check_setting):
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


def check_setting_args(arg):
    values = {
        'name': 'ospfd',
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
    assert_equals(setting_is_configured(instance), True)
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


def test_convert_to_yes_or_no():
    """
    cl_quagga - convert state from present/absent to yes/no
    """
    state = 'absent'
    assert_equals(convert_to_yes_or_no(state), 'no')
    state = 'present'
    assert_equals(convert_to_yes_or_no(state), 'yes')
