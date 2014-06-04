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
    switch_slots:
        description:
            - Switch slots after installing the image. Only a reboot is needed.
            Reboot can be done as a notification.
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

    - name: install image from local filesystem
      cl_img_install: version=2.0.1 src='/root/CumulusLinux-2.0.1.bin'

    - name: install image and switch slots. only reboot needed
      cl_img_install: version=2.0.1 src=/root/image.bin switch_slots=yes'
'''

SLOTS = None


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


def active_sw_version(module):
    lsb_release = '/etc/lsb-release'
    active_version = None
    try:
        lsb_file = open(lsb_release).readlines()
    except:
        module.fail_json(
            msg="failed to read active version file %s" % (lsb_release))
        return None
    for line in lsb_file:
        _match = re.search('DISTRIB_RELEASE=([0-9a-zA-Z.]+)', line)
        if _match:
            active_version = _match.group(1)
            return active_version


def get_slot_info(active_ver):
    slot_ver_file = '/mnt/root-rw/onie/u-boot-env.txt'
    try:
        onie_file = open('/mnt/root-rw/onie/u-boot-env.txt').readlines()
    except:
        module.fail_json(
            msg="failed to read slots detail file %s" % (slot_ver_file))
        return None
    slots = {}
    slots['1'] = {}
    slots['2'] = {}
    num = None
    for line in onie_file:
        _match = re.match('cl.ver(\d+)=(.*)', line)
        if _match:
            num = _match.group(1)
            ver = _match.group(2).split('-')[0]
            slots[num]['version'] = ver
            if slots[num]['version'] == active_ver:
                slots[num]['active'] = True
        _match = re.match('cl.active=(\d+)', line)
        if _match:
            num = _match.group(1)
            slots[num]['primary'] = True
    return slots


def install_img(module):
    src = module.params.get('src')
    app_path = '/usr/cumulus/bin/cl-img-install -f %s' % (src)
    run_cl_cmd(module, app_path)


def switch_slots(module, slotnum):
    _switch_slots = module.params.get('switch_slots')
    if _switch_slots == 'yes':
        app_path = '/usr/cumulus/bin/cl-img-select %s' % (slotnum)
        run_cl_cmd(module, app_path)


def check_sw_version(module, _version):
    SLOTS = get_slot_info(_version)
    for _num in SLOTS.keys():
        slot = SLOTS[_num]
        if slot['version'] == _version:
            if 'active' in slot:
                _msg = "Version %s is installed in the active slot" \
                    % (_version)
                module.exit_json(changed=False,  msg=_msg)
            else:
                perform_switch_slots = module.params.get('switch_slots')
                _msg = "Version " + _version + \
                    " is installed in the alternate slot. "
                if 'primary' not in slot:
                    if perform_switch_slots == 'yes':
                        switch_slots(module, _num)
                        _msg = _msg + \
                            "cl-img-select has made the alternate " + \
                            "slot the primary slot. " +\
                            "Next reboot, switch will load " + _version + "."
                        module.exit_json(changed=True, msg=_msg)
                    else:
                        _msg = _msg + \
                            "Next reboot will not load " + _version + ". " + \
                            "switch_slots keyword set to 'no'."
                        module.exit_json(changed=False, msg=_msg)
                else:
                    _msg = _msg + \
                        "Next reboot, switch will load " + _version + "."
                    module.exit_json(changed=False, msg=_msg)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            version=dict(required=True, type='str'),
            switch_slots=dict(default='no', choices=["yes", "no"])
        ),
    )

    _changed = False
    _msg = ''

    _version = module.params.get('version')
    _url = module.params.get('src')

    check_sw_version(module, _version)

    check_url(module, _url)

    install_img(module)

    check_sw_version(module, _version)

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
