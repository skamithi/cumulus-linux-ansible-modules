#!/usr/bin/env python
#
# Copyright (C) 2014, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_prefix_check
author: Sean Cavanaugh sean@cumulusnetworks.com
short_description: Check to see if route/prefix exists
description:
    - Check to see if a route exists. This module can be used simply \
to check a route and return if its present or absent. \
A larger timeout can be provided to check if a route disappears.  \
An example would be the user could change the OSPF cost \
of a node within the network then utilize cl_prefix_check \
of another (separate) node to verify the node \
(where the OSPF cost was changed) is not being use to  \
route traffic.
options:
    prefix:
        description:
            - route/prefix that module is checking for. Uses format \
acceptable to "ip route show" command. See manpage of "ip-route" for more details
        required: true
    state:
        description:
            - Describes if the prefix should be present.\
        choices: ['present', 'absent']
        default: ['present']
    timeout:
        description:
            - timeout for route to disappear, number of loops
        default: 5
    poll_interval:
        description:
            - interval to check in seconds
        default: 1

notes:
    - IP Route Documentation - [ add later ]\
    - Contact Cumulus Networks @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
Example playbook entries using the cl_prefix_check \
module to check if a prefix exists

    tasks:
    - name:  Test if prefix is present.
      cl_prefix_check: prefix=4.4.4.0/24

    - name: Test if route is absent. poll for 200 seconds. Poll interval \
at default setting of 1 second
      cl_prefix_check: prefix=10.0.1.0/24 timeout=200 state=absent

    - name: Test if route is present, with a timeout of 10 seconds and poll \
interval of 2 seconds
      cl_prefix_check: prefix=10.1.1.0/24 timeout=10 poll_interval=2

'''


def run_cl_cmd(module, cmd, check_rc=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret[:-1]
def route_is_present(result):
    if len(result) > 0:
        return True

def route_is_absent(result):
    if len(result) == 0:
        return True

def loop_route_check(module):

    prefix = module.params.get('prefix')
    state = module.params.get('state')
    timeout = int(module.params.get('timeout'))
    poll_interval = int(module.params.get('poll_interval'))

    # using ip route show instead of ip route get
    # because ip route show will be blank if the exact prefix
    # is missing from the table. ip route get tries longest prefix
    # match so may match default route.
    # command returns empty array if prefix is missing
    cl_prefix_cmd = '/sbin/ip route show %s' % (prefix)
    time_elapsed = 0
    while True:
        result = run_cl_cmd(module, cl_prefix_cmd)
        if state == 'present' and route_is_present(result):
            return True
        if state == 'absent' and route_is_absent(result):
            return True
        time.sleep(poll_interval)
        time_elapsed += poll_interval
        if time_elapsed == timeout:
            return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            prefix=dict(required=True, type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent']),
            timeout=dict(default=2, type='int'),
            poll_interval=dict(default=1, type='int'),

        ),
    )

    _state = module.params.get('state')
    _timeout = module.params.get('timeout')
    _msg = "testing whether route is %s. " % (_state)

    if loop_route_check(module):
        _msg += 'Condition meet'
        module.exit_json(_msg, changed=True)
    else:
        _msg += 'Condition not met %s second timer expired' % (_timeout)
        module.exit_json(_msg, changed=False)

# import module snippets
from ansible.module_utils.basic import *
import time
# from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
