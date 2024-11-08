'''AWS Logs Wrappers'''

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# App imports
from basepair.modules.aws.service import Service


class Logs(Service):
  '''Wrapper for CW services'''
  def __init__(self, cfg):
    super().__init__(cfg, 'CW')
    self.client = self.session.client(**{
      'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
      'service_name': 'logs',
    })

  def get_log_events(self, log_group_name, log_stream_name, limit=10):
    '''Get log events'''
    try:
      res = self.client.get_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        limit=limit
      )
      return res.get('events')
    except ClientError as error:
      raise Exception('Unable to get log events') from error
