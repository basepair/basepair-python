'''Storage manager'''

# General imports
import importlib

# pylint: disable=fixme
# TODO: Use a model to abstract the file object and
# its properties / values from different drivers
# for instance the status for the restore from cold feature

class Secrets:
  '''Storage class'''

  def __init__(self, cfg):
    '''Secrets Manager constructor'''
    driver = cfg.get('driver') or 'aws_sm'
    module = importlib.import_module(f'basepair.modules.secrets.driver.{driver}')
    self.driver = module.Driver(cfg)

  def get(self, secret_id, use_cache=True):
    '''Get the secrets using the ids'''
    return self.driver.get(secret_id, use_cache)