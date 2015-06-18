#!/usr/bin/env python
#
# Copyright (C) 2015, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cumulus_facts
author: Cumulus Networks
short_description: Produces Cumulus Linux specific facts
description:
    - Collect facts specific to Cumulus Linux. Currently supports collecting \
license info.
options:
    no_options_for_this_module:
        description:
            - blank
'''
EXAMPLES = '''
## Get cumulus specific facts.
  - name: get cumulus specific facts
    cumulus_facts:

'''

def license_facts(module):
    _data = """
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
"""

    license_wrapper = '/tmp/ce-lic-wrapper'
    # run gunzip and remove base64 encoding.
    originfd = GzipFile(mode='r',
        fileobj=StringIO(b64decode(_data)))

    desired_fd = open(license_wrapper, 'w')

    desired_fd.write(originfd.read())
    desired_fd.close()

    os.chmod(license_wrapper, 0755)


    license_dict = dict(cumulus_license_present=False)
    (_rc, out, _err) = module.run_command("%s -j" % (license_wrapper))
    if _rc == 0:
      license_dict['cumulus_license_present'] = True
      for k,v in json.loads(json_output).iteritems():
        key_name = "cumulus_license_%s" % (k)
        license_dict[key_name] = v

    return license_dict

def main():
    module = AnsibleModule(argument_spec=dict())
    license_dict = license_facts(module)
    results = dict(
        msg='Collected Cumulus Linux specific facts',
        ansible_facts=license_dict
    )
    module.exit_json(**results)


# import module snippets
from ansible.module_utils.basic import *
# from ansible.module_utils.urls import *
from StringIO import StringIO
from base64 import b64decode
from gzip import GzipFile
import os
import json


if __name__ == '__main__':
    main()
