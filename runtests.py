#!/usr/bin/env python

import nose
import sys
import os

base_path = os.path.dirname(os.path.realpath(__file__))
mod_path = os.path.join(base_path, 'library')
with open(os.path.join(mod_path, '__init__.py'), "w+") as f:
    f.close()

sys.path.append(os.path.dirname(mod_path))
nose.run()

