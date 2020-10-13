'''Project webapp api wrapper'''

# App imports
from .abstract import Abstract

class Project(Abstract):
  '''Webapp Project class'''
  def __init__(self, cfg):
    super().__init__(cfg)
    self.endpoint += 'projects/'
