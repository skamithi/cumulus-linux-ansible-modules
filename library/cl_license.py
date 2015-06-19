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
when a license is installed. \
For more details go the Cumulus Linux License Documentation @ \
http://docs.cumulusnetwork.com
notes:
    - to activate a license for the FIRST time, the switchd service must be restarted. \
This action is disruptive. The license renewal process occurs via the \
Cumulus Networks Customer Portal - http://customers.cumulusnetworks.com
    - a non-EULA license is required for automation. \
Manually install the license \
using the command "cl-license -i <license_file> " to confirm the license is a Non-EULA license.

See EXAMPLES, for the proper way to issue this notify action. \
References: \
https://support.cumulusnetworks.com/hc/en-us/sections/200507688
options:
    src:
        description:
            - full path to the license. Can be local path or http url
    force:
        description:
            - force installation of a license. Typically not needed. \
It is recommended to manually run this \
command via the ansible command. A reload of switchd is not required.

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

       - name: Triggers switchd to be restarted right away, \
before play, or role is over. This is desired behaviour
         meta: flush_handlers

       - name: configure interfaces
         template: src=interfaces.j2 dest=/etc/network/interfaces
         notify: restart networking

     handlers:
       - name: restart switchd
         service: name=switchd state=restarted
       - name: restart networking
         service: name=networking state=reloaded

----

# Force all switches to accept a new license. Typically not needed
ansible -m cl_license -a "src='http://10.1.1.1/new_lic' force=yes"  -u root all

----

'''

CL_LICENSE_PATH='/usr/cumulus/bin/cl-license'

def install_license(module):
    # license is not installed, install it
        _url = module.params.get('src')
        (_rc, out, _err) = module.run_command("%s -i %s" % (CL_LICENSE_PATH, _url))
        if _rc > 0:
            module.fail_json(msg=_err)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str')
        ),
    )

    # check if license is installed
    (_rc, out, _err) = module.run_command(CL_LICENSE_PATH)
    if _rc == 0:
        module.msg = "No change. License already installed"
        module.changed = False
    else:
        install_license(module)
        module.msg = "License installation completed"
        module.changed = True
    module.exit_json(changed=module.changed, msg=module.msg)


# import module snippets
from ansible.module_utils.basic import *
# from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
