### Common Role
Demonstrates how to:
  * set the timezone 
  * install a Cumulus Linux License

### Loopbacks

Range is 10.100.1.X/32  where

* if X = 1 - SPINE1
* if X = 2 - SPINE2
* if X = 3 - LEAF1
* if X = 4 - LEAF4

### Cable/IP Layout

| Switch Name  | Port | IP  | ---  | Remote <br>IP | Remote Port | Remote Switch|
| -------------|---   | --- | ---- |--- |           ---      | --- |
| WAN | swp1 |  10.99.1.1/30 | --- | 10.99.1.2/30|  swp1 | SPINE1 |
| WAN| swp2 | 10.99.1.5/30| --- |10.99.1.6/30 | swp1 | SPINE2|
| SPINE1 | swp10 | 10.101.3.1/30 | --- | 10.101.3.2/30 | swp2 | LEAF1 |
| SPINE1 | swp11 |  10.101.4.1/30 | ---| 10.101.4.2/30 | swp2 | LEAF1 |
| SPINE2 | swp10 |  10.102.3.1/30 |  ---|  10.102.3.2/30 | swp2 | LEAF1|
| SPINE2 | swp11 | 10.102.4.1/30 | --- | 10.102.4.2/30 | swp1  | LEAF2 |

### LEAF1 Host VLANs (primary link)
* vlan1 - mgmt - 10.1.11.2/24
* vlan2 - data - 10.1.2.2/24
* vlan3 - ctrl - 10.1.3.2/24

### LEAF2 Host VLANs (backup link)

*  vlan11 - mgmt - 10.1.11.2/24
* vlan12 - data - 10.1.12.1/24
*  vlan13 - ctrl - 10.1.13.1/24

### OSPF

* OSPFv2 configured on all interfaces with IPs
      * loopbacks with passive enabled
      *  vlan interfaces with passive enabled
* router ID set to the loopback interfaces
* by default `cl_quagga_ospf` sets reference-bandwidth to 40G.

