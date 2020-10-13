'''Module webapp api wrapper'''

# App imports
from .abstract import Abstract

class Module(Abstract):
  '''Webapp Module class'''
  def __init__(self, cfg):
    super().__init__(cfg)
    self.endpoint += 'modules/'
