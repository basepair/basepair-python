'''Configuration parser'''

# General imports
import json
import os

# App imports
from basepair.helpers import eprint

class Parser(): # pylint: disable=too-few-public-methods
  '''Configuration parser class'''
  def __init__(self, source):
    # check if local json file
    self.cfg = {}
    if isinstance(source, dict):
      self.cfg = source
    elif os.path.isfile(source):
      try:
        self.cfg = json.load(open(source))
      except OSError as error:
        eprint('ERROR: Not able to open config file: %s' % (str(error)))
      except ValueError as error:
        eprint('ERROR: Not able to read config file: %s' % (str(error)))
    # TODO: if uri implement configuration manager

  @staticmethod
  def get_cli_credentials_from(cfg):
    '''Get cli credential from service cfg'''
    credentials = ''
    credentials_cfg = cfg.get('credentials', {})
    if credentials_cfg and not credentials_cfg.get('role'):
      credentials = 'AWS_ACCESS_KEY_ID={} AWS_SECRET_ACCESS_KEY={} '.format(
        credentials_cfg.get('id'),
        credentials_cfg.get('secret'),
      )
    return credentials

  def get_reflib_storage(self, bucket=None):
    '''Get storage setting for reflibs'''
    storages_cfg = self.cfg.get('storage', {}).get('reflib', {})
    all_reflib_buckets = []
    for storage_cfg in storages_cfg:
      storage_settings = storage_cfg.get('settings', {})
      all_reflib_buckets.append({
        'bucket': bucket or storage_settings.get('bucket'),
        'credentials': storage_cfg.get('credentials'),
        'region': storage_settings.get('region'),
      })
    return all_reflib_buckets

  def get_user_storage(self, bucket=None):
    '''Get storage setting'''
    storage_cfg = self.cfg.get('storage', {}).get('user', {})
    storage_settings = storage_cfg.get('settings', {})
    return {
      'bucket': bucket or storage_settings.get('bucket'),
      'credentials': storage_cfg.get('credentials'),
      'region': storage_settings.get('region'),
    }

  def get_webapp_api(self):
    '''Get webapp api settings'''
    return self.cfg.get('api', {})

  def is_empty(self):
    '''Check if cfg is empty'''
    return not self.cfg
