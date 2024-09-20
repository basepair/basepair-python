#!/usr/bin/env python

import json

import basepair

config_file = '/Users/amit/hg/webapp/bin/err/config.utk.dev2.json'
conf = json.load(open(config_file))
bp = basepair.connect(conf, verbose=True)

bp.update_project(2, {'name': 'proj 4'})
