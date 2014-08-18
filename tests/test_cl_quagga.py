import mock
from nose.tools import set_trace
from dev_modules.cl_quagga import main
from asserts import assert_equals


def mod_args(arg):
    values = {
        'protocols': 'ospf',
        'state': 'restarted'
    }
    return values[arg]


@mock.patch('dev_modules.cl_quagga.AnsibleModule')
def test_module_args(mock_module):
    """ cl_quagga - Test module argument specs"""
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    main()
    mock_module.assert_called_with(
        argument_spec={'state':
                       {'type': 'str', 'choices':
                        ['stopped', 'started', 'restarted']},
                       'protocols': {'type': 'str'}})

