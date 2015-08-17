#!/usr/bin/env python
#
# Copyright (C) 2015, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_interface
author: Cumulus Networks
short_description: Configures a front panel port, loopback or \
management port on Cumulus Linux.
description:
    - Configures a front panel, sub-interface, SVI, management \
or loopback port on a Cumulus Linux switch. For bridge ports \
use the cl_bridge module. For bond ports use the \
cl_bond module. When configuring bridge related features like \
the "vid" option, please follow the guidelines for configuring \
"vlan aware" bridging. For more details \
review the Layer2 Interface Guide @ \
http://docs.cumulusnetworks.com
options:
    name:
        description:
            - name of the interface
        required: true
    alias_name:
        description:
            - add a port description
    ipv4:
        description:
            - list of IPv4 addresses to configure on the interface. \
use X.X.X.X/YY syntax.
    ipv6:
        description:
            - list of IPv6 addresses  to configure on the interface. \
use X:X:X::X/YYY syntax
    addr_method:
        description:
            - can be loopback for loopback interfaces or dhcp for dhcp \
interfaces.
    speed:
        description:
            - set speed of the swp(front panel) or \
management(eth0) interface. speed is in MB
    mtu:
        description:
            - set MTU. Configure Jumbo Frame by setting MTU to 9000.

    virtual_ip:
        description:
            - define IPv4 virtual IP used by the Cumulus VRR feature
    virtual_mac:
        description:
            - define Ethernet mac associated with Cumulus VRR feature
    vids:
        description:
            - in vlan aware mode, lists vlans defined under the interface
    mstpctl_bpduguard:
        description:
            - Enables BPDU Guard on a port in vlan-aware mode
    mstpctl_portnetwork:
        description:
            - Enables bridge assurance in vlan-aware mode
    clagd_enable:
        description:
            - Enables the clagd daemon. This command should only \
be applied to the clag peerlink interface
    clagd_priority:
        description:
            - Integer that changes the role the switch has in the clag domain \
The lower priority switch will assume the primary role. The number can be \
0 and 65535
    clagd_peer_ip:
        description:
            - IP address of the directly connected peer switch interface
    clagd_sys_mac:
        description:
            - Clagd system mac address. Recommended to use the range starting \
with 44:38:39:ff. Needs to be the same between 2 Clag switches
    pvid:
        description:
            - in vlan aware mode, defines vlan that is the untagged vlan
    location:
        description:
            - interface directory location
        default:
            - /etc/network/interfaces.d

requirements: [ Alternate Debian network interface manager - \
ifupdown2 @ github.com/CumulusNetworks/ifupdown2 ]
notes:
    - because the module writes the interface directory location. Ensure that \
``/etc/network/interfaces`` has a 'source /etc/network/interfaces.d/*' \
or whatever path is mentioned in the ``location`` attribute.

    - For the config to be activated, i.e installed in the kernel, \
"service networking reloaded" needs be be executed. See EXAMPLES section.

'''

EXAMPLES = '''
# Options ['virtual_mac', 'virtual_ip'] are required together
# configure a front panel port with an IP
cl_interface: name=swp1  ipv4=10.1.1.1/24
notify: reload networking

# configure front panel to use DHCP
cl_interface: name=swp2 addr_family=dhcp
notify: reload networking

# configure a SVI for vlan 100 interface with an IP
cl_interface: name=bridge.100 ipv4=10.1.1.1/24
notify: reload networking

# configure subinterface with an IP
cl_interface: name=bond0.100  alias_name='my bond' ipv4=10.1.1.1/24
notify: reload networking

# define cl_interfaces once in tasks
# then write intefaces in variables file
# with just the options you want.
cl_interface:
  name: "{{ item.key }}"
  ipv4: "{{ item.value.ipv4|default(omit) }}"
  ipv6: "{{ item.value.ipv6|default(omit) }}"
  alias_name: "{{ item.value.alias_name|default(omit) }}"
  addr_method: "{{ item.value.addr_method|default(omit) }}"
  speed: "{{ item.value.link_speed|default(omit) }}"
  mtu: "{{ item.value.mtu|default(omit) }}"
  clagd_enable: "{{ item.value.clagd_enable|default(omit) }}"
  clagd_peer_ip: "{{ item.value.clagd_peer_ip|default(omit) }}"
  clagd_sys_mac: "{{ item.value.clagd_sys_mac|default(omit) }}"
  clagd_priority: "{{ item.value.clagd_priority|default(omit) }}"
  vids: "{{ item.value.vids|default(omit) }}"
  virtual_ip: "{{ item.value.virtual_ip|default(omit) }}"
  virtual_mac: "{{ item.value.virtual_mac|default(omit) }}"
  mstpctl_portnetwork: "{{ item.value.mstpctl_portnetwork|default('no') }}"
  mstpctl_bpduguard: "{{ item.value.mstpctl_bpduguard|default('no') }}"
with_dict: cl_interfaces
notify: reload networking


# In vars file
# ============
cl_interfaces:
    swp1:
        alias_name: 'uplink to isp'
        ipv4: '10.1.1.1/24'
    swp2:
        alias_name: 'l2 trunk connection'
        vids: [1, 50]
    swp3:
        speed: 1000
        alias_name: 'connects to 1G link'
##########
#   br0 interface is configured by cl_bridge
##########
    br0.100:
        alias_name: 'SVI for vlan 100'
        ipv4: '10.2.2.2/24'
        ipv6: '10:2:2::2/127'
        virtual_ip: '10.2.2.254'
        virtual_mac: '00:00:5E:00:10:10'


'''


# handy helper for calling system calls.
# calls AnsibleModule.run_command and prints a more appropriate message
# exec_path - path to file to execute, with all its arguments.
# E.g "/sbin/ip -o link show"
# failure_msg - what message to print on failure
def run_cmd(module, exec_path):
    (_rc, out, _err) = module.run_command(exec_path)
    if _rc > 0:
        if re.search('cannot find interface', _err):
            return '[{}]'
        failure_msg = "Failed; %s Error: %s" % (exec_path, _err)
        module.fail_json(msg=failure_msg)
    else:
        return out


def current_iface_config(module):
    # due to a bug in ifquery, have to check for presence of interface file
    # and not rely solely on ifquery. when bug is fixed, this check can be
    # removed
    _ifacename = module.params.get('name')
    _int_dir = module.params.get('location')
    module.custom_current_config = {}
    if os.path.exists(_int_dir + '/' + _ifacename):
        _cmd = "/sbin/ifquery -o json %s" % (module.params.get('name'))
        module.custom_current_config = module.from_json(
            run_cmd(module, _cmd))[0]


def build_address(module):
    # if addr_method == 'dhcp', dont add IP address
    if module.params.get('addr_method') == 'dhcp':
        return
    _ipv4 = module.params.get('ipv4')
    _ipv6 = module.params.get('ipv6')
    _addresslist = []
    if _ipv4 and len(_ipv4) > 0:
        _addresslist += _ipv4
    if _ipv6 and len(_ipv6) > 0:
        _addresslist += _ipv6
    if len(_addresslist) > 0:
        module.custom_desired_config['config']['address'] = ' '.join(
            _addresslist)


def build_vids(module):
    _vids = module.params.get('vids')
    if _vids and len(_vids) > 0:
        module.custom_desired_config['config']['bridge-vids'] = ' '.join(_vids)


def build_pvid(module):
    _pvid = module.params.get('pvid')
    if _pvid:
        module.custom_desired_config['config']['bridge-pvid'] = str(_pvid)


def build_speed(module):
    _speed = module.params.get('speed')
    if _speed:
        module.custom_desired_config['config']['link-speed'] = str(_speed)
        module.custom_desired_config['config']['link-duplex'] = 'full'


def conv_bool_to_str(_value):
    if isinstance(_value, bool):
        if _value is True:
            return 'yes'
        else:
            return 'no'
    return _value


def build_generic_attr(module, _attr):
    _value = module.params.get(_attr)
    _value = conv_bool_to_str(_value)
    if _value:
        module.custom_desired_config['config'][
            re.sub('_', '-', _attr)] = str(_value)


def build_alias_name(module):
    alias_name = module.params.get('alias_name')
    if alias_name:
        module.custom_desired_config['config']['alias'] = alias_name


def build_addr_method(module):
    _addr_method = module.params.get('addr_method')
    if _addr_method:
        module.custom_desired_config['addr_family'] = 'inet'
        module.custom_desired_config['addr_method'] = _addr_method


def build_vrr(module):
    _virtual_ip = module.params.get('virtual_ip')
    _virtual_mac = module.params.get('virtual_mac')
    vrr_config = []
    if _virtual_ip:
        vrr_config.append(_virtual_mac)
        vrr_config.append(_virtual_ip)
        module.custom_desired_config.get('config')['address-virtual'] = \
            ' '.join(vrr_config)


def build_desired_iface_config(module):
    """
    take parameters defined and build ifupdown2 compatible hash
    """
    module.custom_desired_config = {
        'addr_family': None,
        'auto': True,
        'config': {},
        'name': module.params.get('name')
    }

    build_addr_method(module)
    build_address(module)
    build_vids(module)
    build_pvid(module)
    build_speed(module)
    build_alias_name(module)
    build_vrr(module)
    for _attr in ['mtu', 'mstpctl_portnetwork',
                  'mstpctl_bpduguard', 'clagd_enable',
                  'clagd_priority', 'clagd_peer_ip',
                  'clagd_sys_mac', 'clagd_args']:
        build_generic_attr(module, _attr)


def config_dict_changed(module):
    """
    return true if 'config' dict in hash is different
    between desired and current config
    """
    current_config = module.custom_current_config.get('config')
    desired_config = module.custom_desired_config.get('config')
    return current_config != desired_config


def config_changed(module):
    """
    returns true if config has changed
    """
    if config_dict_changed(module):
        return True
    # check if addr_method is changed
    return module.custom_desired_config.get('addr_method') != \
        module.custom_current_config.get('addr_method')


def replace_config(module):
    temp = tempfile.NamedTemporaryFile()
    desired_config = module.custom_desired_config
    # by default it will be something like /etc/network/interfaces.d/swp1
    final_location = module.params.get('location') + '/' + \
        module.params.get('name')
    final_text = ''
    _fh = open(final_location, 'w')
    # make sure to put hash in array or else ifquery will fail
    # write to temp file
    try:
        temp.write(module.jsonify([desired_config]))
        # need to seek to 0 so that data is written to tempfile.
        temp.seek(0)
        _cmd = "/sbin/ifquery -a -i %s -t json" % (temp.name)
        final_text = run_cmd(module, _cmd)
    finally:
        temp.close()

    try:
        _fh.write(final_text)
    finally:
        _fh.close()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            ipv4=dict(type='list'),
            ipv6=dict(type='list'),
            alias_name=dict(type='str'),
            addr_method=dict(type='str',
                             choices=['', 'loopback', 'dhcp']),
            speed=dict(type='str'),
            mtu=dict(type='str'),
            virtual_ip=dict(type='str'),
            virtual_mac=dict(type='str'),
            vids=dict(type='list'),
            pvid=dict(type='str'),
            mstpctl_portnetwork=dict(type='bool', choices=BOOLEANS),
            mstpctl_bpduguard=dict(type='bool', choices=BOOLEANS),
            clagd_enable=dict(type='bool', choices=BOOLEANS),
            clagd_priority=dict(type='str'),
            clagd_peer_ip=dict(type='str'),
            clagd_sys_mac=dict(type='str'),
            clagd_args=dict(type='str'),
            location=dict(type='str',
                          default='/etc/network/interfaces.d')
        ),
        required_together=[
            ['virtual_ip', 'virtual_mac'],
            ['clagd_enable', 'clagd_priority',
             'clagd_peer_ip', 'clagd_sys_mac']
        ]
    )

    # if using the jinja default filter, this resolves to
    # create an list with an empty string ['']. The following
    # checks all lists and removes it, so that functions expecting
    # an empty list, get this result. May upstream this fix into
    # the AnsibleModule code to have it check for this.
    for k, _param in module.params.iteritems():
        if isinstance(_param, list):
            module.params[k] = [x for x in _param if x]

    _location = module.params.get('location')
    if not os.path.exists(_location):
        _msg = "%s does not exist." % (_location)
        module.fail_json(msg=_msg)
        return  # for testing purposes only

    ifacename = module.params.get('name')
    _changed = False
    _msg = "interface %s config not changed" % (ifacename)
    current_iface_config(module)
    build_desired_iface_config(module)
    if config_changed(module):
        replace_config(module)
        _msg = "interface %s config updated" % (ifacename)
        _changed = True

    module.exit_json(changed=_changed, msg=_msg)

# import module snippets
from ansible.module_utils.basic import *
import tempfile
import os

if __name__ == '__main__':
    main()