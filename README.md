cumulus-linux-ansible-modules
=============================

##Cumulus Linux specific ansible modules.

* dev_modules : contains ansible modules with a suffix of .py for
  easier testing with nose.
* tests: contains tests for each ansible module
* library: contains ansible modules without the .py suffix and are ready to be called by ``ansible`` or ``ansible-playbook``.

##Development

All dev work should be done in devel branch.
When module is stable, merge to master and add a copy of it in the ``library`` directory
After development is completed, merge devel branch back into master and run
``./create_final_module.py`` to generate the module without the ``.py`` extension.


##Testing
All modules created have associated nose test cases. Test cases can be find in ``test`` directory
To run the tests run ``nosetests`` in the git root directory.


## Using these modules

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
