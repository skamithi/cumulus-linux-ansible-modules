"from mock import MagicMock"
import mock
from nose.tools import set_trace
from dev_modules.cl_img_install import get_sw_version,\
    check_url, check_sw_version, main, switch_slots, install_img
from asserts import assert_equals

def mod_args(arg):
    values = {'version': '2.0.0',
              'src': 'http://10.1.1.1/cl.bin',
              'reboot': 'yes'}
    return values[arg]

def test_get_sw_version():
    release_file = open('tests/lsb-release.txt')
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = release_file
        assert_equals(get_sw_version(), '2.0.0')

@mock.patch('dev_modules.cl_img_install.AnsibleModule')
@mock.patch('dev_modules.cl_img_install.get_sw_version')
def test_sw_ver_same(mock_version, mock_module):
    """
    Test that module exists if software version installed matches\
    version you want to install
    """
    version = '2.0.0'
    mock_version.return_value = version
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    check_sw_version(instance, version)
    instance.exit_json.assert_called_with(
        msg='Version 2.0.0 already installed',
        changed=False)

@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_check_url(mock_module):
    """
    Test to see that image install url is properly defined
    """
    src = 'http://10.1.1.1/image.bin'
    assert_equals(check_url(mock_module, src), True)
    assert_equals(mock_module.fail_json.call_count, 0)
    src = '/home/my/image.bin'
    assert_equals(check_url(mock_module, src),  True)
    assert_equals(mock_module.fail_json.call_count, 0)
    src = 'https://10.1.1.1/sdfdf.bin'
    assert_equals(check_url(mock_module, src),  True)
    assert_equals(mock_module.fail_json.call_count, 0)
    src = 'ftp://sdfdf.bin'
    _msg = 'Image Path URL. Wrong Format %s' % (src)
    assert_equals(check_url(mock_module, src),  False)
    mock_module.fail_json.assert_called_with(
        msg=_msg)

def mod_args_switch_slots_yes(arg):
    values = {'switch_slots': 'yes' }
    return values[arg]

def mod_args_switch_slots_no(arg):
    values = { 'switch_slots': 'no' }
    return values[arg]


@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_img_install(mock_module, mock_run_cl_cmd):
    """
    Test install image
    """
    instance = mock_module.return_value
    instance.params.get.side_effect
    install_img(instance)
    cmd = '/usr/cumulus/bin/cl-img-install'
    mock_run_cl_cmd.assert_called_with(instance, cmd)

@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_switch_slots(mock_module, mock_run_cl_cmd):
    """
    Test switching slots
    """
    instance = mock_module.return_value

    instance.params.get.side_effect = mod_args_switch_slots_no
    switch_slots(instance)
    assert_equals(mock_run_cl_cmd.call_count, 0)

    instance.params.get.side_effect = mod_args_switch_slots_yes
    switch_slots(instance)
    runcmd = '/usr/cumulus/bin/cl-img-select -s'
    mock_run_cl_cmd.assert_called_with(instance, runcmd)

@mock.patch('dev_modules.cl_img_install.switch_slots')
@mock.patch('dev_modules.cl_img_install.install_img')
@mock.patch('dev_modules.cl_img_install.check_url')
@mock.patch('dev_modules.cl_img_install.check_sw_version')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_funcs_called_from_main(mock_module, mock_check_sw,
                     mock_check_url, mock_install_img,
                     mock_switch_slots):
    """
    Test functions called from main
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    main()
    assert_equals(mock_check_url.call_count, 1)
    assert_equals(mock_check_sw.call_count, 1)
    assert_equals(mock_install_img.call_count, 1)
    assert_equals(mock_switch_slots.call_count, 1)


