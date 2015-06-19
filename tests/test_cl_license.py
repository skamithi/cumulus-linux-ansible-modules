import mock
from mock import MagicMock
from nose.tools import set_trace
from library import cl_license
from asserts import assert_equals
from datetime import date, datetime

def mod_args_generator(values, *args):
    def mod_args(args):
        return values[args]
    return mod_args


@mock.patch('library.cl_license.AnsibleModule')
def test_install_license_failed(mock_ansible_module):
    """ test install license failed"""
    instance = mock_ansible_module.return_value
    instance.params = {'src': 'blah'}
    run_command = MagicMock()
    run_command.return_value = (1, 'output', 'err')
    instance.run_command = run_command
    cl_license.install_license(instance)
    run_command.assert_called_with('/usr/cumulus/bin/cl-license -i blah')
    instance.fail_json.assert_called_with(msg='err')

@mock.patch('library.cl_license.AnsibleModule')
def test_install_license_passed(mock_ansible_module):
    """ test install license passed """
    instance = mock_ansible_module.return_value
    instance.params = {'src': 'blah'}
    run_command = MagicMock()
    run_command.return_value = (0, 'output', None)
    instance.run_command = run_command
    cl_license.install_license(instance)
    run_command.assert_called_with('/usr/cumulus/bin/cl-license -i blah')
    assert_equals(instance.fail_json.call_count, 0)


@mock.patch('library.cl_license.install_license')
@mock.patch('library.cl_license.AnsibleModule')
def test_license_not_installed(mock_ansible_module,
        mock_install_license):
    instance = mock_ansible_module.return_value
    instance.params = {'src': 'blah'}
    run_command = MagicMock()
    run_command.return_value = (20, 'No license', None)
    instance.run_command = run_command
    cl_license.main()
    assert_equals(mock_install_license.call_count, 1)
    instance.exit_json.assert_called_with(msg='License installation completed',
            changed=True)

@mock.patch('library.cl_license.install_license')
@mock.patch('library.cl_license.AnsibleModule')
def test_license_already_installed(mock_ansible_module,
        mock_install_license):
    instance = mock_ansible_module.return_value
    instance.params = {'src': 'blah'}
    run_command = MagicMock()
    run_command.return_value = (0, 'license is there', None)
    instance.run_command = run_command
    cl_license.main()
    assert_equals(mock_install_license.call_count, 0)
    instance.exit_json.assert_called_with(
        msg='No change. License already installed',
        changed=False)


