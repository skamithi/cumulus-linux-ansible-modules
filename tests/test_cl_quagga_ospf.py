import mock
from mock import MagicMock
from nose.tools import set_trace
from dev_modules.cl_quagga_ospf import check_dsl_dependencies, main
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
        msg="incorrect syntax. point2point must have an " +\
        "interface option. Example 'cl_quagga_ospf: interface=swp1 " + \
        "point2point=yes'"
    )
