import os

from basepair.modules.aws import SM

from basepair.modules.secrets.driver import SecretsAbstract


class Driver(SecretsAbstract):
  '''AWS Driver for secrets manager'''

  def __init__(self):
    self.sm_service = SM({
      'region': os.environ.get('SECRETS_MANAGER_REGION', 'us-east-1')
    })

  def get(self, secret_id, use_cache=True):
    '''Get the secrets using secret_id'''
    return self.sm_service.get(secret_id, use_cache)