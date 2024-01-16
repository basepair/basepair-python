def raise_no_implemented():
  '''Helper to raise exception when call no implemented method'''
  raise Exception('Abstract method require to be implemented.')

class SecretsAbstract:
  '''Abstract Driver class'''

  def __init__(self, cfg=None):
    raise Exception('Abstract class cannot be instantiated.')

  def get(self, secret_id, use_cache):
    raise_no_implemented()