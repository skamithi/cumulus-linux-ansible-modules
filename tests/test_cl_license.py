import mock
from mock import MagicMock
from nose.tools import set_trace
from library.cl_license import license_upto_date, main, \
    check_license_url, get_todays_date
from asserts import assert_equals
from datetime import date, datetime

LICENSE_PATH = '/etc/cumulus/.license.txt'

""" List of return values for  module.params.get() function
if you give the lines module.params.get('url') mock will return
what is seen in this function below
"""


mod_args = {
    'src': 'http://10.1.1.1/license.txt',
    'restart_switchd': True,
    'force': False
}


def mod_args_generator(values, *args):
    def mod_args(args):
        return values[args]
    return mod_args


def test_get_todays_date():
    """
    cl_license. test that getting current date returns a date,
    not a string or None
    """
    result = get_todays_date()
    assert_equals(isinstance(result, datetime), True)


@mock.patch('library.cl_license.get_todays_date')
@mock.patch('library.cl_license.os.path.exists')
def test_check_license_existence(mock_os_path_exists, mock_date):
    "Test check_license_existence"
    lf = open('tests/license.txt')
    mock_module = MagicMock()
    # force mode is enabled
    mock_module.params.get.return_value = True
    license_upto_date(mock_module)
    assert_equals(mock_os_path_exists.call_count, 0)

    # license file exists and is current
    mock_module.params.get.return_value = False
    mock_date.return_value = date(2013, 8, 6)
    mock_os_path_exists.return_value = True
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = lf
        license_upto_date(mock_module)
        mock_module.exit_json.assert_called_with(
            msg='license is installed and has not expired', changed=False)
    mock_os_path_exists.assert_called_with(LICENSE_PATH)

    # license file does not exist
    mock_os_path_exists.return_value = False
    mock_module = MagicMock()
    license_upto_date(mock_module)
    assert_equals(mock_module.exit_json.call_count, 0)

    # license file exists but has expired
    mock_os_path_exists.return_value = True
    mock_date.return_value = date(2014, 8, 6)
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = lf
        license_upto_date(mock_module)
        assert_equals(mock_module.exit_json.call_count, 0)


@mock.patch('library.cl_license.time.sleep')
@mock.patch('library.cl_license.license_is_current')
@mock.patch('library.cl_license.AnsibleModule')
def test_run_main(mock_ansible_module,
                  mock_license,
                  mock_time):
    "Test correct cl_licence file execution when restart_switchd is no"
    instance = mock_ansible_module.return_value
    instance.mock_license.return_value = True
    values = mod_args.copy()
    instance.params.get.side_effect = mod_args_generator(values)
    instance.run_command.return_value = ['0', '', '']
    main()
    instance.run_command.assert_called_with(
        '/usr/cumulus/bin/cl-license -i http://10.1.1.1/license.txt')
    _msg = 'license updated/installed. remember to restart switchd'
    instance.exit_json.assert_called_with(msg=_msg, changed=True)


@mock.patch('library.cl_license.AnsibleModule')
def test_check_license_url(mock_module):
    """
    Test to see that license url is properly defined
    """
    src = 'http://10.1.1.1/license.txt'
    assert_equals(check_license_url(mock_module, src), True)
    assert_equals(mock_module.fail_json.call_count, 0)
    src = '/home/my/file.txt'
    assert_equals(check_license_url(mock_module, src),  True)
    assert_equals(mock_module.fail_json.call_count, 0)
    src = 'https://sdfdf.txt'
    check_license_url(mock_module, src)
    mock_module.fail_json.assert_called_with(
        msg='License URL. Wrong Format https://sdfdf.txt')
