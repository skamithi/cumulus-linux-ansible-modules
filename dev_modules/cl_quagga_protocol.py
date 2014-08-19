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
routing protocol.
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
notes:
    - Quagga Routing Documentation - \
        http://cumulusnetworks.com/docs/2.1/user-guide/layer_3/index.html \
        http://www.nongnu.org/quagga/docs.html \
    - Contact Cumulus Networks @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
Example playbook entries using the cl_quagga module

    tasks:
    - name: activate ospfv2
        cl_quagga_protocol name="ospfd" state=present
    - name: deactivate ospfv3
        cl_quagga_protocol name="ospf6d" state=absent
    - name: enable bgp v4/v6
        cl_quagga_protocol name="bgpd" state=present
    - name: activate ospf then restart quagga right away. don't use notify \
as this might not start quagga when you want it to
        cl_quagga_protocol name="ospfd" state=present
        register: ospf_service
    - name: restart Quagga right away after setting it
        service: name=quagga state=restarted
        when: ospf_service.changed == True
    - name: enable only static routing in quagga
        cl_quagga_protocol name="zebra" state=present
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
    _zebrastr = re.compile("zebra=(yes|no)")
    _matchstr = re.compile(_str)
    for _line in _daemon_output:
        _match = re.match(_matchstr, _line)
        _zebramatch = re.match(_zebrastr, _line)
        if _zebramatch:
            if _zebramatch.group(1) == 'no' and _state == 'yes':
                return False
        elif _match:
            if _state == _match.group(2):
                _msg = "%s is configured and is %s" % \
                    (_protocol, module.params.get('state'))
                module.exit_json(msg=_msg, changed=False)
    # for nosetests purposes only
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
            if _zebramatch.group(1) == 'no' and _state == 'yes':
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
                      choices=['ospfd', 'ospf6d', 'bgp'],
                      required=True),
            state=dict(type='str',
                       choices=['present', 'absent'],
                       required=True)),
    )
    module.quagga_daemon_file = '/etc/quagga/daemons'
    setting_is_configured(module)
    modify_config(module)
    _protocol = module.params.get('name')
    _state = module.params.get('state')
    _state = convert_to_yes_or_no(_state)
    _msg = "%s protocol setting modified to %s" % \
        (_protocol, _state)
    module.exit_json(msg=_msg, changed=True)

# import module snippets
from ansible.module_utils.basic import *
# incompatible with ansible 1.4.4 - ubuntu 12.04 version
# from ansible.module_utils.urls import *
import re

if __name__ == '__main__':
    main()
