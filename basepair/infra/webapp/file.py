'''File webapp api wrapper'''

# App imports
from .abstract import Abstract

class File(Abstract):
  '''Webapp File class'''
  def __init__(self, cfg):
    super().__init__(cfg)
    self.endpoint += 'files/'
