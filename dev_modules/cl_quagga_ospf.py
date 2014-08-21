#!/usr/bin/env python
#
# Copyright (C) 2014, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_quagga_ospf
author: Stanley Karunditu
short_description: Configure basic OSPF parameters and interfaces
description:
    - Configures basic OSPF global parameters such as \
router id and bandwidth cost, or OSPF interface configuration \
like point-to-point settings or enabling OSPF on an interface. \
Configuration is applied to single OSPF instance. \
Multiple OSPF instance configuration is currently not supported.
options:
    router_id:
        description:
            - Set the OSPF router id
        required: true
    reference_bandwidth:
        description:
            - Set the OSPF reference bandwidth
        default: 40000
    saveconfig:
        description:
            - Boolean. Issue write memory to save the config
        choices: ['yes', 'no']
        default: ['no']
    interface:
        description:
            - define the name the interface to apply OSPF services.
    point2point:
        description:
            - Boolean. enable OSPF point2point on the interface
        choices: ['yes', 'no']
        default: ['no']
        require_together:
            - with interface option
    area:
        description:
            - defines the area the interface is in
        default: '0'
    cost:
        description:
            - define ospf cost.
        required_together:
            - with interface option
    anchor_int:
        description:
            - Enables OSPF unnumbered on the interface. Define the name \
of the interface with the IP the interface should anchor to. \
If the anchor interface does not have an IP address, the command will fail
    state:
        description:
            - Describes if OSPF should be present on a particular interface.\
        choices: [ 'present', 'absent']
        default: 'present'
        required_together:
            - with interface option
notes:
    - Quagga Routing Documentation - \
        http://cumulusnetworks.com/docs/2.1/user-guide/layer_3/index.html \
        http://www.nongnu.org/quagga/docs.html \
    - Contact Cumulus Networks @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
Example playbook entries using the cl_quagga_ospf module

    tasks:
    - name: configure ospf router_id
        cl_quagga_ospf: router_id=10.1.1.1
    - name: enable OSPF on swp1 and set it be a point2point OSPF \
interface with a cost of 65535
        cl_quagga_ospf: interface=swp1 point2point=yes cost=65535
    - name: enable ospf on swp1-5
        cl_quagga_ospf: interface={{ item }}
        with_sequence: start=1 end=5 format=swp%d
    - name: disable ospf on swp1
        cl_quagga_ospf: interface=swp1 state=absent
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
            reference_bandwidth=dict(type='str',
                                     default='40000'),
            router_id=dict(type='str'),
            interface=dict(type='str'),
            cost=dict(type='str'),
            area=dict(type='str', default='0'),
            state=dict(type='str',
                       choices=['present', 'absent']),
            point2point=dict(choices=BOOLEANS, default=False),
            anchor_int=dict(type='str'),
            saveconfig=dict(choices=BOOLEANS, default=False)
        ))


# import module snippets
from ansible.module_utils.basic import *
# incompatible with ansible 1.4.4 - ubuntu 12.04 version
# from ansible.module_utils.urls import *


if __name__ == '__main__':
    main()
