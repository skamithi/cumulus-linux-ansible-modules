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

def check_url(module, url):
    parsed_url = urlparse(url)
    if len(parsed_url.path) > 0:
        sch = parsed_url.scheme
        if (sch == 'http' or sch == 'https' or len(parsed_url.scheme) == 0):
            return True
    module.fail_json(msg="Image Path URL. Wrong Format %s" % (url))
    return False


def run_cl_cmd(module, cmd, check_rc=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret[:-1]


def get_sw_version():
    release_file = open('/etc/lsb-release').readlines()
    for line in release_file:
        if re.search('DISTRIB_RELEASE', line):
            return line.split('=')[1].strip()



def install_img(module):
    app_path = 'usr/cumulus/bin/cl-img-install'
    run_cl_cmd(module, app_path)

def reboot_switch(module):
    pass

def check_sw_version(module, _version):
    if _version == get_sw_version():
        _msg = "Version %s already installed" % (_version)
        module.exit_json(changed=False,  msg=_msg)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            reboot=dict(default='no', choices=["yes", "no"])
        ),
    )

    _changed = False
    _msg = ''

    _version = module.params.get('version')
    _reboot_sw = module.params.get('reboot')
    _url = module.params.get('src')

    check_sw_version(module, _version)
    check_url(module, _url)

    install_img(module)

    if _reboot_sw == 'yes':
        reboot_switch(module)
    else:
        _changed = True
        _msg = "Cumulus Linux Version " + _version + " successfully" + \
                " installed in alternate slot"
        module.exit_json(changed=_changed, msg=_msg)


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
from urlparse import urlparse
import re

if __name__ == '__main__':
    main()
