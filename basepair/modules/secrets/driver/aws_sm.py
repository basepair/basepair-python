from basepair.modules.aws import SM

from basepair.modules.secrets.driver import SecretsAbstract


class Driver(SecretsAbstract):
  '''AWS Driver for secrets manager'''

  def __init__(self, cfg=None):
    sm_settings = cfg.get('settings', {})
    self.sm_service = SM({
      'credentials': cfg.get('credentials', None), # is this required?
      'region': sm_settings.get('region'),
    })

  def get(self, secret_id, use_cache=True):
    '''Get the secrets using secret_id'''
    return self.sm_service.get(secret_id, use_cache)