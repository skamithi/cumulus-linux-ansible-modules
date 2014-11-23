# This lists a bunch of experimental thoughts and features

* for `cl_img_install` use binary files available to look into new file to
 determine code version. frees up user from defining code version or module
guessing code from filename. Problem is that file must be reside on filesystem
to do this. So does this mean file must be always found on local filesystem
before module works?

* add ospfv3 support to cl_quagga_ospf

* create cl_bgp that can define simple ipv4 bgp config.
  * simple peer connections
  * network statements
  * basic bgp neighbor options

* after creating cl_bgp update it to support basic ipv6 bgp config.
  * suppor ability to do _bgp unnumbered_ using ipv6 link-local address

* update cl_interface to support the new bridge driver

* update cl_interface to support vrr, vrrp, dhcp relay, mlag, as ifupdown2
modules for these features become available
