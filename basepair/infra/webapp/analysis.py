'''Analysis webapp api wrapper'''

# App imports
from .abstract import Abstract

class Analysis(Abstract):
  '''Webapp Analysis class'''
  def __init__(self, cfg):
    super(Analysis, self).__init__(cfg)
    self.endpoint += 'analyses/'
