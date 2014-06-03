#!/usr/bin/env python
#
# Copyright (C) 2014, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_install_img
author: Stanley Karunditu
short_description: Install a different Cumulus Linux version.
description:
    - install a different version of Cumulus Linux in the inactive slot
options:
    version:
        description:
            - cumulus linux version to install
        required: true
    src:
        description:
            - full path to binary image. Can be a local path, http or https URL
        required: true
    reboot:
        description:
            - reboot the switch
        choices: ['yes', 'no']
        default: 'no'
notes:
    - Image Management Documentation - http://cumulusnetworks.com/docs/2.0/user-guide/system_management_diagnostics/img-mgmt.html#upgrade
    - Contact Cumulus Networks @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
Example playbook entries using the cl_img_install module

    tasks:
    - name: install image using using http url
      cl_img_install: version=2.0.1 src='http://10.1.1.1/CumulusLinux-2.0.1.bin'

    - name: install license from local filesystem
      cl_img_install: version=2.0.1 src='/root/CumulusLinux-2.0.1.bin'

'''


def run_cl_cmd(module, cmd, check_rc=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret[:-1]

def get_switch_version():

def install_img(module):

def reboot_switch(module):
def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            reboot=dict(default='no', choices=["yes", "no"])
        ),
    )

    install_img(module)

    reboot_switch(module)




# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
