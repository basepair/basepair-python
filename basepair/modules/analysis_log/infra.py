'''Infra log wrapper'''

# General imports
import sys
import os

# App imports
from .log import Log

class InfraLog(Log): #pylint: disable=too-few-public-methods
  '''Infra log class'''

  def get_data(self):
    '''Set log data'''
    return {
      'id': self.analysis_id,
      'log': {
        'infra': {
          **self.log
        }
      }
    }
