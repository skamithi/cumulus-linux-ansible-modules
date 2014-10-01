#!/usr/bin/env python

# A wrapper script to convert an ansible module to something nose knows
# how to import and interperate correctly
# Appreciate any better solutions to this.

import os
import sys
import shutil
import re
import nose

base_path = os.path.dirname(os.path.realpath(__file__))
mod_path = os.path.join(base_path, 'library')
temp_mod_path = os.path.join(base_path, ".temp_mods", "dev_modules")
shutil.rmtree(os.path.dirname(temp_mod_path), ignore_errors=True)
os.makedirs(temp_mod_path)
for i in os.listdir(mod_path):
        src = os.path.join(mod_path, i)
        dst = os.path.join(temp_mod_path, i + ".py")
        #print "src: ", src
        #print "dst: ", dst
        shutil.copy(src, dst)
with open(os.path.join(temp_mod_path, '__init__.py'), "w+") as f:
    f.close()
sys.path.append(os.path.dirname(temp_mod_path))
#print "sys.path: ", sys.path
nose.run()
