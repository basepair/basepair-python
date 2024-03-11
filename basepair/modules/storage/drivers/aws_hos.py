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
      'credentials': cfg.get('credentials'),
      'sequence_store_id': storage_settings.get('ho_sequence_store_id'),
      'region': storage_settings.get('ho_region'),
      'role_arn': storage_settings.get('ho_import_export_role_arn'),
    })

  def get_service(self):
    return self.hos_service
