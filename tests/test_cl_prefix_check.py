import mock
from nose.tools import set_trace
from library.cl_prefix_check import main, loop_route_check
from asserts import assert_equals


global_values = {
    'prefix': '1.1.1.1/24',
    'poll_interval': '1',
    'timeout': '2',
    'state': 'present',
    'nexthop': '1.2.3.4',
    'nonexthop': '1.2.3.4'
}


def mod_args_generator(values, *args):
    newvalues = global_values.copy()
    newvalues.update(values)

    def mod_args(args):
        return newvalues[args]
    return mod_args


@mock.patch('library.cl_prefix_check.loop_route_check')
@mock.patch('library.cl_prefix_check.AnsibleModule')
def test_module_args(mock_module,
                     mock_loop_route_check):
    """
    cl_prefix_check - test module arguments
    """
    instance = mock_module.return_value
    values = {'nexthop': '1.1.1.1'}
    instance.params.get.side_effect = mod_args_generator(values)
    main()
    mock_module.assert_called_with(
        argument_spec={'prefix': {'required': True, 'type': 'str'},
                       'poll_interval': {'type': 'int', 'default': 1},
                       'timeout': {'type': 'int', 'default': 2},
                       'state': {'type': 'str',
                                 'default': 'present',
                                 'choices': ['present', 'absent']},
                       'nexthop': {'type': 'str', 'default': ''},
                       'nonexthop': {'type': 'str', 'default': ''}
                       })


@mock.patch('library.cl_prefix_check.loop_route_check')
@mock.patch('library.cl_prefix_check.AnsibleModule')
def test_printing_module_exit_msg_loop_passed(mock_module,
                                              mock_loop_route_check):
    """
    cl_prefix_check - test exit_json messages when loop check is true or false
    """
    instance = mock_module.return_value
    values = {'nexthop': '2.2.2.2'}
    instance.params.get.side_effect = mod_args_generator(values)
    # loop check is true, i.e condition is matched
    mock_loop_route_check.return_value = True
    main()
    _msg = 'Testing whether route is present. Condition Met'
    instance.exit_json.assert_called_with(msg=_msg, changed=False)
    # loop check is false, i.e condition is not matched
    mock_loop_route_check.return_value = False
    main()
    _msg = 'paremeters not found'
    instance.fail_json.assert_called_with(msg=_msg)


def mock_loop_check_arg(arg):
    values = {
        'prefix': '10.1.1.1/24',
        'state': 'present',
        'timeout': '10',
        'poll_interval': '2',
        'nexthop': '',
        'nonexthop': ''
    }
    return values[arg]


def mock_loop_check_arg_absent(arg):
    values = {
        'prefix': '10.1.1.1/24',
        'state': 'absent',
        'timeout': '10',
        'poll_interval': '2',
        'nexthop': '',
        'nonexthop': ''
    }
    return values[arg]


@mock.patch('library.cl_prefix_check.run_cl_cmd')
@mock.patch('library.cl_prefix_check.AnsibleModule')
def test_loop_route_check_state_present(mock_module,
                                        mock_run_cl_cmd):
    """
    cl_prefix_check - state is present route is present
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mock_loop_check_arg
    # run_cl_cmd returns an array if there is match
    # returns any empty array if nothing is found.
    mock_run_cl_cmd.return_value = ['something']
    # state is present, route is found
    assert_equals(loop_route_check(instance), True)


@mock.patch('library.cl_prefix_check.run_cl_cmd')
@mock.patch('library.cl_prefix_check.AnsibleModule')
def test_loop_route_check_state_absent(mock_module,
                                       mock_run_cl_cmd):
    """
    cl_prefix_check - state is absent route is absent should return True
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mock_loop_check_arg_absent
    # run_cl_cmd returns an array if there is match
    # returns any empty array if nothing is found.
    mock_run_cl_cmd.return_value = []
    # state is present, route is found
    assert_equals(loop_route_check(instance), True)


@mock.patch('library.cl_prefix_check.time.sleep')
@mock.patch('library.cl_prefix_check.run_cl_cmd')
@mock.patch('library.cl_prefix_check.AnsibleModule')
def test_loop_route_check_state_absent_route_present(mock_module,
                                                     mock_run_cl_cmd,
                                                     mock_sleep):
    """
    cl_prefix_check - state is absent route is absent should return True
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mock_loop_check_arg_absent
    # run_cl_cmd returns an array if there is match
    # returns any empty array if nothing is found.
    mock_run_cl_cmd.return_value = ['something']
    # state is present, route is found
    assert_equals(loop_route_check(instance), False)
    # test command that outputs route
    mock_run_cl_cmd.assert_called_with(instance,
                                       '/sbin/ip route show 10.1.1.1/24')


@mock.patch('library.cl_prefix_check.time.sleep')
@mock.patch('library.cl_prefix_check.run_cl_cmd')
@mock.patch('library.cl_prefix_check.AnsibleModule')
def test_loop_route_check_state_present_route_failed(mock_module,
                                                     mock_run_cl_cmd,
                                                     mock_sleep):

    """
    cl_prefix_check - state is present route is not present, timeout occurs
    """
    # state is present, object is not found
    # function takes 10 seconds to run. Difficult to
    # test timers in nose..havent found a good way yet
    instance = mock_module.return_value
    instance.params.get.side_effect = mock_loop_check_arg
    mock_run_cl_cmd.return_value = []
    assert_equals(loop_route_check(instance), False)
    # test sleep ! figured it out
    # sleep should be called 5 times with a poll
    # interval of 2
    assert_equals(mock_sleep.call_count, 5)
    mock_sleep.assert_called_with(2)
