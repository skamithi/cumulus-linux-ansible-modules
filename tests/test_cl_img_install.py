import mock
from nose.tools import set_trace
from dev_modules.cl_img_install import install_img, \
    check_url, switch_slots, get_active_slot, get_primary_slot_num
from asserts import assert_equals


def mod_args(arg):
    values = {'version': '2.0.0',
              'src': 'http://10.1.1.1/cl.bin',
              'switch_slots': 'yes'}
    return values[arg]


def slot_info():
    return {
        '1': {'version': '2.0.0'},
        '2': {'version': '2.0.2',
              'primary': True}
    }


@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_get_active_slot(mock_module):
    """
    Test getting active slot information
    """
    instance = mock_module.return_value
    cmdline = open('tests/proc_cmdline.txt')
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = cmdline
        assert_equals(get_active_slot(instance), '2')
        mock_open.assert_called_with('/proc/cmdline')

@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_getting_primary_slot_num(mock_module, mock_run_cmd):
    """
    Test getting primary slot number
    """
    instance = mock_module.return_value
    mock_run_cmd.return_value = ['1']
    assert_equals(get_primary_slot_num(instance), '1')

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
    values = {'switch_slots': 'yes'}
    return values[arg]


def mod_args_switch_slots_no(arg):
    values = {'switch_slots': 'no'}
    return values[arg]


@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_img_install(mock_module, mock_run_cl_cmd):
    """
    Test install image
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    install_img(instance)
    cmd = '/usr/cumulus/bin/cl-img-install -f %s' % (mod_args('src'))
    mock_run_cl_cmd.assert_called_with(instance, cmd)


@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_switch_slots(mock_module, mock_run_cl_cmd):
    """
    Test switching slots
    """
    instance = mock_module.return_value

    instance.params.get.side_effect = mod_args_switch_slots_no
    switch_slots(instance, 1)
    assert_equals(mock_run_cl_cmd.call_count, 0)

    instance.params.get.side_effect = mod_args_switch_slots_yes
    switch_slots(instance, '1')
    runcmd = '/usr/cumulus/bin/cl-img-select 1'
    mock_run_cl_cmd.assert_called_with(instance, runcmd)
