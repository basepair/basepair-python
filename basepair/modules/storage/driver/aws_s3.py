'''Driver for AWS S3 compute'''

# Libs import
from modules.aws import S3

# App import
from .abstract import StorageAbstract

class Driver(StorageAbstract):
  '''AWS S3 Driver class'''

  def __init__(self, cfg=None): # pylint: disable=super-init-not-called
    '''Instance constructor'''
    storage_settings = cfg.get('settings', {})
    self.s3_service = S3({
      'bucket': storage_settings.get('bucket'),
      'credentials': cfg.get('credentials'),
      'region': storage_settings.get('region'),
      'endpoint_url': storage_settings.get('endpoint_url'),
      'disable_sts': storage_settings.get('disable_sts', False),
    })

  def bulk_delete(self, uris):
    '''Delete list of files by their uris'''
    return self.s3_service.bulk_delete(uris)

  def delete(self, uri):
    '''Delete file from storage'''
    key = S3.get_key_from_uri(uri)
    return self.s3_service.delete(key)

  def download(self, uri, callback=None, file=None):
    '''Download file froms torage'''
    bucket = S3.get_bucket_from_uri(uri)
    key = S3.get_key_from_uri(uri)
    if callback:
      return self.s3_service.client.download_fileobj(
        bucket,
        key,
        file,
        Callback=callback,
      )
    return self.s3_service.download(key, file)

  def get_body(self, uri):
    '''Get file body'''
    key = S3.get_key_from_uri(uri)
    return self.s3_service.get_file_body(key)

  def get_head(self, uri):
    '''Get file head'''
    key = S3.get_key_from_uri(uri)
    return self.s3_service.get_object_head(key)

  def get_lifecycle(self, bucket=None):
    '''Get storage lifecycle'''
    return self.s3_service.get_lifecycle(bucket)

  def get_public_url(self, uri):
    '''Get a public accessible url'''
    key = S3.get_key_from_uri(uri)
    return self.s3_service.get_self_signed(key)

  def get_status(self, uri):
    '''Get the file status'''
    bucket = S3.get_bucket_from_uri(uri)
    key = S3.get_key_from_uri(uri)
    return self.s3_service.get_status(bucket=bucket, key=key)

  def get_uri(self, key):
    '''Get uri using key and storage settings'''
    return f's3://{self.s3_service.bucket}/{key}'

  def restore_from_cold(self, uri, days):
    '''Restore file from cold storage'''
    key = S3.get_key_from_uri(uri)
    return self.s3_service.start_restore(key, days)

  def set_body(self, body, uri):
    '''Set file body'''
    key = S3.get_key_from_uri(uri)
    return self.s3_service.set_file_body(body, key)

  def set_lifecycle(self, **kwargs):
    '''Set storage lifecycle'''
    return self.s3_service.set_lifecycle(**kwargs)

  def upload(self, file_name, full_path, force=False):
    '''Upload file to storage'''
    return self.s3_service.upload_file(file_name, full_path, force)
