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
        default: '0.0.0.0'
    cost:
        description:
            - define ospf cost.
        required_together:
            - with interface option
    passive:
        description:
            - make OSPF interface passive
        default: 'no'
        choices: ['yes', 'no']
        required_together:
            - with interface option
    anchor_int:
        description:
            - Enables OSPF unnumbered on the interface. Define the name \
of the interface with the IP the interface should anchor to. Module will \
add the IP address of the anchor interface to the \
/etc/network/interfaces config
of the interface.\
If the anchor interface does not have an IP address, the module will fail
    state:
        description:
            - Describes if OSPF should be present on a particular interface.\
Module currently does not check that interface is not associated \
with a bond or bridge. \
User will have to manually clear the configuration of the interface \
from the bond or bridge. \
This will be implemented in a later release
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
    - name: enable ospf unnumbered on swp1
        cl_quagga_ospf: interface=swp1 anchor_int=lo
'''


def run_cl_cmd(module, cmd, check_rc=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret


def check_dsl_dependencies(module, input_options,
                           dependency, _depend_value):
    for _param in input_options:
        if module.params.get(_param):
            if not module.params.get(dependency):
                _param_output = module.params.get(_param)
                _msg = "incorrect syntax. " + _param + " must have an interface option." + \
                    " Example 'cl_quagga_ospf: " + dependency + "=" + _depend_value + " " + \
                    _param + "=" + _param_output + "'"
                module.fail_json(msg=_msg)


def has_interface_config(module):
    modparams = []
    for k, v in module.params.iteritems():
        modparams.append(k)
    if 'interface' in modparams:
        return True
    else:
        return False


def get_running_config(module):
    running_config = run_cl_cmd(module, '/usr/bin/vtysh -c "show run"')
    f = StringIO.StringIO(''.join(running_config))
    got_global_config = False
    module.global_config = []
    for line in f:
        line = line.strip()
        # ignore the '!' lines or blank lines
        if len(line.strip()) <= 1:
            if got_global_config:
                got_global_config = False
            continue
        # make all char lowercase
        line = line.lower()
        # begin capturing global config
        if re.match('router\s+ospf', line):
            got_global_config = True
            continue
        if got_global_config:
            module.global_config.append(line)
            continue

def get_global_config(module):
    get_running_config()

def add_global_ospf_config(module):
    get_global_config(module)


def config_ospf_interface_config(module):
    pass


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
        ),
        mutually_exclusive=[['reference_bandwidth', 'interface'],
                            ['router_id', 'interface']]
    )
    check_dsl_dependencies(module, ['cost', 'state', 'area',
                                    'point2point', 'anchor_int', 'passive'],
                           'interface', 'swp1')
    check_dsl_dependencies(module, ['interface'], 'area', '0.0.0.0')
    if has_interface_config(module):
        add_global_ospf_config(module)
    else:
        config_ospf_interface_config(module)

# import module snippets
from ansible.module_utils.basic import *
import StringIO
import re
# incompatible with ansible 1.4.4 - ubuntu 12.04 version
# from ansible.module_utils.urls import *


if __name__ == '__main__':
    main()
