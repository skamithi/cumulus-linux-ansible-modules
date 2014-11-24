
##ABOUT

Cumulus Linux is Linux so Ansible works right out of the box.  However Cumulus Networks has created several modules to reduce complexity of Ansible playbooks and reduce need for jinja templating.  In addition to github the Cumulus Networks Ansible Library is hosted on the Ansible Galaxy website under the role [CumulusLinux](https://galaxy.ansible.com/list#/roles/1875).


## OVERVIEW OF MODULES
- cl_img_install — Install a different version of Cumulus Linux in the inactive slot.
- cl_interface — Configures a front panel, bridge or bond interface on a Cumulus Linux switch.
- cl_license — Install a Cumulus Linux license. 
- cl_prefix_check - Check to see if a route exists.
- cl_quagga_ospf - Configures basic OSPFv2 global parameters and OSPFv2 interface configuration.
- cl_quagga_protocol - Enable Quagga services available on Cumulus Linux.

## INSTALLATION 
To download the CumulusLinux role to the Ansible host, execute the ansible-galaxy install command, and specify **cumulus.CumulusLinux**.


```
cumulus@ansible-vm:~$ sudo ansible-galaxy install cumulus.CumulusLinux
 downloading role 'CumulusLinux', owned by cumulus
 no version specified, installing master
 - downloading role from https://github.com/cumulusnetworks/cumulus-linux-ansible-modules/archive/master.tar.gz
 - extracting cumulus.CumulusLinux to /etc/ansible/roles/cumulus.CumulusLinux
cumulus.CumulusLinux was installed successfully
cumulus@ansible-vm:~$
```

For more detailed installation guide please refer to the [Cumulus Linux Knowledge Base](https://support.cumulusnetworks.com/hc/en-us/articles/204255593)

###Example Playbook

Example using ``cl_license`` module
```
#cd ~/playbook

# ls

site.yml
roles
ansible.cfg
hosts

# cat ansible.cfg
[defaults]
library=/etc/ansible/roles/cumulus.CumulusLinux/library/:/usr/share/ansible 
hostfile = /files/ansible_playbooks/hosts

# cat site.yml
---
- hosts: all
  user: root
  tasks:
    - name: install license from http server
      cl_license: src='http://myserver/license.txt' restart_switchd=yes

```

##Development

All dev work should be done in devel branch.
When module is stable, merge to master branch.

###Description of Folders for this git repo

* tests: contains tests for each ansible module
* library: contains ansible modules and are ready to be called by ``ansible`` or ``ansible-playbook``.

###Testing
All modules created have associated nose test cases. Test cases can be found
in ``tests`` directory.
To run the tests run ``runtests.py`` in the git root directory.

#### Required Packages For Tests To Run

* python
* mock
 * (pip install mock)
* nose
 * (pip install nose)




---

![Cumulus icon](http://cumulusnetworks.com/static/cumulus/img/logo_2014.png)

### Cumulus Linux

Cumulus Linux is a software distribution that runs on top of industry standard
networking hardware. It enables the latest Linux applications and automation
tools on networking gear while delivering new levels of innovation and
ﬂexibility to the data center.

For further details please see: [cumulusnetworks.com](http://www.cumulusnetworks.com)

## CONTRIBUTORS

- Sean Cavanaugh (@seanx820)
- Stanley Karunditu (@skamithik)
