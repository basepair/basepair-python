'''Gene webapp api wrapper'''

# App imports
from .abstract import Abstract

class Gene(Abstract):
  '''Webapp Gene class'''
  def __init__(self, cfg):
    super(Gene, self).__init__(cfg)
    self.endpoint += 'genes/'
