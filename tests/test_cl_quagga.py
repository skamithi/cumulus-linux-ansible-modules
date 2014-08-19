import mock
from nose.tools import set_trace
from dev_modules.cl_quagga import main, convert_to_yes_or_no
from asserts import assert_equals


def mod_args(arg):
    values = {'name': 'ospfd',
              'state': 'present'}
    return values[arg]

@mock.patch('dev_modules.cl_quagga.check_setting')
@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_module_args(mock_module,
                     mock_check_setting):
    """ cl_quagga - Test module argument specs"""
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    main()
    mock_module.assert_called_with(
        argument_spec={'name':
                       {'type': 'str', 'choices':
                        ['ospfd', 'ospf6d', 'bgp'],
                        'required': True},
                       'state': {'type': 'str',
                                 'choices': ['present', 'absent'],
                                 'required': True}
                       })


def test_convert_to_yes_or_no():
    """
    cl_quagga - convert state from present/absent to yes/no
    """
    state = 'absent'
    assert_equals(convert_to_yes_or_no(state), 'no')
    state = 'present'
    assert_equals(convert_to_yes_or_no(state), 'yes')
