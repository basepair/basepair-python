'''Pipeline webapp api wrapper'''

# App imports
from .abstract import Abstract

class Pipeline(Abstract):
  '''Webapp Pipeline class'''
  def __init__(self, cfg):
    super(Pipeline, self).__init__(cfg)
    self.endpoint += 'pipelines/'
