#!/usr/bin/env python
#
# Copyright (C) 2014, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_quagga
author: Stanley Karunditu
short_description: Enable routing protocol services via Quagga
description:
    - Enable Quagga services available on Cumulus Linux. \
This includes OSPF v2/v3 and BGP v4/v6.
options:
    protocols:
        description:
            - provide a list of protocols to enable via Quagga
    state:
        description:
            - start , stop or restart the quagga daemon. By default the \
                quagga daemon is disabled
        choices: ['restarted', 'started', 'stopped']
notes:
    - Quagga Routing Documentation - \
        http://cumulusnetworks.com/docs/2.1/user-guide/layer_3/index.html \
        http://www.nongnu.org/quagga/docs.html \
    - Contact Cumulus Networks @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
Example playbook entries using the cl_quagga module

    tasks:
    - name: activate ospf v2
        cl_quagga: protocols="ospf" state=restarted

    - name: activate ospf v2 and v3
        cl_quagga: protocols="ospf, ospf6d" state=restarted

    - name: activate bgp
        cl_quagga: protocols="bgp" state=restarted

    - name: configure ospfv2 and bgp but don't activate the change
        cl_quagga: protocols="bgp, ospf"

    - name: stop all routing protocols
        cl_quagga: state=stopped

    - name: ospf is enabled but change it to bgp only
        cl_quagga: protocols="ospf" state=restarted

    - name: bgp is enabled but change to bgp and ospf v2
        cl_quagga: protocols="ospf, bgp" state=restarted
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
            protocols=dict(type='str'),
            state=dict(type='str', choices=['stopped', 'started', 'restarted']),
        ),
    )

# import module snippets
from ansible.module_utils.basic import *
# incompatible with ansible 1.4.4 - ubuntu 12.04 version
#from ansible.module_utils.urls import *
from urlparse import urlparse
import re

if __name__ == '__main__':
    main()
