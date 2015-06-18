import mock
from mock import MagicMock
from nose.tools import set_trace
from library import cl_license
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


@mock.patch('library.cl_license.run_cmd')
@mock.patch('library.cl_license.AnsibleModule')
def test_cumulus_fact_not_present(mock_ansible_module,
        mock_run_cmd):
    """ cumulus fact module is not loaded """
    instance = mock_ansible_module.return_value
    cl_license.main()
    instance.fail_json.assert_called_with(msg="Add the 'cumulus_facts' " + \
            "before running cl-license. Check the cl_license documentation " + \
            "for an example")


@mock.patch('library.cl_license.AnsibleModule')
def test_license_is_installed(mock_ansible_module):
    cl_license.cumulus_license_present = True
    instance = mock_ansible_module.return_value
    cl_license.main()
    instance.exit_json.assert_called_with(msg='License exists', changed=False)

@mock.patch('library.cl_license.run_cmd')
@mock.patch('library.cl_license.AnsibleModule')
def test_license_not_installed(mock_ansible_module, mock_run_cmd):
    cl_license.cumulus_license_present = False
    instance = mock_ansible_module.return_value
    cl_license.main()
    mock_run_cmd.assert_called_with(instance, '/tmp/ce-lic-wrapper')
    instance.exit_json.assert_called_with(msg='License installed', changed=True)


