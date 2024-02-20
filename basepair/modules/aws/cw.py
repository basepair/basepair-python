'''AWS CW Wrappers'''

# General import
from datetime import datetime, timedelta
from operator import itemgetter

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler
from basepair.modules.aws.service import Service

class CW(Service): # pylint: disable=too-few-public-methods
  '''Wrapper for CW services'''
  def __init__(self, cfg):
    super().__init__(cfg, 'CW')
    self.client = self.session.client(**{
      'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
      'service_name': 'cloudwatch',
    })

  def get_cpu_load_avg(self, instance_id, range_in_seconds=300):
    '''Get cpu load average'''
    now = datetime.utcnow()
    past = now - timedelta(seconds=range_in_seconds)
    try:
      res = self.client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=past,
        EndTime=now,
        Period=60,
        Statistics=['Average']
      )
      last_datapoint = sorted(res.get('Datapoints'), key=itemgetter('Timestamp'))
      return len(last_datapoint) > 0 and last_datapoint[-1].get('Average')
    except IndexError as error:
      detail = error
      msg = 'No metrics available.'
    except ClientError as error:
      detail = error
      msg = 'Failing trying to access metrics.'
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return self.get_log_msg({'exception': detail, 'msg': msg})

  def get_mem_load_avg(self, instance, range_in_seconds=300):
    '''Get mem load average'''
    now = datetime.utcnow()
    past = now - timedelta(seconds=range_in_seconds)
    try:
      res = self.client.get_metric_statistics(
        Namespace='CWAgent',
        MetricName='mem_used_percent',
        Dimensions=[{
          'Name': 'InstanceId',
          'Value': instance.id,
        }, {
          'Name': 'ImageId',
          'Value': instance.image_id,
        }, {
          'Name': 'InstanceType',
          'Value': instance.instance_type,
        }],
        StartTime=past,
        EndTime=now,
        Period=60,
        Statistics=['Average']
      )
      last_datapoint = sorted(res.get('Datapoints'), key=itemgetter('Timestamp'))
      return len(last_datapoint) > 0 and last_datapoint[-1].get('Average')
    except IndexError as error:
      detail = error
      msg = 'No metrics available.'
    except ClientError as error:
      detail = error
      msg = 'Failing trying to access metrics.'
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return self.get_log_msg({'exception': detail, 'msg': msg})

  def get_storage_load_avg(self, instance, range_in_seconds=300):
    '''Get disk used average'''
    now = datetime.utcnow()
    past = now - timedelta(seconds=range_in_seconds)
    try:
      res = self.client.get_metric_statistics(
        Namespace='CWAgent',
        MetricName='disk_used_percent',
        Dimensions=[{
          'Name': 'InstanceId',
          'Value': instance.id,
        }, {
          'Name': 'ImageId',
          'Value': instance.image_id,
        }, {
          'Name': 'InstanceType',
          'Value': instance.instance_type,
        }, {
          'Name': 'device',
          'Value': 'nvme0n1p1',
        }, {
          'Name': 'fstype',
          'Value': 'ext4',
        }, {
          'Name': 'path',
          'Value': '/',
        }],
        StartTime=past,
        EndTime=now,
        Period=60,
        Statistics=['Average']
      )
      last_datapoint = sorted(res.get('Datapoints'), key=itemgetter('Timestamp'))
      return len(last_datapoint) > 0 and last_datapoint[-1].get('Average')
    except IndexError as error:
      detail = error
      msg = 'No metrics available.'
    except ClientError as error:
      detail = error
      msg = 'Failing trying to access metrics.'
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return self.get_log_msg({'exception': detail, 'msg': msg})