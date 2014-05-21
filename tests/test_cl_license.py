import mock
import sys
from time import time
from mock import MagicMock
from nose.tools import set_trace
from dev_modules.cl_license import license_installed, main, \
    check_license_url, check_for_switchd_run_ready
from asserts import assert_equals

LICENSE_PATH = '/etc/cumulus/.license.txt'

""" List of return values for  module.params.get() function
if you give the lines module.params.get('url') mock will return
what is seen in this function below
"""


def mod_args_return_values_switchd_no(arg):
    values = {'src': 'http://10.1.1.1/license.txt',
              'restart_switchd': 'no'}
    return values[arg]


def mod_args_return_values_switchd_yes(arg):
    values = {'src': 'http://10.1.1.1/license.txt',
              'restart_switchd': 'yes'}
    return values[arg]


@mock.patch('dev_modules.cl_license.os.path.exists')
def test_check_license_existence(mock_os_path_exists):
    "Test check_license_existence"
    mock_module = MagicMock()
    mock_os_path_exists.return_value = True
    license_installed(mock_module)
    mock_module.exit_json.assert_called_with(
        msg='license already installed', changed=False)
    mock_os_path_exists.assert_called_with(LICENSE_PATH)
    mock_os_path_exists.return_value = False
    mock_module = MagicMock()
    license_installed(mock_module)
    assert_equals(mock_module.exit_json.call_count, 0)


@mock.patch('dev_modules.cl_license.AnsibleModule')
def test_run_main_restart_switchd_no(mock_ansible_module):
    "Test correct cl_licence file execution when restart_switchd_is_no"
    instance = mock_ansible_module.return_value
    instance.params.get.side_effect = mod_args_return_values_switchd_no
    instance.run_command.return_value = ['0', '', '']
    main()
    instance.run_command.assert_called_with(
        '/usr/cumulus/bin/cl-license -i http://10.1.1.1/license.txt',
        check_rc=True)
    _msg = 'license updated/installed. no request to restart switchd'
    instance.exit_json.assert_called_with(msg=_msg, changed=True)

@mock.patch('dev_modules.cl_license.AnsibleModule')
@mock.patch('dev_modules.cl_license.restart_switchd_now')
def test_run_main_restart_switchd_yes(mock_restart_switchd, mock_ansible_module):
    """
    Test correct cl_licence file execution when restart_switchd_is_yes\
    and switchd fails to start.
    """
    mock_restart_switchd.return_value = False
    instance = mock_ansible_module.return_value
    instance.params.get.side_effect = mod_args_return_values_switchd_yes
    instance.run_command.return_value = ['0', '', '']
    main()
    instance.run_command.assert_called_with(
        '/usr/cumulus/bin/cl-license -i http://10.1.1.1/license.txt',
        check_rc=True)
    instance.fail_json.assert_called_with(
        msg='license updated/installed. switchd failed to restart')


@mock.patch('dev_modules.cl_license.AnsibleModule')
@mock.patch('dev_modules.cl_license.restart_switchd_now')
def test_run_main_restart_switchd_yes_doesn_fail(mock_restart_switchd, mock_ansible_module):
    """
    Test correct cl_licence file execution when restart_switchd_is_yes\
    and switchd starts properly
    """
    mock_restart_switchd.return_value = True
    instance = mock_ansible_module.return_value
    instance.params.get.side_effect = mod_args_return_values_switchd_yes
    instance.run_command.return_value = ['0', '', '']
    main()
    instance.run_command.assert_called_with(
        '/usr/cumulus/bin/cl-license -i http://10.1.1.1/license.txt',
        check_rc=True)
    assert_equals(instance.fail_json.call_count, 0)
    instance.exit_json.assert_called_with(
        msg='license updated/installed. switchd restarted', changed=True)

@mock.patch('dev_modules.cl_license.AnsibleModule')
@mock.patch('dev_modules.cl_license.time.sleep')
@mock.patch('dev_modules.cl_license.os.path.exists')
def test_check_for_switch_running(mock_os_path_exists,
                                  mock_time,
                                  mock_module):
    """
    Test to check that it iterates for 30 seconds before failing\
    when checking for switchd startup
    """
    mock_os_path_exists.return_value = False
    check_for_switchd_run_ready(mock_module)
    assert_equals(mock_time.call_count, 30)
    mock_os_path_exists.assert_called_with('/var/run/switchd.ready')
