'''log Wrappers'''

# General imports
import os
import sys
from datetime import datetime

# Libs imports
from basepair.infra.webapp import Analysis

class Abstract:
  '''Abstract class'''
  def __init__(self, config=None, analysis_id=None):
    self.analysis_id = analysis_id
    self.config = config
    self.log = {
      'error': [],
      'info': [],
      'warning': []
    }

  def clear(self):
    '''Clear logs'''
    self.log = {
      'error': [],
      'info': [],
      'warning': []
    }

  def error(self, msg, display_in_report_view=False):
    '''log errors'''
    self._log(field='error', msg=msg, display_in_report_view=display_in_report_view)

  def info(self, msg, display_in_report_view=False):
    '''log info'''
    self._log(field='info', msg=msg, display_in_report_view=display_in_report_view)

  def flush(self):
    '''Save log in db'''
    data = self.get_data()
    response = (Analysis(self.config.get('api'))).save_log(data)
    if response.get('error'):
      print('Error saving analysis log')
      return
    print('Analysis log saved')
    self.clear()

  def warning(self, msg, display_in_report_view=False):
    '''log warning'''
    self._log(field='warning', msg=msg, display_in_report_view=display_in_report_view)

  def _log(self, field='', msg=None, display_in_report_view=False):
    '''log messages'''
    msg = {
      'datetime': str(datetime.now()),
      'msg': msg,
    }
    if display_in_report_view:
      msg['display_in_report_view'] = True
    self.log.get(field).append(msg)

  def get_data(self):
    '''Set log data'''
    return {
      'id': self.analysis_id,
      'log': self.log
    }
