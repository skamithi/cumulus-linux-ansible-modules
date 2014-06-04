import mock
from nose.tools import set_trace
from dev_modules.cl_img_install import install_img, \
    check_url, switch_slots, get_active_slot, get_primary_slot_num, \
    check_mnt_root_lsb_release, check_fw_print_env, get_slot_version, \
    check_sw_version, get_slot_info

from asserts import assert_equals


def mod_args(arg):
    values = {'version': '2.0.0',
              'src': 'http://10.1.1.1/cl.bin',
              'switch_slots': 'yes'}
    return values[arg]


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


def test_check_mnt_root_lsb_release():
    """
    Test getting version from root-rw config1/2
    """
    slot_num = 1
    lsb_release = open('tests/lsb-release.txt')
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = lsb_release
        assert_equals(check_mnt_root_lsb_release(slot_num),
                      '2.0.3')
        filename = '/mnt/root-rw/config%s/etc/lsb-release' % (slot_num)
        mock_open.assert_called_with(filename)

    with mock.patch('__builtin__.open') as mock_open:
        mock_open.sideffect = Exception
        assert_equals(check_mnt_root_lsb_release(2), None)


@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_check_fw_print_env(mock_module, mock_run_cmd):
    slot_num = '1'
    instance = mock_module.return_value
    mock_run_cmd.return_value = ['2.0.2-a8ec422-201404161914-final']
    assert_equals(check_fw_print_env(instance, slot_num), '2.0.2')
    cmd = '/usr/sbin/fw_printenv -n cl.ver%s' % (slot_num)
    mock_run_cmd.assert_called_with(instance, cmd)


@mock.patch('dev_modules.cl_img_install.AnsibleModule')
@mock.patch('dev_modules.cl_img_install.check_mnt_root_lsb_release')
@mock.patch('dev_modules.cl_img_install.check_fw_print_env')
def test_get_slot_version(mock_from_onie,
                          mock_from_etc,
                          mock_module):
    instance = mock_module.return_value
    mock_from_etc.return_value = '2.0.2'
    get_slot_version(instance, '1')
    assert_equals(mock_from_onie.call_count, 0)

    mock_from_etc.return_value = None
    get_slot_version(instance, '1')
    assert_equals(mock_from_onie.call_count, 1)


def slotvers(module, arg):
    values = {'1': '2.0.3', '2': '2.0.10'}
    return values[arg]


def slot_info():
    return {'1':
            {'active': True,
             'version': '2.0.3'},
            '2':
            {'version': '2.0.10',
             'primary': True}}


def slot_info2():
    return {'1':
            {'version': '2.0.3'},
            '2':
            {'version': '2.0.10',
             'primary': True,
             'active': True}}


@mock.patch('dev_modules.cl_img_install.get_primary_slot_num')
@mock.patch('dev_modules.cl_img_install.get_active_slot')
@mock.patch('dev_modules.cl_img_install.get_slot_version')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_get_slot_info(mock_module,
                       mock_get_slot_ver,
                       mock_active_ver,
                       mock_primary_ver):
    instance = mock_module.return_value
    mock_get_slot_ver.side_effect = slotvers
    mock_active_ver.return_value = '1'
    mock_primary_ver.return_value = '2'
    assert_equals(get_slot_info(instance), slot_info())

@mock.patch('dev_modules.cl_img_install.switch_slots')
@mock.patch('dev_modules.cl_img_install.get_slot_info')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_check_sw_version(mock_module, mock_get_slot_info, mock_switch_slots):
    instance = mock_module.return_value
    mock_get_slot_info.return_value = slot_info()
    ver = '2.0.10'
    check_sw_version(instance, ver)
    _msg = 'Version 2.0.10 is installed in the alternate slot. ' +\
        'Next reboot, switch will load 2.0.10.'
    instance.exit_json.assert_called_with(msg=_msg, changed=False)

    ver = '2.0.3'
    check_sw_version(instance, ver)
    _msg = 'Version 2.0.3 is installed in the active slot'
    instance.exit_json.assert_called_with(msg=_msg, changed=False)

    ver = '2.0.3'
    mock_get_slot_info.return_value = slot_info2()
    check_sw_version(instance, ver)
    instance.exit_json.assert_called_with(msg="Version 2.0.3 is installed in the alternate slot. Next reboot will not load 2.0.3. switch_slots keyword set to 'no'.", changed=False)

    instance.params.get.return_value = 'yes'
    check_sw_version(instance, ver)
    instance.exit_json.assert_called_with(msg='Version 2.0.3 is installed in the alternate slot. cl-img-select has made the alternate slot the primary slot. Next reboot, switch will load 2.0.3.', changed=True)


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
