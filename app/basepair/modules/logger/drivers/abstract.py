'''Log abstract class'''

class LogAbstract:
  '''Abstract class for log drivers'''
  def __init__(self):
    '''Constructor'''
    self.cfg = {}
    self.log = None

  def set_config(self, cfg): # pylint: disable=dangerous-default-value
    '''To update the configuration'''

  def debug(self, msg, payload={}): # pylint: disable=dangerous-default-value
    '''Send debug log'''

  def error(self, msg, payload={}): # pylint: disable=dangerous-default-value
    '''Send error log'''

  def exception(self, payload={}): # pylint: disable=dangerous-default-value
    '''Send exception'''

  def info(self, msg, payload={}): # pylint: disable=dangerous-default-value
    '''Send info log'''

  def warning(self, msg, payload={}): # pylint: disable=dangerous-default-value
    '''Send warning log'''
