'''Alert abstract class'''

class AlertAbstract:
  '''Abstract class for log drivers'''
  def __init__(self, cfg):
    '''Constructor'''
    self.cfg = {}

  def critical(self, msg, payload):
    '''Send very high severity alert'''

  def high(self, msg, payload):
    '''Send high severity alert'''

  def info(self, msg, payload):
    '''Send very low severity alert'''

  def low(self, msg, payload):
    '''Send low severity alert'''

  def medium(self, msg, payload):
    '''Send medium severity alert'''

  def set_config(self, cfg):
    '''Helper to set configuration'''
