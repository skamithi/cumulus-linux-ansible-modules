import mock
from mock import MagicMock
from nose.tools import set_trace
from dev_modules.cl_license import license_installed, main
from asserts import assert_equals

LICENSE_PATH = '/mnt/persist/etc/cumulus/.license.txt'


@mock.patch('dev_modules.cl_license.os.path.exists')
def test_check_license_existence(mock_os_path_exists):
    "Test check_license_existence"
    mock_module = MagicMock()
    mock_os_path_exists.return_value = True
    license_installed(mock_module)
    mock_module.exit_json.assert_called_with(
        msg='license installed', changed=False)
    mock_os_path_exists.assert_called_with(LICENSE_PATH)
    mock_os_path_exists.return_value = False
    mock_module = MagicMock()
    license_installed(mock_module)
    assert_equals(mock_module.exit_json.call_count, 0)

@mock.patch('dev_modules.cl_license.AnsibleModule')
def test_correct_reconstruction_of_syntax(mock_ansible_module):
    "Test correct cl_licence file execution"
    instance = mock_ansible_module.return_value
    instance.params.get.return_value = 'http://10.1.1.1/license.txt'
    instance.run_command.return_value = ['rc', 'out', 'err']
    main()
    instance.run_command.assert_called_with(
        '/usr/cumulus/bin/cl-license -i http://10.1.1.1/license.txt',
        check_rc=True)

def test_incorrect_cl_license_syntax():
    "Test incorrect cl_license_syntax"
    instance = mock_ansible_module.return_value
    instance.params.get_return_value = 'https://10.1.1.1/license.txt'
    instance.run_command.return_value = ['rc', 'out', 'err']
    check_license_url(mock_module)
    instance.exit_json.assert_called_with(
        msg="Wrong URL format. http:// allowed")



