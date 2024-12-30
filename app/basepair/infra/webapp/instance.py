'''Instance webapp api wrapper'''

# Lib imports
import json
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class Instance(Abstract):
  '''Webapp Instance class'''
  def __init__(self, cfg):
    super(Instance, self).__init__(cfg)
    self.endpoint += 'instances/'

