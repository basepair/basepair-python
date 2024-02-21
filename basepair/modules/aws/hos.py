'''AWS HealthOmics Storage Wrappers'''

# General imports
import uuid

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.service import Service

class HOS(Service):
  '''Wrapper for Health Omics Storage services'''

  def __init__(self, cfg):
    super().__init__(cfg, 'HOS')
    self.client = self.session.client(**{
      'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
      'service_name': 'omics',
    })
    self.sequence_store_id = cfg.get('sequence_store_id')
    self.role_arn = cfg.get('role_arn')

  def get_export_job(self, job_id):
    '''Get export job'''
    try:
      response = self.client.get_read_set_export_job(
        id=job_id,
        sequenceStoreId=self.sequence_store_id,
      )
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get HealthOmics export job information: {str(error)}.',
      })
      raise error
    return response

  def get_read_set_import_job(self, job_id):
    '''Get import job'''
    try:
      response = self.client.get_read_set_import_job(
        id=job_id,
        sequenceStoreId=self.sequence_store_id,
      )
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get HealthOmics import job information: {str(error)}.',
      })
      raise error
    return response

  def get_read_sets(self, filters):
    '''Get read sets list'''
    try:
      response = self.client.list_read_sets(
        sequenceStoreId=self.sequence_store_id,
        filter=filters
      )
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get HealthOmics read sets: {str(error)}.',
      })
      raise error
    return response

  def start_export_job(self, destination, sources):
    '''Start export job'''
    try:
      client_token = str(uuid.uuid4())
      response = self.client.start_read_set_export_job(
        sequenceStoreId=self.sequence_store_id,
        destination=destination,
        roleArn=self.role_arn,
        clientToken=client_token,
        sources=sources
      )
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to start HealthOmics export job: {str(error)}.',
      })
      raise error
    return response

  def start_import_job(self, sources):
    '''Start import job'''
    try:
      return self.client.start_read_set_import_job(
        sequenceStoreId=self.sequence_store_id,
        roleArn=self.role_arn,
        sources=sources
      )
    except ClientError as error:
      self.get_log_msg({
        'exception': str(error),
        'msg': f'Not able to start HealthOmics import job: {str(error)}.',
      })
      raise error