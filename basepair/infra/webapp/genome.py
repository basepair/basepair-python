'''Genome webapp api wrapper'''

# App imports
from .abstract import Abstract

class Genome(Abstract):
  '''Webapp Genome class'''
  def __init__(self, cfg):
    super().__init__(cfg)
    self.endpoint += 'genomes/'
