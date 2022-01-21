'''Project webapp api wrapper'''
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class Project(Abstract):
  '''Webapp Project class'''
  def __init__(self, cfg):
    super(Project, self).__init__(cfg)
    self.endpoint += 'projects/'
