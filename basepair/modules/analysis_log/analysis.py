'''Analysis log wrapper'''

# General imports
import sys
import os

# Libs imports
from basepair.infra.webapp import Analysis

# App imports
from .abstract import Abstract


class AnalysisLog(Abstract):
  '''Analysis log class'''
  def __init__(self, analysis_id=None, config=None, kind=None, node_key=None):
    super().__init__(config, analysis_id)
    self.kind = kind
    self.node_key = node_key

  def get_data(self):
    '''Set log data'''
    return {
      'id': self.analysis_id,
      'log': {
        'bio': {
          self.node_key: {
            self.kind: {
              **self.log
            }
          }
        }
      }
    }

  def update_node(self, cmd=None, status=None, time_taken=None):
    '''Set node cmd, status'''
    node_data = {
      'status': status,
      'time_taken': time_taken
    }

    if cmd:
      node_data['commands'] = cmd
    data = {
      'id': self.analysis_id,
      'log': {
        'bio': {
          self.node_key: node_data
        }
      }
    }

    try:
      response = (Analysis(self.config.get('api'))).save_log(data)
      if response.get('error'):
        print('Error updating analysis node status')
        return
      print('Analysis node status updated')
    except Exception as error: #pylint: disable=broad-except
      print(f'ERROR: Updating analysis node status: {str(error)}')
