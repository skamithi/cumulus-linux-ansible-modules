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
    - to activate a license, the switchd service must be restarted. \
This action is disruptive. See EXAMPLES, for the proper way to issue this notify action.
options:
    src:
        description:
            - full path to the license. Can be local path or http url
        required: true
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
       - name: grab cumulus facts. has licensing info
         cumulus_facts

       - name: install license using http url
         cl_license: src='http://10.1.1.1/license.txt'
         notify: restart switchd
         when: cumulus_license_present == False

       - name: Triggers switchd to be restarted right away, before play, or role is over. This is desired behaviour
         meta: flush_handlers
         when: cumulus_license_present == False

       - name: configure interfaces
         template: src=interfaces.j2 dest=/etc/network/interfaces
         notify: restart networking

     handlers:
       - name: restart switchd
         service: name=switchd state=restarted
       - name: restart networking
         service: name=networking state=reloaded

'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str')
        ),
    )

    _url = '/tmp/ce-lic-wrapper -e -i %s' % module.params.get('src')
    (_rc, out, _err) = module.run_command(_url)
    if _rc > 0:
        module.fail_json(msg=_err)
    module.msg = "License installed"
    module.exit_json(changed=module.changed, msg=module.msg)


# import module snippets
from ansible.module_utils.basic import *
# from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
