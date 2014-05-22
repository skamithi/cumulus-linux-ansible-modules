#!/usr/bin/env python
#
# Copyright (C) 2014, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_license
author: Sean Cavanaugh & Stanley Karunditu
short_description: install Cumulus Linux license
description:
    - install Cumulus Linux license
options:
    src:
        description:
            - full path to the license. Can be local path or http url
        required: true
    restart_switchd:
        description:
            - restart switchd process after installing the license
        choices: ['yes', 'no']
        default: 'no'
notes:
    - License Documentation - http://cumulusnetworks.com/docs/2.0/quick-start/quick-start.html
    - Contact Cumulus Networks @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
Example playbook entries using the cl_license module to manage
licenses on Cumulus Linux

    tasks:
    - name: install license using http url
      cl_license: src='http://10.1.1.1/license.txt'

    - name: install license from local filesystem
      cl_license: src='/home/nfsshare/license.txt'

    - name: install license from local filesystem restart switchd
      cl_license: src='/home/nfsshare/licence.txt' restart_switchd=yes
'''
LICENSE_PATH = '/etc/cumulus/.license.txt'


def run_cl_cmd(module, cmd, check_rc=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret[:-1]


def license_installed(module):
    if os.path.exists(LICENSE_PATH):
        module.exit_json(changed=False, msg="license already installed")


def check_for_switchd_run_ready(module):
    count = 29
    while count >= 0:
        if os.path.exists('/var/run/switchd.ready'):
            return True
        count -= 1
        time.sleep(1)
    module.fail_json(
        msg='license updated/installed. switchd failed to restart')


def restart_switchd_now(module):
    run_cl_cmd(module, 'service switchd restart')
    return check_for_switchd_run_ready(module)


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
            restart_switchd=dict(default='no', choices=["yes", "no"])
        ),
    )

    license_installed(module)

    license_url = module.params.get('src')
    restart_switchd = module.params.get('restart_switchd')

    cl_license_path = '/usr/cumulus/bin/cl-license'
    _changed = False
    _msg = ""

    check_license_url(module, license_url)

    cl_lic_cmd = ('%s -i %s') % (cl_license_path, license_url)
    run_cl_cmd(module, cl_lic_cmd)
    _msg = 'license updated/installed. no request to restart switchd'
    if restart_switchd == 'yes':
        if restart_switchd_now(module):
            _changed = True
            _msg = 'license updated/installed. switchd restarted'
        else:
            _msg = 'license updated/installed. switchd failed to restart'
            module.fail_json(msg=_msg)
    _changed = True
    module.exit_json(changed=_changed, msg=_msg)


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
import time
from urlparse import urlparse

if __name__ == '__main__':
    main()
