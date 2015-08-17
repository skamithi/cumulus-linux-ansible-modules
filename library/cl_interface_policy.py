#!/usr/bin/env python
# Copyright (C) 2015, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_interface_policy
author: Cumulus Networks
short_description: Configure interface enforcement policy on Cumulus Linux
description:
    - This module affects the configuration files located in the interfaces \
folder defined by ifupdown2. Interfaces port and port ranges listed in the \
"allowed" parameter define what interfaces will be available on the switch. \
If the user runs this module and has an interface configured on the switch, \
but not found in the "allowed" list, this interface will be unconfigured. \
By default this is `/etc/network/interface.d` \
For more details go the Configuring Interfaces @ \
http://docs.cumulusnetworks.com
notes:
    - lo must be included in the allowed list.
    - eth0 must be in allowed list if out of band management is done
options:
    allowed:
        description:
            - list of ports to run initial run at 10G
    location:
        description:
            - folder to store interface files.
        default: '/etc/network/interfaces.d/'
'''
EXAMPLES = '''
Example playbook entries using the cl_interface_policy module.

    - name: shows types of interface ranges supported
      cl_interface_policy:
          allowed: "lo eth0 swp1-9, swp11, swp12-13s0, swp12-30s1, swp12-30s2, bond0-12"

'''


# get list of interface files that are currently "configured".
# doesn't mean actually applied to the system, but most likely are
def read_current_int_dir(module):
    module.custom_currentportlist = os.listdir(module.params.get('location'))


# take the allowed list and conver it to into a list
# of ports.
def convert_allowed_list_to_port_range(module):
    allowedlist = module.params.get('allowed')
    for portrange in allowedlist:
        module.custom_allowedportlist += breakout_portrange(portrange)


def breakout_portrange(prange):
    _m0 = re.match(r'(\w+[a-z.])(\d+)?-?(\d+)?(\w+)?', prange.strip())
    # no range defined
    if _m0.group(3) is None:
        return [_m0.group(0)]
    else:
        portarray = []
        intrange = range(int(_m0.group(2)), int(_m0.group(3)) + 1)
        for _int in intrange:
            portarray.append(''.join([_m0.group(1),
                                      str(_int),
                                      str(_m0.group(4) or '')
                                      ]
                                     )
                             )
        return portarray


# deletes the interface files
def unconfigure_interfaces(module):
    currentportset = set(module.custom_currentportlist)
    allowedportset = set(module.custom_allowedportlist)
    remove_list = currentportset.difference(allowedportset)
    fileprefix = module.params.get('location')
    module.msg = "remove config for interfaces %s" % (', '.join(remove_list))
    for _file in remove_list:
        os.unlink(fileprefix + _file)


# check to see if policy should be enforced
# returns true if policy needs to be enforced
# that is delete interface files
def int_policy_enforce(module):
    currentportset = set(module.custom_currentportlist)
    allowedportset = set(module.custom_allowedportlist)
    return not currentportset.issubset(allowedportset)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            allowed=dict(type='list', required=True),
            location=dict(type='str', default='/etc/network/interfaces.d/')
        ),
    )
    module.custom_currentportlist = []
    module.custom_allowedportlist = []
    module.changed = False
    module.msg = 'configured port list is part of allowed port list'
    read_current_int_dir(module)
    convert_allowed_list_to_port_range(module)
    if int_policy_enforce(module):
        module.changed = True
        unconfigure_interfaces(module)
    module.exit_json(changed=module.changed, msg=module.msg)


# import module snippets
from ansible.module_utils.basic import *
# from ansible.module_utils.urls import *
import os
import shutil

if __name__ == '__main__':
    main()
