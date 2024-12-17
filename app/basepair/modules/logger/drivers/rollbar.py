'''Rollbar driver'''

# General imports
import sys

# Libs imports
import rollbar

# App imports
from .abstract import LogAbstract

class Instance(LogAbstract):
  '''RollBar implementation of Abstract class'''

  def set_config(self, cfg):
    '''To update the configuration'''
    if not self.log or cfg != self.cfg:
      self.cfg = cfg
      self.log = rollbar
      # if getattr(settings, 'ROLLBAR_SERVER_ACCESS_TOKEN', None):
      #   rollbar_settings = {
      #     'access_token': settings.ROLLBAR_SERVER_ACCESS_TOKEN,
      #     'environment': settings.ROLLBAR_ENVIRONMENT,
      #     'root': os.getcwd(),
      #     'suppress_reinit_warning': True,
      #   }
      #   rollbar.init(**rollbar_settings) # to remove the anoying WARNING:rollbar:Rollbar already initialized. Ignoring re-init.

  def debug(self, msg, payload={}):  # pylint: disable=dangerous-default-value
    '''Send debug log'''
    self.log.report_message(msg, 'debug', **payload)

  def error(self, msg, payload={}):  # pylint: disable=dangerous-default-value
    '''Send error log'''
    self.log.report_message(msg, 'error', **payload)

  def exception(self, payload={}): # pylint: disable=dangerous-default-value
    '''Send exception'''
    self.log.report_exc_info(sys.exc_info())

  def info(self, msg, payload={}):  # pylint: disable=dangerous-default-value
    '''Send info log'''
    self.log.report_message(msg, 'info', **payload)

  def warning(self, msg, payload={}):  # pylint: disable=dangerous-default-value
    '''Send warning log'''
    self.log.report_message(msg, 'warning', **payload)
