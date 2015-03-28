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
    - Install a Cumulus Linux license. If an existing license has expired, \
it will be replaced with the new license. The module currently doesn't check \
the new license expiration date. This will be done in a future release.  \
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
license. It overwrites the existing license without checking \
if the license has expired or not.
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

   handlers:
     - name: restart switchd
       service: name=switchd state=restarted

   - hosts: all
     tasks:
        - name: configure interfaces
          template: src=interfaces.j2 dest=/etc/network/interfaces
          notify: restart networking

     handlers:
       - name: restart networking
         service: name=networking state=reloaded

'''
LICENSE_PATH = '/etc/cumulus/.license.txt'


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

def get_todays_date():
    """
    create function to wrap getting today's date so i can mock it.
    """
    return datetime.now()


def license_is_current():
    """
    Check that license is current. If it is not,
    then install the license file from ansible
    * Assumes that license file been installed is current. Not checking this *
    """
    license_file = open(LICENSE_PATH).readlines()
    for _line in license_file:
        if re.match('expires', _line):
            expire_date = _line.split()[0].split('=')[1]
            # today's date in epoch
            todays_date = get_todays_date().strftime('%s')
            if expire_date > todays_date:
                return True
    return False


def license_upto_date(module):
    if module.params.get('force') is True:
        return
    if os.path.exists(LICENSE_PATH) and license_is_current():
        module.exit_json(changed=False,
                         msg="license is installed and has not expired")


def check_license_url(module, license_url):
    parsed_url = urlparse(license_url)
    if parsed_url.scheme == 'http' and len(parsed_url.path) > 0:
        return True
    if len(parsed_url.scheme) == 0 and len(parsed_url.path) > 0:
        return True
    module.fail_json(msg="License URL. Wrong Format %s" % (license_url))
    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            force=dict(type='bool', choices=BOOLEANS, default=False)
        ),
    )



    license_url = module.params.get('src')

    license_upto_date(module)

    cl_license_path = '/usr/cumulus/bin/cl-license'
    _changed = False
    _msg = "License installed and not expired"

    check_license_url(module, license_url)

    cl_lic_cmd = ('%s -i %s') % (cl_license_path, license_url)
    run_cmd(module, cl_lic_cmd)
    _changed = True
    _msg = 'license updated/installed. remember to restart switchd'
    module.exit_json(changed=_changed, msg=_msg)


# import module snippets
from ansible.module_utils.basic import *
# from ansible.module_utils.urls import *
import time
from datetime import datetime
from urlparse import urlparse

if __name__ == '__main__':
    main()
