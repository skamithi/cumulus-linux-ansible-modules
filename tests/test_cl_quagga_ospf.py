import mock
from mock import MagicMock
from nose.tools import set_trace
from dev_modules.cl_quagga_ospf import check_dsl_dependencies, main, \
    has_interface_config
from asserts import assert_equals


@mock.patch('dev_modules.cl_quagga_ospf.check_dsl_dependencies')
@mock.patch('dev_modules.cl_quagga_ospf.AnsibleModule')
def test_check_mod_args(mock_module,
                        mock_check_dsl_dependencies):
    """
    cl_quagga_ospf - check mod args
    """
    instance = mock_module.return_value
    instance.params.get.return_value = MagicMock()
    main()
    mock_module.assert_called_with(argument_spec={
        'router_id': {'type': 'str'},
        'area': {'default': '0', 'type': 'str'},
        'anchor_int': {'type': 'str'},
        'reference_bandwidth': {
            'default': '40000',
            'type': 'str'
        },
        'saveconfig': {
            'default': False,
            'choices': ['yes', 'on', '1', 'true',
                        1, 'no', 'off', '0',
                        'false', 0]},
        'state': {'type': 'str', 'choices': ['present', 'absent']},
        'cost': {'type': 'str'}, 'interface': {'type': 'str'},
        'point2point': {'default': False,
                        'choices': ['yes', 'on', '1',
                                    'true', 1, 'no',
                                    'off', '0', 'false', 0]}},
        mutually_exclusive=[
            ['reference_bandwidth', 'interface'],
            ['router_id', 'interface']]
    )
    assert_equals(mock_check_dsl_dependencies.call_args_list[0],
                  mock.call(instance, ['cost', 'state', 'area',
                                       'point2point', 'anchor_int', 'passive'],
                            'interface', 'swp1'))
    assert_equals(mock_check_dsl_dependencies.call_args_list[1],
                  mock.call(instance, ['interface'], 'area', '0.0.0.0'))


@mock.patch('dev_modules.cl_quagga_ospf.AnsibleModule')
def test_has_int_config(mock_module):
    instance = mock_module.return_value
    instance.params = { 'interface': '', 'state': '' }
    assert_equals(has_interface_config(instance), True)
    instance.params = { 'state': '' }
    assert_equals(has_interface_config(instance), False)


def check_dsl_args(arg):
    values = {
        'cost': None,
        'state':  None,
        'point2point': 'yes',
        'anchor_int': None,
        'interface': None,
    }
    return values[arg]


@mock.patch('dev_modules.cl_quagga_ospf.AnsibleModule')
def test_check_dsl_dependencies(mock_module):
    instance = mock_module.return_value
    instance.params.get.side_effect = check_dsl_args
    _input_options = ['point2point', 'cost']
    _depends = 'interface'
    check_dsl_dependencies(instance, _input_options, _depends, 'swp1')
    instance.fail_json.assert_called_with(
        msg="incorrect syntax. point2point must have an " +
        "interface option. Example 'cl_quagga_ospf: interface=swp1 " +
        "point2point=yes'"
    )
