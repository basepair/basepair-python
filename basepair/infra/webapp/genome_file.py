'''Genome file webapp api wrapper'''

# App imports
from .abstract import Abstract

class GenomeFile(Abstract):
  '''Webapp GenomeFile class'''
  def __init__(self, cfg):
    super().__init__(cfg)
    self.endpoint += 'genomefiles/'
