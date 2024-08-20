'''AWS STS wrappers'''

# General imports
from datetime import datetime

# Libs imports
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# App imports
from basepair.modules.logger import Logger

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler

class STS: # pylint: disable=too-few-public-methods
  '''Abstract wrapper for services'''
  def __init__(self, session=None, service_name='GeneralPurpose'):
    self.client = session.client(**{
      'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
      'service_name': 'sts',
    }) if session else boto3.client('sts')
    self.credential = None
    self.log = Logger.get_instance()
    self.service_name = service_name

    service = f'AWS {service_name} Service'
    self.handler = {
      'error': f'{service} Error:', # Blocking errors
      'info': f'{service} Info:', # Information
      'warning': f'{service} Warning:', # Non blocking errors
    }

  def assume_role(self, role):
    '''Assume role'''
    now = datetime.now()
    try:
      response = self.client.assume_role(
        RoleArn=role,
        RoleSessionName=f'AssummingRoleFor{self.service_name}_{now.strftime("%Y%m%d%H%M%S")}',
      )
      self.credential = response.get('Credentials')
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to assume role {role}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

  def is_valid_credential(self):
    '''Check if valid credential'''
    try:
      self.client.get_caller_identity()
      return True
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': 'Not able to get caller identity.',
        'msg_type': 'warning',
      })
      return False

  def get_log_msg(self, data):
    '''helper to return formated log message'''
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
