#!/usr/bin/env python
#
# Copyright (C) 2014, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_quagga_protocol
author: Stanley Karunditu
short_description: Enable routing protocol services via Quagga
description:
    - Enable Quagga services available on Cumulus Linux. \
This includes OSPF v2/v3 and BGP. Quagga services are defined in the \
/etc/quagga/daemons file. This module creates a file that will only enable \
OSPF or BGP routing protocols, because this is what Cumulus Linux currently \
supports. Using Ansible Templates you any supported or unsupported quagga \
routing protocol. For more details go to the Quagga Documentation located at \
http://cumulusnetworks.com/docs/2.2 and \
http://www.nongnu.org/quagga/docs.html
options:
    name:
        description:
            - name of the protocol to update
        choices: ['zebra', 'ospfd', 'ospf6d', 'bgpd']
        required: true
    state:
        description:
            - describe whether the protocol should be enabled or disabled
        choices: ['present', 'absent']
        required: true
    activate:
        description:
            - restart quagga process to activate the change. If the service \
is already configured but not activated, setting activate=yes will not activate the service. \
This will be fixed in an upcoming release
        choices: ['yes', 'no']
        default: ['no']
requirements: ['Quagga version 0.99.23 and higher']
'''
EXAMPLES = '''
Example playbook entries using the cl_quagga module

## Enable OSPFv2. Do not activate the change
    cl_quagga_protocol name="ospfd" state=present

## Disable OSPFv2. Do not activate the change
    cl_quagga_protocol name="ospf6d" state=absent

## Enable BGPv2. Do not activate the change. Activating the change requires a restart of the
## entire quagga process.
    cl_quagga_protocol name="bgpd" state=present

## Enable OSPFv2 and activate the change
as this might not start quagga when you want it to
    cl_quagga_protocol name="ospfd" state=present activate=yes

## To activate a configured service

- name: disable ospfv2 service. Its configured but not enabled
  cl_quagga_protocol name=ospfd state=absent

- name: enable ospfv2 service and activate it
  cl_quagga_protocol name=ospfd state=present activate=yes
'''


def run_cl_cmd(module, cmd, check_rc=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret


def convert_to_yes_or_no(_state):
    if _state == 'present':
        _str = 'yes'
    else:
        _str = 'no'
    return _str


def read_daemon_file(module):
    f = open(module.quagga_daemon_file)
    if f:
        return f.readlines()
    else:
        return []


def setting_is_configured(module):
    _protocol = module.params.get('name')
    _state = module.params.get('state')
    _state = convert_to_yes_or_no(_state)
    _daemon_output = read_daemon_file(module)
    _str = "(%s)=(%s)" % (_protocol, 'yes|no')
    _daemonstr = re.compile("\w+=yes")
    _zebrastr = re.compile("zebra=(yes|no)")
    _matchstr = re.compile(_str)
    daemoncount = 0
    module.disable_zebra = False
    for _line in _daemon_output:
        _match = re.match(_matchstr, _line)
        _active_daemon_match = re.match(_daemonstr, _line)
        _zebramatch = re.match(_zebrastr, _line)
        if _active_daemon_match:
            daemoncount += 1
        if _zebramatch:
            if _zebramatch.group(1) == 'no' and _state == 'yes':
                return False
        elif _match:
            if _state == _match.group(2):
                _msg = "%s is configured and is %s" % \
                    (_protocol, module.params.get('state'))
                module.exit_json(msg=_msg, changed=False)
    # for nosetests purposes only
    if daemoncount < 3 and _state == 'no':
        module.disable_zebra = True
    return False


def modify_config(module):
    _protocol = module.params.get('name')
    _state = module.params.get('state')
    _state = convert_to_yes_or_no(_state)
    _daemon_output = read_daemon_file(module)
    _str = "(%s)=(%s)" % (_protocol, 'yes|no')
    _zebrastr = re.compile("zebra=(yes|no)")
    _matchstr = re.compile(_str)
    write_to_file = open(module.quagga_daemon_file, 'w')
    for _line in _daemon_output:
        _match = re.match(_matchstr, _line)
        _zebramatch = re.match(_zebrastr, _line)
        if _zebramatch:
            if module.disable_zebra is True and _state == 'no':
                write_to_file.write('zebra=no\n')
            elif _state == 'yes':
                write_to_file.write('zebra=yes\n')
            else:
                write_to_file.write(_line)
        elif _match:
            if _state != _match.group(2):
                _str = "%s=%s\n" % (_protocol, _state)
                write_to_file.write(_str)
        else:
            write_to_file.write(_line)
    write_to_file.close()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str',
                      choices=['ospfd', 'ospf6d', 'bgpd'],
                      required=True),
            state=dict(type='str',
                       choices=['present', 'absent'],
                       required=True),
            activate=dict(type='bool', choices=BOOLEANS, default=False)
        ))
    module.quagga_daemon_file = '/etc/quagga/daemons'
    setting_is_configured(module)
    modify_config(module)
    _protocol = module.params.get('name')
    _state = module.params.get('state')
    _state = convert_to_yes_or_no(_state)
    _msg = "%s protocol setting modified to %s" % \
        (_protocol, _state)
    if module.params.get('activate') is True:
        run_cl_cmd(module, '/usr/sbin/service quagga restart')
        _msg += '. Restarted Quagga Service'
    module.exit_json(msg=_msg, changed=True)

# import module snippets
from ansible.module_utils.basic import *
# incompatible with ansible 1.4.4 - ubuntu 12.04 version
# from ansible.module_utils.urls import *
import re

if __name__ == '__main__':
    main()
