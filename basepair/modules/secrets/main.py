'''Storage manager'''

# General imports
import importlib
import os

# pylint: disable=fixme
# TODO: Use a model to abstract the file object and
# its properties / values from different drivers
# for instance the status for the restore from cold feature

class Secrets:
  '''Storage class'''

  def __init__(self):
    '''Secrets Manager constructor'''
    driver =  os.environ.get('SECRETS_DRIVER', 'aws_sm')

    cfg = { 'region': os.environ.get('SECRETS_MANAGER_REGION', 'us-east-1')}
    module = importlib.import_module(f'basepair.modules.secrets.driver.{driver}')
    self.driver = module.Driver(cfg)

  def get(self, secret_id, use_cache=True):
    '''Get the secrets using the ids'''
    return self.driver.get(secret_id, use_cache)