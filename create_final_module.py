#!/usr/bin/env python

import os
import shutil
import re

base_path = os.path.dirname(os.path.realpath(__file__))
dev_mod_path = base_path + '/dev_modules/'
final_mod_path = base_path + '/library/'
for i in os.listdir(dev_mod_path):
    if re.match('[a-z].*.py$', i):
        src = dev_mod_path + i
        dst = final_mod_path + i.replace('.py', '')
        shutil.copy(src, dst)
