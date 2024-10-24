'''AWS S3 Wrappers'''

# General imports
import json
import mimetypes
import re
from datetime import datetime

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler
from basepair.modules.aws.service import Service

# Constants
DEFAULT_RESTORE_PERIOD = 7 # days
DEFAULT_TRANSITION_THRESHOLD = 30 # days

class S3(Service):
  '''Wrapper for S3 services'''
  def __init__(self, cfg):
    self.cfg = cfg
    super().__init__(cfg, 'S3')
    self.bucket = cfg.get('bucket')
    client_vars = {
      'config': Config(
        retries={'max_attempts': 10, 'mode': 'standard'},
        signature_version='s3v4',
      ),
      'service_name': 's3',
    }
    if cfg.get('endpoint_url'):
        client_vars['endpoint_url'] = cfg.get('endpoint_url')
    self.client = self.session.client(**client_vars)
    self.resource = self.session.resource('s3')

  def bulk_delete(self, uris):
    '''Bulk objects deletion by uri auto detecting bucket'''
    # validate uris
    uri_list = {'not_valid': {}, 'valid': {}}
    for uri in uris:
      bucket = self.bucket
      validation_label = 'not_valid'
      if uri.startswith('s3'):
        # group by bucket
        bucket = S3.get_bucket_from_uri(uri)
        validation_label = 'valid'
      uri_list[validation_label][bucket] = uri_list[validation_label].get(bucket) or []
      uri_list[validation_label][bucket].append({
        'Key': S3.get_key_from_uri(uri, bucket)
      })

    # if there are valid uris we try to delete them
    response = self.get_log_msg({
      'msg': 'Nothing to delete.',
      'msg_type': 'info',
    })
    if uri_list.get('valid'):
      for bucket, objects in uri_list['valid'].items():
        try:
          self.client.delete_objects(
            Bucket=bucket,
            Delete={'Quiet': True, 'Objects': objects},
          )
        except ClientError as error:
          response = self.get_log_msg({
            'exception': error,
            'msg': 'Not able to delete objects.',
          })
          if ExceptionHandler.is_throttled_error(exception=error):
            raise error
      response = self.get_log_msg({
        'msg': 'S3 deletion completed.',
        'msg_type': 'info',
      })

    # if there are invalid uris we return a warning
    if uri_list.get('not_valid'):
      response = self.get_log_msg({
        'exception': 'Not valid URI.',
        'msg': f"Not valid uris provided for deletion.\n{json.dumps(uri_list.get('not_valid'), indent=2)}",
        'msg_type': 'warning',
      })
    return response

  def delete(self, key, bucket=None):
    '''Delete object'''
    bucket = bucket or self.bucket
    try:
      self.client.delete_object(Bucket=bucket, Key=key)
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete object key {key}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return response
    return True

  def download(self, key, file=None, bucket=None):
    '''Download key as file'''
    bucket = bucket or self.bucket
    file = file or key.split('/')[-1]
    try:
      self.client.download_file(
        Bucket=self.bucket,
        Key=key,
        Filename=file
      )
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to download object key {key}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return response
    return True

  def get_bucket(self, bucket=None):
    '''Return bucket object'''
    bucket = bucket or self.bucket
    try:
      self.client.head_bucket(Bucket=bucket)
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to access bucket {bucket}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return response
    return self.resource.Bucket(bucket)

  def get_file_body(self, key):
    '''Return the content of the file if possible'''
    if self.get_object_head(key):
      try:
        response = self.client.get_object(
          Bucket=self.bucket,
          Key=key,
        )
        return response['Body'].read()
      except ClientError as error:
        self.get_log_msg({
          'exception': error,
          'msg': f'Not able to get object body for key {key}.',
        })
        if ExceptionHandler.is_throttled_error(exception=error):
          raise error
    return None

  def get_lifecycle(self, bucket=None):
    '''Get the current configuration of the object'''
    bucket = bucket or self.bucket
    response = None
    try:
      response = self.client.get_bucket_lifecycle_configuration(
        Bucket=bucket,
      )
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get lifecycle configuration for bucket {bucket}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def get_object_head(self, key, bucket=None, show_log=True):
    '''Check if key exists in S3 bucket'''
    bucket = bucket or self.bucket
    try:
      response = self.client.head_object(Bucket=bucket, Key=key)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get object header for key {key} in bucket {bucket}.',
        'std_print': show_log,
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      response = int(error.response['Error']['Code']) != 404
    return response

  def get_self_signed(self, key, bucket=None, expires_in=28800):
    '''Generate self signed url for key'''
    try:
      bucket = bucket or self.bucket
      return self.client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expires_in, # a week
      )
    except (ClientError, NoCredentialsError, Exception) as error: # pylint: disable=broad-except
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to self sign object key {key}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return None

  def get_storage_context(self):
    '''Method to return context for S3'''
    return {
      'storage_archival_enabled' : bool(self.cfg.get('restore_period', False)),
      'storage_bucket' : self.cfg.get('bucket'),
      'storage_driver': 'aws_s3',
      'storage_region' : self.cfg.get('region'),
      'storage_sse_enabled' : 'True',
      'storage_url': f"https://s3.{self.cfg.get('region')}.amazonaws.com",
    }

  def get_status(self, key, bucket=None):
    '''Method to check the status of file restore process'''
    status = 'restore_error'
    storage_class = None
    head_response = self.get_object_head(key, bucket)
    if type(head_response).__name__ == 'dict':
      storage_class = head_response.get('StorageClass') or 'STANDARD'
      restore_status = head_response.get('Restore', '')
      # Object in STANDARD, INTELLIGENT_TIERING, GLACIER_IR, ONEZONE_IA, STANDARD_IA => Instant retrieval possible
      status = 'restore_not_started' if storage_class in ['DEEP_ARCHIVE', 'GLACIER'] else 'restore_not_required'
      # check the status of restoration if had been triggered
      if restore_status and 'true' in restore_status:
        status = 'restore_in_progress'
      elif restore_status and 'false' in restore_status:
        status = 'restore_complete'
    elif head_response is False:  # 404 not found
      status = 'file_not_found'
    return status, storage_class

  def get_storage_class(self, key, bucket=None):
    '''Return the storage class of the key'''
    response = self.get_object_head(key, bucket)
    return response.get('StorageClass', '') or 'STANDARD'

  def list(self, prefix, bucket=None):
    '''List objects with prefix'''
    bucket = bucket or self.bucket
    try:
      all_files = []
      continuation_token = None
      while True:
        params = {'Bucket': bucket, 'Prefix': prefix}
        if continuation_token:
          params['ContinuationToken'] = continuation_token

        response = self.client.list_objects_v2(**params)
        all_files.extend(response.get('Contents', []))
        if not response.get('IsTruncated'):  # At the end of the list?
          break
        continuation_token = response.get('NextContinuationToken')
      return all_files
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to list objects in bucket {bucket}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return {}

  def replicate(self, source, new_file, storage_class='STANDARD_IA'):
    '''Replicate a file from S3 to S3'''
    try:
      return self.client.copy_object(
        CopySource={
          'Bucket': source.get('bucket', self.bucket),
          'Key': source.get('key'),
        },
        Bucket=self.bucket,
        Key=new_file,
        StorageClass=storage_class
      )
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to replicate object key {source}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return None

  def set_file_body(self, body, key):
    '''Write content to file'''
    try:
      return self.client.put_object(
        Body=body,
        Bucket=self.bucket,
        Key=key
      )
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to set object body for key {key}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return response

  def set_lifecycle(self, **kwargs):
    '''
    :param append_rule: (boolean) if previous rules are to be retained
    :param bucket: (string) bucket name for which the lifecycle rule is to be set
    :param prefix: (string) folder wise filter for which the lifecycle will be effective
    :param storage_class: (string) cold storage s3 class name where the files will be moved
    :param tag: (Array) of dictionary that will be used as a filter while applying lifecycle rule
                [{'Key': 'some_key', 'Value': 'some_value'}]
    '''
    transition_threshold = kwargs.get('transition_threshold') or DEFAULT_TRANSITION_THRESHOLD # days
    storage_class = kwargs.get('storage_class') or 'DEEP_ARCHIVE'
    prefix = kwargs.get('prefix') or 'uploads/'
    tag = kwargs.get('tag')
    rules = []
    tag_name = tag and f'<{tag[0].get("Key")}:{tag[0].get("Value")}>'
    object_filter = {
        'And': {
            'Prefix': prefix,
            'Tags': tag
            }
        } if tag else {'Prefix': prefix}
    new_rule = {
      'Filter': object_filter,
      'ID': f'Move-files-in-{prefix}-{f"with-tag-{tag_name}" if tag else ""}-to-{storage_class}-\
        after-{transition_threshold}-days-<created-{datetime.now()}>',
      'Status': 'Enabled',
      'Transitions': [
        {
          'Days': transition_threshold,
          'StorageClass': storage_class,
        },
      ],
    }
    if kwargs.get('append_rule'):
      rules = self.convert_to_v2(self.get_lifecycle().get('Rules', []))
    rules.append(new_rule)
    bucket = kwargs.get('bucket') or self.bucket
    response = None
    try:
      response = self.client.put_bucket_lifecycle_configuration(
        Bucket=bucket,
        LifecycleConfiguration={
          'Rules': rules,
        },
      )
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to update lifecycle configuration for bucket {bucket}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def start_restore(self, key, days=DEFAULT_RESTORE_PERIOD, bucket=None, tier='Standard'):
    '''
    Restore object using key
    If the object is not previously restored, then Amazon S3 returns 202 Accepted in the response.
    If the object is previously restored, Amazon S3 returns 200 OK in the response.
    DEEP_ARCHIVE only supports 'Standard' tier for retrieval
    '''
    restore_status, storage_class = self.get_status(key)
    if restore_status == 'restore_not_started':
      try:
        self.client.restore_object(
          Bucket=bucket or self.bucket,
          Key=key,
          RestoreRequest={
            'Days': days,
            'GlacierJobParameters': {
              'Tier': 'Expedited' if storage_class == 'GLACIER' else tier
            }
          }
        )
        restore_status = 'restore_in_progress'
      except ClientError as error:
        self.get_log_msg({
          'exception': error,
          'msg': f'Not able to restore object key {key}.',
        })
        if ExceptionHandler.is_throttled_error(exception=error):
          raise error
        restore_status = 'restore_error'
    return restore_status, storage_class

  def upload_file(self, file_name, full_path, extra_args=None, force=False, show_log=True):
    '''Upload a file to an S3 bucket'''
    extra_args = extra_args or {}
    mimetype, _ = mimetypes.guess_type(file_name)
    if mimetype:
      extra_args['ContentType'] = mimetype

    # Upload the file
    try:
      if force or not self.get_object_head(full_path, show_log=show_log):
        self.client.upload_file(file_name, self.bucket, full_path, ExtraArgs=extra_args)
      else:
        print(f'Skipping file {full_path} because already exist in S3.')
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to upload file {file_name}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return response

    # get url by key
    return {
      'path': full_path,
      'url': self.get_self_signed(full_path),
    }
  
  def upload_file_obj(self, file_obj, full_path, extra_args=None, force=False, show_log=True):
    '''Upload a file to an S3 bucket'''
    extra_args = extra_args or {}
    
    # Upload the file
    try:
      if force or not self.get_object_head(full_path, show_log=show_log):
        self.client.put_object(Body=file_obj, Bucket=self.bucket, Key=full_path, **extra_args)
        
        self.client.put_object_acl(Bucket=self.bucket, Key=full_path, ACL='public-read-write')
      else:
        print(f'Skipping file {full_path} because already exist in S3.')
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to upload file {file_obj}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return response
    
    # get url by key
    return {
      'path': full_path,
      'url': self.get_self_signed(full_path),
    }

  @staticmethod
  def convert_to_v2(rules):
    '''Method to convert the version1 lifecycle configuration format to v2'''
    for rule in rules:
      if 'Prefix' in rule:
        rule['Filter'] = {'Prefix': rule['Prefix']}
        rule.pop('Prefix')
    return rules

  @staticmethod
  def get_bucket_from_uri(uri):
    '''Helper to get bucket from uri'''
    match = re.search(r'^s3:\/\/([^:\/?\n]+)', uri)
    return match and match.group(1)

  @staticmethod
  def get_key_from_uri(uri, bucket=None):
    '''Helper to get key from uri'''
    bucket = bucket or S3.get_bucket_from_uri(uri)
    return uri.replace(f's3://{bucket}/', '')
