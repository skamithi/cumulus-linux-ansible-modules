import mock
from nose.tools import set_trace
from dev_modules.cl_img_install import install_img, \
    check_url, switch_slot, get_active_slot, get_primary_slot_num, \
    determine_sw_version, check_mnt_root_lsb_release, check_fw_print_env, get_slot_version, \
    check_sw_version, get_slot_info, main

from asserts import assert_equals

slot_values = {
    '1': {'version': '2.0.3'},
    '2': {'version': '2.0.10', 'primary': True, 'active': True}
}


arg_values = {
    'version': None,
    'switch_slot': 'no',
    'src': '/root/CumulusLinux-2.1.3.bin'
}


def mod_args_generator(values, *args):
    def mod_args(args):
        return values[args]
    return mod_args


@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_determine_sw_version(mock_module):
    instance = mock_module.return_value
    values = arg_values.copy()
    # version set in version otion
    values['version'] = '2.0.0'
    instance.params.get.side_effect = mod_args_generator(values)
    determine_sw_version(instance)
    assert_equals(instance.sw_version, '2.0.0')
    # version set in filename
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_generator(arg_values)
    determine_sw_version(instance)
    assert_equals(instance.sw_version, '2.1.3')
    # filename is a dev build so has a-z char in it
    values = arg_values.copy()
    values['src'] = '/root/CumulusLinux-2.2.x.bin'
    instance.params.get.side_effect = mod_args_generator(values)
    determine_sw_version(instance)
    assert_equals(instance.sw_version, '2.2.x')


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

    # test with dev image
    lsb_release = open('tests/lsb-release_dev.txt')
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = lsb_release
        assert_equals(check_mnt_root_lsb_release(slot_num),
                      '2.2.x')


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
    instance.sw_version == '2.2.0'
    mock_from_etc.return_value = '2.0.2'
    mock_from_onie.return_value = '2.0.10'
    assert_equals(get_slot_version(instance, '1'), '2.0.2')
    assert_equals(mock_from_onie.call_count, 1)

    mock_from_etc.return_value = None
    assert_equals(get_slot_version(instance, '1'), '2.0.10')
    assert_equals(mock_from_onie.call_count, 2)

    # /etc/lsb-release matches version provided by user
    instance.sw_version = '2.2.x'
    mock_from_etc.return_value = '2.2.x'
    mock_from_onie.return_value = '2.0.10'
    assert_equals(get_slot_version(instance, '1'), '2.2.x')

    # onie image version matches what user provided
    instance.sw_version = '2.0.1'
    mock_from_etc.return_value = '2.2.2'
    mock_from_onie.return_value = '2.0.1'
    assert_equals(get_slot_version(instance, '1'), '2.0.1')


def slotvers(module, arg):
    values = {'1': '2.0.3', '2': '2.0.10'}
    return values[arg]


@mock.patch('dev_modules.cl_img_install.get_primary_slot_num')
@mock.patch('dev_modules.cl_img_install.get_active_slot')
@mock.patch('dev_modules.cl_img_install.get_slot_version')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_get_slot_info(mock_module,
                       mock_get_slot_ver,
                       mock_active_ver,
                       mock_primary_ver):
    instance = mock_module.return_value
    mock_get_slot_ver.side_effect = {'1': '2.0.3', '2': '2.0.10'}
    mock_active_ver.return_value = '1'
    mock_primary_ver.return_value = '2'
    result_slot_values = {
        '1': {'active': True, 'version': '1'},
        '2': {'primary': True, 'version': '2'}
    }
    assert_equals(get_slot_info(instance), result_slot_values)


@mock.patch('dev_modules.cl_img_install.switch_slot')
@mock.patch('dev_modules.cl_img_install.get_slot_info')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_check_sw_version(mock_module, mock_get_slot_info, mock_switch_slot):
    instance = mock_module.return_value
    # switch_slots = yes , version found in alternate slots
    instance.params.get.return_value = True
    slot_values = {
        '1': {'version': '2.0.10', 'primary': True},
        '2': {'version': '2.0.3',  'active': True}
    }
    mock_get_slot_info.return_value = slot_values
    instance.sw_version = '2.0.10'
    check_sw_version(instance)
    _msg = 'Version 2.0.10 is installed in the alternate slot. ' +\
        'Next reboot, switch will load 2.0.10.'
    instance.exit_json.assert_called_with(msg=_msg, changed=True)

    # switch slot = no , version found in alternate slot
    instance.params.get.return_value = False
    instance.sw_version = '2.0.10'
    check_sw_version(instance)
    _msg = 'Version 2.0.10 is installed in the alternate slot. ' +\
        'switch_slot set to "no". No further action to take'
    instance.exit_json.assert_called_with(msg=_msg, changed=False)

    # switch_slot = yes code in active slot
    slot_values = {
        '1': {'version': '2.0.10'},
        '2': {'version': '2.0.3',  'primary': True, 'active': True}
    }
    mock_get_slot_info.return_value = slot_values
    instance.params.get.return_value = True
    instance.sw_version = '2.0.3'
    check_sw_version(instance)
    _msg = 'Version 2.0.3 is installed in the active slot'
    instance.exit_json.assert_called_with(msg=_msg, changed=False)

    # switch_slot = no , code in active slot
    instance.params.get.return_value = False
    instance.sw_version = '2.0.3'
    check_sw_version(instance)
    _msg = 'Version 2.0.3 is installed in the active slot'
    instance.exit_json.assert_called_with(msg=_msg, changed=False)

    # switch_slot = no, code in alternate slot
    slot_values = {
        '1': {'version': '2.0.10', 'active': True},
        '2': {'version': '2.0.3',  'primary': True}
    }
    mock_get_slot_info.return_value = slot_values
    instance.sw_version = '2.0.3'
    check_sw_version(instance)
    instance.exit_json.assert_called_with(
        msg='Version 2.0.3 is installed in the alternate slot. ' +
        'switch_slot set to "no". No further action to take', changed=False)

    instance.params.get.return_value = True
    check_sw_version(instance)
    instance.exit_json.assert_called_with(
        msg='Version 2.0.3 is installed in the alternate slot. ' +
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
    instance.params.get.side_effect = mod_args_generator(arg_values)
    main()
    mock_module.assert_called_with(
        argument_spec={'src': {'required': True, 'type': 'str'},
                       'version': {'type': 'str'},
                       'switch_slot':  {
                           'type': 'bool',
                           'default': False,
                           'choices': ['yes', 'on', '1',
                                       'true', 1, 'no',
                                       'off', '0', 'false', 0]}})


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
    instance.params.get.side_effect = mod_args_generator(arg_values)
    instance.sw_version = '2.0.3'
    install_img(instance)
    cmd = '/usr/cumulus/bin/cl-img-install -f %s' % \
        (arg_values.get('src'))
    mock_run_cl_cmd.assert_called_with(instance, cmd)
    instance.exit_json.assert_called_with(
        msg='Cumulus Linux Version 2.0.3 ' +
        'successfully installed in alternate slot',
        changed=True)
    # test using when switching slots
    values = arg_values.copy()
    values['switch_slot'] = True
    instance.params.get.side_effect = mod_args_generator(values)
    mock_get_slot_info.return_value = {'1': {'version': '2.0.2',
                                             'active': True,
                                             'primary': True},
                                       '2': {'version': '2.0.3'}}
    instance.sw_version = '2.0.3'
    install_img(instance)
    assert_equals(mock_switch_slot.call_count, 1)


@mock.patch('dev_modules.cl_img_install.run_cl_cmd')
@mock.patch('dev_modules.cl_img_install.AnsibleModule')
def test_switch_slot(mock_module, mock_run_cl_cmd):
    """
    Test switching slots
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args_generator(
        {'switch_slot': 'no'})
    switch_slot(instance, 1)
    assert_equals(mock_run_cl_cmd.call_count, 0)

    instance.params.get.side_effect = mod_args_generator(
        {'switch_slot': True})
    switch_slot(instance, '1')
    runcmd = '/usr/cumulus/bin/cl-img-select 1'
    mock_run_cl_cmd.assert_called_with(instance, runcmd)
