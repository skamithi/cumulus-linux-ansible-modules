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
            - this is a test
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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str',
                      choices=['ospfd', 'ospf6d', 'bgp']),
            state=dict(type='str',
                       choices=['present', 'absent'])
        ),
    )

# import module snippets
from ansible.module_utils.basic import *
# incompatible with ansible 1.4.4 - ubuntu 12.04 version
# from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
