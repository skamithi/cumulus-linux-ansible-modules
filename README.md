cumulus-linux-ansible-modules
=============================

Cumulus Linux specific ansible modules.

* dev_modules : contains ansible modules with a suffix of .py for
  easier testing with nose.
* tests: contains tests for each ansible module
* final_modules: contains ansible modules with the .py suffix.

Development

All dev work should be done in devel branch.
When module is stable, merge to master and add a copy of it in the final_modules
directory.
TODO: (script to do this will be created)

--
This is a good guide on how branching can be managed in git and still
keep yourself sane when having to support multiple versions of your code.

http://nvie.com/posts/a-successful-git-branching-model/

If I can figure out a way to run nose on a python script with .py suffix, then
we can do away with final_modules , dev_modules structure. I'm sure its possible
but for now this works.


