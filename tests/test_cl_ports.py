import mock
from nose.tools import set_trace
import dev_modules.cl_ports as cl_ports
from asserts import assert_equals


@mock.patch('dev_modules.cl_ports.make_copy_of_orig_ports_conf')
@mock.patch('dev_modules.cl_ports.write_to_ports_conf')
@mock.patch('dev_modules.cl_ports.hash_existing_ports_conf')
@mock.patch('dev_modules.cl_ports.generate_new_ports_conf_hash')
@mock.patch('dev_modules.cl_ports.compare_new_and_old_port_conf_hash')
@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_module_args(mock_module,
                     mock_compare,
                     mock_generate,
                     mock_existing,
                     mock_write,
                     mock_copy):
    """ cl_ports - Test module argument specs"""
    cl_ports.main()
    mock_module.assert_called_with(
        argument_spec={'speed_10g': {'type': 'list'},
                       'speed_40g': {'type': 'list'},
                       'speed_40g_div_4': {'type': 'list'},
                       'speed_4_by_10g': {'type': 'list'}},
        required_one_of=[['speed_40g_div_4',
                          'speed_4_by_10g',
                          'speed_10g',
                          'speed_40g']]
    )


@mock.patch('dev_modules.cl_ports.make_copy_of_orig_ports_conf')
@mock.patch('dev_modules.cl_ports.write_to_ports_conf')
@mock.patch('dev_modules.cl_ports.hash_existing_ports_conf')
@mock.patch('dev_modules.cl_ports.generate_new_ports_conf_hash')
@mock.patch('dev_modules.cl_ports.compare_new_and_old_port_conf_hash')
@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_basic_integration_test(mock_module,
                                mock_compare,
                                mock_generate,
                                mock_existing,
                                mock_write,
                                mock_copy):
    """ test module results when comparing old and new config """
    # ports.conf has changed
    instance = mock_module.return_value
    mock_compare.return_value = True
    cl_ports.main()
    instance.exit_json.assert_called_with(
        msg='/etc/cumulus/ports.conf changed', changed=True)

    # ports.conf not changed
    mock_compare.return_value = False
    cl_ports.main()
    instance.exit_json.assert_called_with(
        msg='No change in /etc/ports.conf', changed=False)


@mock.patch('dev_modules.cl_ports.os.path.exists')
@mock.patch('dev_modules.cl_ports.shutil.copyfile')
def test_make_copy_of_orig_ports_conf(mock_copy_file,
                                      mock_exists):
    # ports.conf.orig exists.
    mock_exists.return_value = True
    cl_ports.make_copy_of_orig_ports_conf()
    assert_equals(mock_copy_file.call_count, 0)
    mock_exists.assert_called_with('/etc/cumulus/ports.conf.orig')

    # ports.conf does not exist
    mock_exists.return_value = False
    cl_ports.make_copy_of_orig_ports_conf()
    mock_copy_file.assert_called_with(
        '/etc/cumulus/ports.conf', '/etc/cumulus/ports.conf.orig')


@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_compare_new_and_old_port_conf_hash(mock_module):
    """ test comparing existing and new ports.conf config """
    instance = mock_module.return_value
    instance.ports_conf_hash = {1: '40G',
                                2: '40G',
                                3: '10G'}
    # test and see if doing this out of order makes a difference
    instance.new_ports_hash = {3: '4x10G', 1: '10G'}
    result = cl_ports.compare_new_and_old_port_conf_hash(instance)
    assert_equals(result, True)


@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_write_to_ports_conf(mock_module):
    """ test writing to ports.conf file """
    test_port_conf = './tests/write_to_ports_conf'
    lf = open(test_port_conf, 'w')
    instance = mock_module.return_value
    instance.ports_conf_hash = {1: '40G',
                                10: '10G',
                                22: '4x10G',
                                2: '40/4'}
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = lf
        cl_ports.write_to_ports_conf(instance)
    lf.close()
    result = open(test_port_conf, 'r').readlines()
    mock_open.assert_called_with('/etc/cumulus/ports.conf', 'w')
    assert_equals(result[0].strip(), '# Managed By Ansible')
    result.pop(0)
    assert_equals(map(lambda x: x.strip(), result),
                  ['1=40G', '2=40/4', '10=10G', '22=4x10G'])


@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_compare_new_and_old_port_conf_hash_idempotent(mock_module):
    """ test comparing existing and new ports.conf config """
    instance = mock_module.return_value
    instance.ports_conf_hash = {1: '40G',
                                2: '40G',
                                3: '10G'}
    instance.new_ports_hash = {1: '40G', 3: '10G'}
    result = cl_ports.compare_new_and_old_port_conf_hash(instance)
    assert_equals(result, True)


@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_generate_new_ports_conf_hash(mock_module):
    """ test generating ports_conf hash based on user added params """
    instance = mock_module.return_value
    instance.params = {
        'speed_40g': ['swp1-2', 'swp5'],
        'speed_4_by_10g': ['swp7-8'],
        'speed_40g_div_4': ['swp9'],
        'speed_10g': ['swp10']
    }
    cl_ports.generate_new_ports_conf_hash(instance)
    assert_equals(instance.new_ports_hash, {1: '40G',
                                            2: '40G',
                                            5: '40G',
                                            7: '4x10G',
                                            8: '4x10G',
                                            9: '40G/4',
                                            10: '10G'})


@mock.patch('dev_modules.cl_ports.os.path.exists')
@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_hash_existing_ports_conf_doesntwork(mock_module, mock_exists):
    """ test missing ports.conf """
    instance = mock_module.return_value
    mock_exists.return_value = False
    assert_equals(cl_ports.hash_existing_ports_conf(instance), False)
    instance.fail_json.assert_called_with(
        msg='/etc/cumulus/ports.conf is missing', changed=False)


@mock.patch('dev_modules.cl_ports.os.path.exists')
@mock.patch('dev_modules.cl_ports.AnsibleModule')
def test_hash_existing_ports_conf_works(mock_module, mock_exists):
    """ test putting ports.conf values into a hash """
    # create ansiblemodule mock instance
    instance = mock_module.return_value
    # say that ports.conf exists
    mock_exists.return_value = True
    lf = open('tests/ports.conf')
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = lf
        cl_ports.hash_existing_ports_conf(instance)
        mock_exists.assert_called_with('/etc/cumulus/ports.conf')
        assert_equals(instance.ports_conf_hash[1], '40G')
        assert_equals(instance.ports_conf_hash[11], '4x10G')
