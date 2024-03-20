'''AWS SM Wrappers'''

# General import
import json
import os
import time

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler
from basepair.modules.aws.service import Service

class SM(Service): # pylint: disable=too-few-public-methods
  '''Wrapper for CW services'''
  def __init__(self, cfg):
    super().__init__(cfg, 'SM')
    self.client = self.session.client(**{
      'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
      'service_name': 'secretsmanager',
    })

  def get(self, secret_id, use_cache=True):
    '''Get the values for the given secret key'''
    key = f'{secret_id}'
    cache_file = f'/tmp/{key}'
    twelve_hours_ago = time.time() - 43200 # 43200 seconds = 12hs
    if use_cache and os.path.isfile(cache_file):
      # reading the price from cache
      cache = {}
      with open(cache_file, 'r', encoding='utf-8') as file:
        cache = json.load(file)
      # expire the cache if needed
      filte_stats = os.stat(cache_file)
      if filte_stats.st_mtime < twelve_hours_ago:
        os.unlink(cache_file)
      # returning cached price
      return cache.get('SecretString', {})

    try:
      response = self.client.get_secret_value(SecretId=secret_id)
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get secret with id {secret_id}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return response
    secret = response.get('SecretString')
    if secret and use_cache:
      with open(cache_file, 'w', encoding='utf-8') as file:
        json_content = json.dumps({'SecretString': secret})
        file.write(json_content)
    return secret
