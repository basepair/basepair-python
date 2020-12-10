'''Upload webapp api wrapper'''

# App imports
from .abstract import Abstract

class Upload(Abstract):
  '''Webapp Upload class'''
  def __init__(self, cfg):
    super(Upload, self).__init__(cfg)
    self.endpoint += 'uploads/'
