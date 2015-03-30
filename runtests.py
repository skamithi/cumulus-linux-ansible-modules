#!/usr/bin/env python

import nose
import sys
import os

base_path = os.path.dirname(os.path.realpath(__file__))
mod_path = os.path.join(base_path, 'library')
sys.path.append(os.path.dirname(mod_path))
nose.run()

