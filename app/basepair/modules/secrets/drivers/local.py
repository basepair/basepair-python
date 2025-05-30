import os
import json

from basepair.modules.secrets.drivers import SecretsAbstract


class Driver(SecretsAbstract):
  '''Local Driver for managing Secrets'''

  def __init__(self):
    '''Constructor for local secret driver class'''
    pass

  def get(self, secret_id, use_cache=True):
    '''Get the secrets using secret_id'''
    path = os.environ.get('SECRETS_PATH', '/home/ec2-user')
    secret_file_path = os.path.join(path, secret_id)
    if os.path.isfile(secret_file_path):
      secrets = ""
      with open(secret_file_path, 'r', encoding='utf-8') as file:
        secrets = json.load(file)
        return secrets.get('SecretString', '')
