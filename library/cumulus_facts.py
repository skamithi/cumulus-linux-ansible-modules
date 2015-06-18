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

def run_cl_cmd(module, cmd):
    (rc, out, err) = module.run_command(cmd, check_rc=False)
    # trim last line as it is always empty
    ret = out.splitlines()
    return ret

def license_facts():
    _data = """
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
mqK7+2mKpS5N+8jMVr3eb28Tj9tGIgAA
"""

    license_wrapper = '/tmp/ce-lic-wrapper'
    # run gunzip and remove base64 encoding.
    originfd = GzipFile(mode='r',
        fileobj=StringIO(b64decode(_data)))

    desired_fd = open(license_wrapper, 'w')

    desired_fd.write(originfd.read())
    desired_fd.close()

    os.chmod(license_wrapper, 0755)
    run_cmd(module, '%s -j' % license_wrapper)

    license_dict = {cumulus_license_present: False}
    for k,v in json.loads(json_output).iteritems():
        key_name = "cumulus_license_%s" % (k)
        license_dict[key_name] = v

    return license_dict

def main():
    module = AnsibleModule(argument_spec=dict())
    license_dict = license_facts()
    results = dict(
        msg='Collected Cumulus Linux specific facts',
        ansible_facts=licence_dict
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
