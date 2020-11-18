'''Analysis webapp api wrapper'''

# General imports
import json

# Lib imports
import requests

# App imports
from .abstract import Abstract
from basepair.helpers import eprint

class Analysis(Abstract):
  '''Webapp Analysis class'''
  def __init__(self, cfg):
    super(Analysis, self).__init__(cfg)
    self.endpoint += 'analyses/'
