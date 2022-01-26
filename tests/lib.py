from __future__ import print_function

import json
import os
import sys
import unittest

# use local basepair module instead of package installed with pip
sys.path.insert(0, os.path.realpath(__file__ + '/../../'))
import basepair


class BaseTest(unittest.TestCase):
    # try:
    #     conf = json.load(open(os.environ.get('BP_API_CONFIG', None)))
    # except:
    #     sys.exit('Error in config file.'
    #                          ' Please properly set BP_API_CONFIG.')

    # bp = basepair.connect(conf=conf)

    confs = {}
    conf_names = ['_', '_SUPER_', '_ALICE_', '_BOB_', '_CLAIRE_']
    for conf_name in conf_names:
        try:
            confs[conf_name] = json.load(open(os.environ.get(
                'BP{}API_CONFIG'.format(conf_name), None)))
        except:
            sys.exit(('Error in config file.' +
                ' Please properly set BP {} API_CONFIG.'.format(conf_name)),
                file=sys.stderr)

    # TODO: for now leave as is; maybe later put this in above loop and change test files where appropriate
    bp = basepair.connect(conf=confs['_'],verbose=True)
    bp_super = basepair.connect(conf=confs['_SUPER_'],verbose=True)
    bp_alice = basepair.connect(conf=confs['_ALICE_'],verbose=True) # alice
    bp_bob = basepair.connect(conf=confs['_BOB_'],verbose=True) # bob
    bp_claire = basepair.connect(conf=confs['_CLAIRE_'],verbose=True) # claire


def compare_info(old_data, new_data):
    for key, val in old_data.items():
        # if old_data.get(key) != new_data.get(key):
        # replace f string in the following line if uncommenting
        #     print(f'{old_data.get(key)} != {new_data.get(key)}')
        if (type(new_data.get(key)) == dict 
            and type(old_data.get(key)) == str 
            and new_data[key].get('resource_uri')):
            assert old_data.get(key) == new_data[key].get('resource_uri')
        else:
            assert old_data.get(key) == new_data.get(key)
