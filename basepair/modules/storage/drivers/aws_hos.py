'''Driver for AWS Health Omics'''

# Libs import
from basepair.modules.aws import HOS
from basepair.modules.aws import S3

# App import
from .aws_s3 import Driver as S3Driver


FILE_NOT_FOUND = 'file_not_found'
RESTORE_COMPLETE = 'restore_complete'
RESTORE_ERROR = 'restore_error'
RESTORE_IN_PROGRESS = 'restore_in_progress'
RESTORE_NOT_REQUIRED = 'restore_not_required'
RESTORE_NOT_STARTED = 'restore_not_started'

class Driver(S3Driver):
  '''AWS Health Omics Driver class'''

  def __init__(self, cfg=None):  # pylint: disable=super-init-not-called
    '''Instance constructor'''
    super().__init__(cfg=cfg)  # calling parent class(S3) constructor to create the S3 client

    storage_settings = cfg.get('settings', {})
    self.hos_service = HOS({
      'credentials': cfg.get('credentials'),
      'reference_store_id': storage_settings.get('ho_reference_store_id'),
      'sequence_store_id': storage_settings.get('ho_sequence_store_id'),
      'region': storage_settings.get('ho_region'),
      'role_arn': storage_settings.get('ho_import_export_role_arn'),
    })

  def get_service(self):
    return self.hos_service

  def get_public_url(self, uri):
    # Omics S3 URIs are generated via S3 access points
    if '-s3alias' in uri:
      bucket = S3.get_bucket_from_uri(uri)
      key = S3.get_key_from_uri(uri, bucket=bucket)
      return self.s3_service.get_self_signed(key, bucket=bucket)
    else:
      super().get_public_url(uri)

  def get_status(self, uri):
    '''Get the file status'''
    if '-s3alias' in uri:
      read_set_id = uri.split('/')[-2]
      status = 'restore_error'
      try:
        metadata = self.hos_service.get_read_set_metadata(read_set_id)
        storage_status = metadata.get('status')
        if storage_status == 'ARCHIVED':
          status = 'restore_not_started'
        elif storage_status == 'ACTIVE':
          status = 'restore_complete'
        elif storage_status == 'ACTIVATING':
          status = 'restore_in_progress'
      except Exception:
        status = 'restore_error'
      return status
    else:
      return super().get_status(uri)

  def restore_files_from_cold(self, uris, days):
    '''Restore files from cold storage'''
    for uri in uris:
      status = self.get_status(uri)
      if status == 'restore_not_started':
        self.restore_from_cold(uri, days=days)

  def restore_from_cold(self, uri, days):
    '''Restore file from cold storage'''
    if '-s3alias' in uri:
      read_set_id = uri.split('/')[-2]
      return self.hos_service.start_read_set_activation_job(sources=[{'readSetId': read_set_id}])
    else:
      super().restore_from_cold(uri, days)