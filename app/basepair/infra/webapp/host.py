'''Host webapp api wrapper'''

# App imports
from .abstract import Abstract

class Host(Abstract):
  '''Webapp Host class'''
  def __init__(self, cfg):
    super(Host, self).__init__(cfg)
    self.endpoint += 'hosts/'
