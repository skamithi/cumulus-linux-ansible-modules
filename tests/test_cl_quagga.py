import mock
from nose.tools import set_trace
from dev_modules.cl_quagga import main, create_new_quagga_file, \
    check_quagga_services_setting, check_protocol_options, \
    copy_quagga_service_file
from asserts import assert_equals


@mock.patch('dev_modules.cl_quagga.copy')
@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_copy_quagga_service_file(mock_module, mock_copy):
    instance = mock_module.return_value
    instance.quagga_daemon_file = '/etc/quagga/daemons'
    instance.tmp_quagga_file = '/tmp/quagga_daemons'
    copy_quagga_service_file(instance)
    mock_copy.assert_called_with('/tmp/quagga_daemons',
                                 '/etc/quagga/daemons')


def mod_args(arg):
    values = {
        'protocols': 'ospf',
        'state': 'restarted'
    }
    return values[arg]

@mock.patch('dev_modules.cl_quagga.copy_quagga_service_file')
@mock.patch('dev_modules.cl_quagga.check_quagga_services_setting')
@mock.patch('dev_modules.cl_quagga.create_new_quagga_file')
@mock.patch('dev_modules.cl_quagga.check_protocol_options')
@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_module_args(mock_module,
                     mock_check_protocol,
                     mock_create_new_quagga_file,
                     mock_get_existing_quagga_services,
                     mock_copy_quagga_service_file):
    """ cl_quagga - Test module argument specs"""
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    main()
    mock_module.assert_called_with(
        argument_spec={'state':
                       {'type': 'str', 'choices':
                        ['stopped', 'started', 'restarted']},
                       'protocols': {'type': 'list'}})
    assert_equals(instance.quagga_daemon_file, '/etc/quagga/daemons')
    assert_equals(instance.tmp_quagga_file, '/tmp/quagga_daemons')


@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_create_new_quagga_file(mock_module):
    instance = mock_module.return_value
    filename = '/tmp/test'
    instance.tmp_quagga_file = filename
    # only ospfv2
    instance.params.get.return_value = ['ospf']
    create_new_quagga_file(instance)
    _lines = open(filename).readlines()
    assert_equals(_lines[0], '#created using ansible\n')
    assert_equals(_lines[2], 'zebra=yes\n')
    assert_equals(_lines[3], 'ospf=yes\n')
    # ospfv2 and ospfv3
    instance.params.get.return_value = ['ospf6d', 'ospf']
    create_new_quagga_file(instance)
    _lines = open(filename).readlines()
    assert_equals(_lines[3], 'ospf6d=yes\n')
    assert_equals(_lines[4], 'ospf=yes\n')
    # install bgp only
    instance.params.get.return_value = ['bgp']
    create_new_quagga_file(instance)
    _lines = open(filename).readlines()
    assert_equals(_lines[3], 'bgp=yes\n')


@mock.patch('dev_modules.cl_quagga.cmp')
@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_check_quagga_services_setting(mock_module,
                                       mock_cmp):
    instance = mock_module.return_value
    # if file comparison is true
    mock_cmp.return_value = True
    check_quagga_services_setting(instance)
    assert_equals(instance.exit_json.call_count, 0)
    # if file comparison is false - files don't match
    mock_cmp.return_value = False
    check_quagga_services_setting(instance)
    instance.exit_json.assert_called_with(
        msg='Desired quagga routing protocols already configured',
        changed=False
    )


@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_check_protocol_options(mock_module):
    instance = mock_module.return_value
    # protocol options are correct
    instance.params.get.return_value = ['ospfd', 'bgpd']
    check_protocol_options(instance)
    assert_equals(instance.fail_json.call_count, 0)
    # protocol option is incorrect
    instance.params.get.return_value = ['ospfd', 'ripd']
    check_protocol_options(instance)
    instance.fail_json.assert_called_with(msg="protocols options are " +
                                          "'ospfd, ospf6d, bgpd'." +
                                          " option used was ripd")
