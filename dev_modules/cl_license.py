#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_license
author: Sean Cavanaugh & Stanley Karunditu
short_description: install Cumulus Linux license
requirements:
    - CL 1.5 or later
description:
    - Install Cumulus Linux License
options:
    url:
        description:
            - full path to the license. Can be local path or http url
        required: true
notes:
    - License Documentation: http://cumulusnetworks.com/docs/2.0/
    quick-start/quick-start.html#installing-the-license
    - Contact Us @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
Example playbook entries using the cl_license module to manage
licenses on Cumulus Linux

    tasks:
    - name: install license using http url
      cl_license: url='http://10.1.1.1/license.txt'

    - name: install license from local filesystem
      cl_license: url='/home/nfsshare/license.txt'
'''
LICENSE_PATH = '/mnt/persist/etc/cumulus/.license.txt'


def run_cl_cmd(module, cmd, check_rc=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret[0:len(ret)-1]


def license_installed(module):
    if os.path.exists(LICENSE_PATH) is True:
        module.exit_json(changed=False, msg="license installed")


def check_for_switchd_run_ready():
    count = 30
    while (count >= 0):
        if os.path.exists('var/run/switchd.ready'):
            return True
        count -= 1
        time.sleep(1)
    return False


def restart_switchd_now(module):
    run_cl_cmd(module, 'service switchd restart')
    return check_for_switchd_run_ready()


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
            url=dict(required=True, type='str'),
            restart_switchd=dict(default='no', choices=["yes", "no"])
        ),
    )

    license_installed(module)

    license_url = module.params.get('url')
    restart_switchd = module.params.get('restart_switchd')

    cl_license_path = '/usr/cumulus/bin/cl-license'
    _changed = False
    _msg = ""

    check_license_url(module, license_url)

    cl_lic_cmd = ('%s -i %s') % (cl_license_path, license_url)
    _msg = run_cl_cmd(module, cl_lic_cmd)
    if restart_switchd == 'yes':
        if restart_switchd_now(module):
            _changed = True
            _msg = 'license updated/installed. switchd restarted'
    else:
        _changed = True
        _msg = 'license updated/installed'
    module.exit_json(changed=_changed, msg=_msg)


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
import time
from urlparse import urlparse

if __name__ == '__main__':
    main()
