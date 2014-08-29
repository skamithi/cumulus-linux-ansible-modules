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
    - Check to see if a route exists. This module can be used simply to check a route \
    and return if its present or absent. A larger timeout can be provided to check  \
    if a route disappears.  An example would be the user could change the OSPF cost \
    of a node within the network then utilize cl_prefix_check of another (separate) \
    node to verify the node (where the OSPF cost was changed) is not being use to  \
    route traffic.
options:
    prefix:
        description:
            - route/prefix that module is checking for.
        required: true
    state:
        description:
            - Describes if the prefix should be present.\
        choices: ['present', 'absent']
        default: ['present']
    timeout:
        description:
            - timeout for route to disappear, number of loops
        default: 2
    timeout:
        description:
            - interval to check in seconds
        default: 1

notes:
    - License Documentation - http://cumulusnetworks.com/docs/2.1/quick-start/quick-start.html
    - Contact Cumulus Networks @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
Example playbook entries using the cl_prefix_check module to check if a prefix exists

    tasks:
    - name: install license using http url
      cl_prefix_check: prefix:4.4.4.4

    - name: install license from local filesystem
      cl_prefix_check: prefix:10.0.1.1 timeout:200 state=absent

    - name: install license from local filesystem restart switchd
      cl_prefix_check: prefix:1.2.3.4 timeout:10 interval:2 
'''


def run_cl_cmd(module, cmd, check_rc=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret[:-1]
    
def loop_route_check(module, cmd, prefix, state, timeout, interval, check_rc=True):
	if state == 'present':
		return_state = "false"
	elif state == 'absent':
		return_state = "true"
	else:
		module.fail_json(msg=e.strerror)
		
	cl_prefix_cmd = ('ip route show %s') % (prefix)
	while(1):
    	run_cl_cmd(module, cl_prefix_cmd)
    	if prefix in out and state == 'present':
	   		return_state = "true"
	   		break
		if prefix not in out and state == 'absent':
			return_state = "false"
			break
		if timeout == 200:
			print "timeout"
			break
	   timeout = timeout + 1 
	   sleep(interval)
	return return_state  

def main():
    module = AnsibleModule(
        argument_spec=dict(
            prefix=dict(required=True, type='str'),
            state=dict(default=present, type='str',
                       choices=['present', 'absent']),
            timeout=dict(default='2', type='str'),   
            interval=dict(default='1', type='str'),                     

        ),
    )

    prefix = module.params.get('prefix')
    state = module.params.get('state')
    timeout = module.params.get('timeout')
    interval = module.params.get('interval')

    _changed = False
    _msg = ""
    
    
	return_value = loop_route_check(module, cmd, prefix, state, timeout, interval)
    
    
    
    if state == 'present':
        if return_value == 'present':
            _msg = 'route was found successfully'
        elif return_value == 'absent':
            _msg = 'unsuccessful in finding route'
            module.fail_json(msg=_msg)
        else:
        	_msg = 'unexpected value, state=present, return_value = unknown
        	module.fail.json(msg=_msg)
	elif state == 'absent'
        if return_value == 'present':
            _msg = 'route was still found, unsuccessful removal'
            module.fail_json(msg=_msg)
        elif return_value == 'absent':
            _msg = 'route was successfully removed'
        else:
        	_msg = 'unexpected value, state=absent, return_value = unknown
        	module.fail.json(msg=_msg)	
	
        	
    module.exit_json(changed=_changed, msg=_msg)


# import module snippets
from ansible.module_utils.basic import *
# from ansible.module_utils.urls import *
import time

if __name__ == '__main__':
    main()
