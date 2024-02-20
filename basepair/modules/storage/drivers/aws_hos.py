'''Driver for AWS Health Omics'''

# Libs import
from basepair.modules.aws import HOS

# App import
from .aws_s3 import Driver as S3Driver

class Driver(S3Driver):
  '''AWS Health Omics Driver class'''

  def __init__(self, cfg=None):  # pylint: disable=super-init-not-called
    '''Instance constructor'''
    super().__init__(cfg=cfg)  # calling parent class(S3) constructor to create the S3 client

    storage_settings = cfg.get('settings', {})
    self.hos_service = HOS({
      'sequence_store_id': storage_settings.get('ho_sequence_store_id'),
      'region': storage_settings.get('ho_region'),
    })
    self.role_arn = storage_settings.get('ho_import_export_role_arn')

  def get_import_job(self, job_id):
    '''Get import job details for a given import job id'''
    return self.hos_service.get_import_job(job_id)

  def get_export_job(self, job_id):
    '''Get import job details for a given export job id'''
    return self.hos_service.get_export_job(job_id)

  def get_read_sets(self, filters):
    '''Get read set list for a given filters'''
    return self.hos_service.get_read_sets(filters)

  def get_service(self):
    return self.hos_service

  def start_import_job(self, sources):
    '''Start a read set import job with given source files'''
    return self.hos_service.start_import_job(role_arn=self.role_arn, sources=sources)

  def start_export_job(self, destination, sources):
    '''Start a read set export job with given source files'''
    return self.hos_service.start_export_job(destination=destination, role_arn=self.role_arn, sources=sources)
