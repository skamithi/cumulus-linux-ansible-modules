#!/usr/bin/env python

import nose
import sys
import os
import subprocess
import glob

def main():
    base_path = os.path.dirname(os.path.realpath(__file__))
    mod_path = os.path.join(base_path, 'library')
    with open(os.path.join(mod_path, '__init__.py'), "w+") as _file:
        _file.close()

    sys.path.append(os.path.dirname(mod_path))
    nose.run()

    os.environ['ANSIBLE_LIBRARY'] = './library'
    os.environ['PAGER'] = ''
    _modulelist = glob.glob('library/c*.py')
    for _path in _modulelist:
        print('Checking documentation for %s' % (_path))
        subprocess.call(['ansible-doc', os.path.basename(_path)])

if __name__ == '__main__':
    main()
