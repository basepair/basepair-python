'''AWS Service abstract wrappers'''

# General imports
import json
import os
import time
from datetime import datetime

# Libs imports
import boto3
import requests

# App imports
from basepair.modules.logger import Logger
from .sts import STS

class Service: # pylint: disable=too-few-public-methods
  '''Abstract wrapper for services'''
  def __init__(self, cfg, service_name=''):
    self.cfg = cfg
    self.log = Logger.get_instance()
    self.session = None
    self.sts_service = self.connect()

    service = f'AWS {service_name} Service'
    self.handler = {
      'error': f'{service} Error:', # Blocking errors
      'info': f'{service} Info:', # Information
      'warning': f'{service} Warning:', # Non blocking errors
    }

  def connect(self):
    '''connect if session not valid anymore'''
    retry = 0
    # get session
    while True:
      session_args = Service.get_session_args(self.cfg, retry > 0)
      self.session = boto3.session.Session(**session_args)
      if self.cfg.get('disable_sts', False):
        return None
      else:
        sts_service = STS(self.session)
        if sts_service.is_valid_credential() or retry > 3:
          return sts_service
        retry += 1
        time.sleep(5) # else we sleep and try again

  def get_credentials(self):
    '''To get the current used credential for the session'''
    if hasattr(self, 'session'):
      client = self.session.get_credentials()
      return client.get_frozen_credentials()
    return None

  def get_log_msg(self, data):
    '''helper to return formatted log message'''
    default = {
      'exception': '',
      'msg': '',
      'log': True,
      'msg_type': 'error',
      'std_print': True,
    }
    data = {**default, **data}
    msg = f"{self.handler.get(data.get('msg_type'))}\n{data.get('msg')}"
    if data.get('std_print'):
      print(f"{msg}\n{data.get('exception') or ''}")
    if data.get('log') and hasattr(self.log, data.get('msg_type')):
      getattr(self.log, data.get('msg_type'))(msg, payload={'error': f"{data.get('exception')}"})
    return {
      'detail': data.get('exception'),
      'error': data.get('msg_type') == 'error',
      'msg': msg
    }

  @staticmethod
  def get_instance_meta_credentials(clean_cache=False):
    '''Getting credential from cache if exist'''
    tmp_file = '/tmp/.service_meta_info'
    credentials = {}
    expiration = None
    if not clean_cache:
      if os.path.isfile(tmp_file):
        with open(tmp_file, 'r', encoding='utf-8') as file:
          credentials = json.load(file)
          expiration = datetime.strptime(credentials.get('expiration'), '%Y-%m-%dT%H:%M:%SZ')

      if expiration and (expiration - datetime.utcnow()).total_seconds() > 60:
        return credentials

    try:
      os.unlink(tmp_file)
      instance_profile = requests.get('http://169.254.169.254/latest/meta-data/iam/security-credentials/')
      credentials = requests.get(f'http://169.254.169.254/latest/meta-data/iam/security-credentials/{instance_profile.text}').json()
      with open(tmp_file, 'w', encoding='utf-8') as file:
        file_content = json.dumps({
          'expiration': credentials.get('Expiration'),
          'id': credentials.get('AccessKeyId'),
          'secret': credentials.get('SecretAccessKey'),
          'token': credentials.get('Token'),
        })
        file.write(file_content)
    except Exception: # pylint: disable=broad-except
      credentials = {}
    return credentials

  @staticmethod
  def get_session_args(cfg, clean_cache=False):
    '''Generate the session arguments'''
    session_args = {}
    credential = cfg.get('credentials') or Service.get_instance_meta_credentials(clean_cache)
    if credential.get('assume_role'):
      sts_service = STS()
      sts_service.assume_role(credential['assume_role'])
      if sts_service.credential:
        credential['id'] = sts_service.credential.get('AccessKeyId')
        credential['secret'] = sts_service.credential.get('SecretAccessKey')
        credential['token'] = sts_service.credential.get('SessionToken')

    if credential.get('id'):
      session_args['aws_access_key_id'] = credential['id']

    if credential.get('secret'):
      session_args['aws_secret_access_key'] = credential['secret']

    if credential.get('token'):
      session_args['aws_session_token'] = credential['token']

    if cfg.get('region'):
      session_args['region_name'] = cfg['region']
    return session_args

  @staticmethod
  def get_tag_value(item, key):
    '''Helper to get tag value from item'''
    if isinstance(item, dict) and item.get('Tags'):
      return next(
        (tag for tag in item.get('Tags') if tag.get('Key') == key),
        {},
      ).get('Value') or None
    if hasattr(item, 'tags'):
      return next(
        (tag for tag in item.tags if tag.get('Key') == key),
        {},
      ).get('Value') or None
    return None
