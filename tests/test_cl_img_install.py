import mock
from nose.tools import set_trace
from dev_modules.cl_img_install import install_img, \
    check_url, switch_slot, get_active_slot, get_primary_slot_num, \
    determine_sw_version, check_mnt_root_lsb_release, check_fw_print_env, get_slot_version, \
    check_sw_version, get_slot_info, main

from asserts import assert_equals


def mod_args(arg):
    values = {'version': '2.0.0',
              'src': 'http://10.1.1.1/cl.bin',
              'switch_slot': 'yes'}
    return values[arg]


def mod_args_no_switch_slot(arg):
    values = {'version': None,
              'switch_slot': 'no',
              'src': '/usr/local/CumulusLinux-2.1.3.bin'}
    return values[arg]


def mod_args_version_in_file(arg):
    values = {'version': None,
              'src': 'http://10.1.1.1/CumulusLinux-2-3-1',
              'switch_slot': 'yes'}
    return values[arg]


@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_determine_sw_version(mock_module):
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    _version = determine_sw_version(instance)
    assert_equals(_version, '2.0.0')
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_version_in_file
    _version = determine_sw_version(instance)
    assert_equals(_version, '2.3.1')


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
    mock_from_onie.return_value = '2.0.10'
    assert_equals(get_slot_version(instance, '1'), '2.0.2')
    assert_equals(mock_from_onie.call_count, 0)

    mock_from_etc.return_value = None
    assert_equals(get_slot_version(instance, '1'), '2.0.10')
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


@mock.patch('dev_modules.cl_img_install.switch_slot')
@mock.patch('dev_modules.cl_img_install.get_slot_info')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_check_sw_version(mock_module, mock_get_slot_info, mock_switch_slot):
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
    instance.exit_json.assert_called_with(
        msg="Version 2.0.3 is installed in the alternate slot." +
        ' Next reboot will not load 2.0.3. ' +
        "switch_slot keyword set to 'no'.", changed=False)

    instance.params.get.return_value = 'yes'
    check_sw_version(instance, ver)
    instance.exit_json.assert_called_with(
        msg='Version 2.0.3 is installed in the alternate slot. ' +
        'cl-img-select has made the alternate slot the primary slot. ' +
        'Next reboot, switch will load 2.0.3.', changed=True)


@mock.patch('dev_modules.cl_img_install.install_img')
@mock.patch('dev_modules.cl_img_install.check_url')
@mock.patch('dev_modules.cl_img_install.check_sw_version')
@mock.patch('dev_modules.cl_img_install.determine_sw_version')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_module_args(mock_module,
                     mock_det_ver,
                     mock_check_ver,
                     mock_check_url,
                     mock_install_img):
    """ cl_img_install - Test module argument specs"""
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    main()
    mock_module.assert_called_with(
        argument_spec={'src': {'required': True, 'type': 'str'},
                       'version': {'type': 'str'},
                       'switch_slot': {
                           'default': 'no', 'choices': ['yes', 'no']}})


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


def mod_args_switch_slot_yes(arg):
    values = {'switch_slot': 'yes'}
    return values[arg]


def mod_args_switch_slot_no(arg):
    values = {'switch_slot': 'no'}
    return values[arg]


@mock.patch('dev_modules.cl_img_install.switch_slot')
@mock.patch('dev_modules.cl_img_install.get_slot_info')
@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_img_install(mock_module, mock_run_cl_cmd,
                     mock_get_slot_info, mock_switch_slot):
    """
    Test install image
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_no_switch_slot
    install_img(instance, '2.0.3')
    cmd = '/usr/cumulus/bin/cl-img-install -f %s' % \
        (mod_args_no_switch_slot('src'))
    mock_run_cl_cmd.assert_called_with(instance, cmd)
    instance.exit_json.assert_called_with(
        msg='Cumulus Linux Version 2.0.3 ' +
        'successfully installed in alternate slot',
        changed=True)
    # test using when switching slots
    instance.params.get.side_effect = mod_args
    mock_get_slot_info.return_value = {'1': {'version': '2.0.2',
                                             'active': True,
                                             'primary': True},
                                       '2': {'version': '2.0.3'}}
    install_img(instance, '2.0.3')
    assert_equals(mock_switch_slot.call_count, 1)


@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_switch_slot(mock_module, mock_run_cl_cmd):
    """
    Test switching slots
    """
    instance = mock_module.return_value

    instance.params.get.side_effect = mod_args_switch_slot_no
    switch_slot(instance, 1)
    assert_equals(mock_run_cl_cmd.call_count, 0)

    instance.params.get.side_effect = mod_args_switch_slot_yes
    switch_slot(instance, '1')
    runcmd = '/usr/cumulus/bin/cl-img-select 1'
    mock_run_cl_cmd.assert_called_with(instance, runcmd)
