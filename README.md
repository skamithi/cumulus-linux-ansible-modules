##Cumulus Linux specific ansible modules.

* dev_modules : contains ansible modules with a suffix of .py for
  easier testing with nose.
* tests: contains tests for each ansible module
* library: contains ansible modules without the .py suffix and are ready to be called by ``ansible`` or ``ansible-playbook``.

###Development

All dev work should be done in devel branch.
When module is stable, merge to master branch.

###Testing
All modules created have associated nose test cases. Test cases can be found
in ``tests`` directory.
To run the tests run ``runtests.py`` in the git root directory.

#### Required Packages For Tests To Run

python
mock
 (pip install mock)
nose
 (pip install nose)
 

###Using these modules

Clone this directory and then create an ansible.cfg adding the ``library`` directory of this
repo to your ansible module path

Example using ``cl_license`` module
```
# pwd
/files/ansible_modules

# git clone github.com/CumulusNetworks/cumulus-linux-ansible-modules

# cd /files/ansible_playbooks/

# ls

site.yml
roles
ansible.cfg
hosts

# cat ansible.cfg
[defaults]
library = /files/ansible_modules/cumulus-linux-ansible-modules/library:/usr/share/ansible
hostfile = /files/ansible_playbooks/hosts

# cat site.yml
---
- hosts: all
  user: root
  tasks:
    - name: install license from http server
      cl_license: src='http://myserver/license.txt' restart_switchd=yes
      
```


---

![Cumulus icon](http://cumulusnetworks.com/static/cumulus/img/logo_2014.png)

### Cumulus Linux

Cumulus Linux is a software distribution that runs on top of industry standard 
networking hardware. It enables the latest Linux applications and automation 
tools on networking gear while delivering new levels of innovation and 
ﬂexibility to the data center.

For further details please see: [cumulusnetworks.com](http://www.cumulusnetworks.com)
