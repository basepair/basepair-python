'''Driver for Logbook log'''

# General imports
import sys

# Libs import
import logbook

# App imports
from .abstract import LogAbstract

class Instance(LogAbstract):
  '''LogBook implementation of Abstract class'''

  def set_config(self, cfg):
    '''To update the configuration'''
    if not self.log or cfg != self.cfg:
      self.cfg = cfg
      self.log = logbook.Logger(cfg.get('name', 'Logger'))
      hand = logbook.FileHandler(cfg.get('log_file', '/tmp/app.log'))
      hand.push_application()

  def debug(self, msg, payload={}): # pylint: disable=dangerous-default-value
    '''Send debug log'''
    try:
      self.log.debug([msg, payload])
    except Exception: # pylint: disable=broad-except
      pass

  def error(self, msg, payload={}): # pylint: disable=dangerous-default-value
    '''Send error log'''
    try:
      self.log.error([msg, payload])
    except Exception: # pylint: disable=broad-except
      pass

  def exception(self, payload={}): # pylint: disable=dangerous-default-value
    '''Send exception'''
    try:
      self.log.error([sys.exc_info(), payload])
    except Exception: # pylint: disable=broad-except
      pass

  def info(self, msg, payload={}): # pylint: disable=dangerous-default-value
    '''Send info log'''
    try:
      self.log.info([msg, payload])
    except Exception: # pylint: disable=broad-except
      pass

  def warning(self, msg, payload={}): # pylint: disable=dangerous-default-value
    '''Send warning log'''
    try:
      self.log.info([msg, payload])
    except Exception: # pylint: disable=broad-except
      pass
