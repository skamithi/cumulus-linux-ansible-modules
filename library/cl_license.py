#!/usr/bin/env python
#
# Copyright (C) 2015, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_license
author: Cumulus Networks
short_description: Install Cumulus Linux license
description:
    - Installs a Cumulus Linux license. The module reports no change of status \
when a license is installed. If you attempt to install a different license,  \
this will fail. To install a new license, use the "force=yes" option. \
For more details go the Cumulus Linux License Documentation @ \
http://docs.cumulusnetwork.com
notes:
    - to activate a license, the switchd service must be restarted. \
This action is disruptive. See EXAMPLES, for the proper way to issue this notify action.
options:
    src:
        description:
            - full path to the license. Can be local path or http url
        required: true
    force:
        description:
            - force installation of the license. This does not active the new \
license. It overwrites the existing license.
        choices: ['yes', 'no']
        default: 'no'
'''
EXAMPLES = '''
Example playbook using the cl_license module to manage \
licenses on Cumulus Linux

## Install a license. Note that the license install task is placed in a separate "hosts" block.
## This is to ensure that switchd restarts before configuring the interfaces. You could also
## perform this task using "register" variables, as shown in  http://bit.ly/1EpQQzd. But this
## can get cumbersome.

---
   - hosts: all
     tasks:
       - name: install license using http url
         cl_license: src='http://10.1.1.1/license.txt'
         notify: restart switchd
       - name: Triggers switchd to be restarted right away, before play, or role is over. This is desired behaviour
         meta: flush_handlers
       - name: configure interfaces
         template: src=interfaces.j2 dest=/etc/network/interfaces
         notify: restart networking

     handlers:
       - name: restart switchd
         service: name=switchd state=restarted
       - name: restart networking
         service: name=networking state=reloaded

'''


# handy helper for calling system calls.
# calls AnsibleModule.run_command and prints a more appropriate message
# exec_path - path to file to execute, with all its arguments.
# E.g "/sbin/ip -o link show"
# failure_msg - what message to print on failure
def run_cmd(module, exec_path):
    (_rc, out, _err) = module.run_command(exec_path)
    if _rc > 0:
        failure_msg = "Failed; %s Error: %s" % (exec_path, _err)
        module.fail_json(msg=failure_msg)
    else:
        return out

def license_installed(module):
    """
    check if the license is installed. if True, then license is installed
    """
    if module.params.get('force') is True:
        return False
    try:
        return cumulus_license_present
    except NameError:
        _err_msg = "Add the 'cumulus_facts' before running cl-license." + \
                " Check the cl_license documentation for an example"
        module.fail_json(msg=_err_msg)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            force=dict(type='bool', choices=BOOLEANS, default=False)
        ),
    )


    if not license_installed(module):
        run_cmd(module, '/tmp/ce-lic-wrapper')
        module.changed = True
        module.msg = "License installed"
    else:
        module.changed = False
        module.msg = "License exists"

    module.exit_json(changed=module.changed, msg=module.msg)


# import module snippets
from ansible.module_utils.basic import *
# from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
