'''Module webapp api wrapper'''

# App imports
from .abstract import Abstract

class Module(Abstract):
  '''Webapp Module class'''
  def __init__(self, cfg):
    super(Module, self).__init__(cfg)
    self.endpoint += 'modules/'
