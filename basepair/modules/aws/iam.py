'''AWS IAM Wrappers'''

# General imports
import json
try:
  from time import time_ns
except ImportError:
  from datetime import datetime
  # For compatibility with Python 3.6
  def time_ns():
    now = datetime.now()
    return int(now.timestamp() * 1e9)

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError, ParamValidationError

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler
from basepair.modules.aws.service import Service

class IAM(Service):
  '''Wrapper for IAM services'''
  def __init__(self, cfg):
    super().__init__(cfg, 'IAM')
    self.client = self.session.client(**{
      'config': Config(retries={'max_attempts': 10, 'mode': 'standard'}),
      'service_name': 'iam',
    })
    # Reminder: Update __bp_tmp_user__ will require to update boundary policy for the role
    self.username_pattern = cfg.get('username_pattern') or '_tmp_{}'

  def delete_access_keys(self, username):
    '''Delete all the access keys of the user'''
    response = {}
    try:
      has_access = self.client.list_access_keys(UserName=username)
      if has_access:
        for existing_access_key in has_access.get('AccessKeyMetadata'):
          self.client.delete_access_key(
            AccessKeyId=existing_access_key.get('AccessKeyId'),
            UserName=username,
          )
    except (ClientError, ParamValidationError) as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete access key for user {username}.',
        'msg_type': 'warning',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def delete_inline_policies(self, username):
    '''Delete inline policies of the user'''
    response = {}
    try:
      list_response = self.client.list_user_policies(UserName=username)
      if list_response and list_response.get('PolicyNames'):
        for policy in list_response['PolicyNames']:
          self.client.delete_user_policy(PolicyName=policy, UserName=username)
    except (ClientError, self.client.exceptions.NoSuchEntityException) as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete inline policies for user {username}.',
        'msg_type': 'warning',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def delete_policy(self, policy_arn):
    '''Delete the specific policy'''
    try:
      for version in self.get_policy_versions(policy_arn):
        if not version.get('IsDefaultVersion'):
          self.get_log_msg({
            'exception': None,
            'msg': f"Deleting policy version {version.get('VersionId')}.",
            'msg_type': 'info',
          })
          self.client.delete_policy_version(PolicyArn=policy_arn, VersionId=version.get('VersionId'))
      # Deleting default version
      self.client.delete_policy(PolicyArn=policy_arn,)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete policy {policy_arn}.',
        'msg_type': 'warning',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

  def get_policy_versions(self, policy_arn):
    '''Get policy versions'''
    max_item = 100
    loops = 0
    try:
      response = self.client.list_policy_versions(PolicyArn=policy_arn, MaxItems=max_item)
      while response.get('IsTruncated'):
        loops += 1
        next_page = self.client.list_policy_versions(
          Marker=response.get('Marker'),
          MaxItems=max_item,
          PolicyArn=policy_arn,
        )
        response['IsTruncated'] = next_page.get('IsTruncated')
        response['Marker'] = next_page.get('Marker')
        response['Versions'] += next_page.get('Versions')
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to list policy versions for policy {policy_arn}.',
        'msg_type': 'warning',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response['Versions']

  def delete_user(self, uid, ignore_format=False):
    '''Delete the user from aws'''
    username = str(uid) if ignore_format else self.username_pattern.format(uid)

    # check if user exist
    try:
      self.client.get_user(UserName=username)
    except (ClientError, self.client.exceptions.NoSuchEntityException) as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete user {username}.',
        'msg_type': 'info',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return

    try:
      self.client.delete_login_profile(UserName=username)
    except (ClientError, self.client.exceptions.NoSuchEntityException) as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete login profile for user {username}.',
        'msg_type': 'info',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

    self.detach_policies(username)
    self.delete_access_keys(username)
    self.delete_inline_policies(username)

    try:
      self.client.delete_user(UserName=username)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete user {username}.',
        'msg_type': 'warning',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

  def detach_policies(self, username, delete=True):
    '''Detach policies from user'''
    try:
      list_response = self.client.list_attached_user_policies(UserName=username)
      if list_response and list_response.get('AttachedPolicies'):
        for policy in list_response['AttachedPolicies']:
          self.client.detach_user_policy(
            PolicyArn=policy.get('PolicyArn'),
            UserName=username,
          )
          if delete:
            self.delete_policy(policy.get('PolicyArn'))
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to list/detach/delete policies for user {username}.',
        'msg_type': 'warning',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

  def setup_user(self, uid, boundary='', tags=[]): # pylint: disable=dangerous-default-value,too-many-branches
    '''Create IAM user and key'''
    username = self.username_pattern.format(uid)
    access_key = None
    try:
      self.client.get_user(UserName=username)
    except ClientError as error:
      if (getattr(error, 'response', {})).get('Error', {}).get('Code') == 'NoSuchEntity':
        args = {'Tags': tags, 'UserName': username}
        if boundary:
          args['PermissionsBoundary'] = boundary
        self.client.create_user(**args)
      else:
        username = None
        self.get_log_msg({
          'exception': error,
          'msg': f'Not able to find/create user {username}.',
          'msg_type': 'warning',
        })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

    if username:
      # We always clear any existing access key and create new one to get the credentials
      # there is a limited quote of 2 that cannot be changed in AWS
      self.delete_access_keys(username)
      try:
        access_key_response = self.client.create_access_key(UserName=username)
        access_key = access_key_response.get('AccessKey')
        if access_key:
          access_key.update({
            'CreateDate': access_key['CreateDate'].strftime('%m/%d/%Y, %H:%M:%S')
          })
      except (ClientError, ParamValidationError) as error:
        access_key = None
        self.get_log_msg({
          'exception': error,
          'msg': f'Not able to create access key for user {username}.',
          'msg_type': 'warning',
        })
        if ExceptionHandler.is_throttled_error(exception=error):
          raise error
    return username, access_key

  def set_inline_policy(self, policy_scheme, username, replace=True):
    '''Set inline policy to user'''
    # clear out old policies
    if replace:
      self.delete_inline_policies(username)

    # adding new policy
    try:
      self.client.put_user_policy(
        PolicyDocument=json.dumps(policy_scheme),
        PolicyName=f'{username}_policy_{time_ns()}',
        UserName=username,
      )
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to set inline policy for user {username}.',
        'msg_type': 'warning',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return policy_scheme

  def set_policy(self, policy_scheme, username, force=True, sufix='', tags=[]): # pylint: disable=too-many-arguments,dangerous-default-value
    '''Create a policy and attach it to the user'''
    # create new policy

    # detach and delete any existing policies for the user
    if force:
      self.detach_policies(username)

    policy_name = f'{username}_policy{sufix}'
    try:
      args = {
        'PolicyDocument': json.dumps(policy_scheme),
        'PolicyName': policy_name,
        'Tags': tags,
      }
      response = self.client.create_policy(**args)
      policy = response.get('Policy')
    except self.client.exceptions.EntityAlreadyExistsException as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Policy {policy_name} already exists.',
        'msg_type': 'info',
      })
      # look for existing policy
      account_id = self.sts_service.client.get_caller_identity()['Account']
      policy_arn = f'arn:aws:iam::{account_id}:policy/{policy_name}'
      policy = self.client.get_policy(PolicyArn=policy_arn)['Policy']
    except ClientError as error:
      policy = None
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to create or get policy {policy_name}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

    if policy:
      try:
        self.client.attach_user_policy(
          UserName=username,
          PolicyArn=policy.get('Arn'),
        )
      except ClientError as error:
        self.get_log_msg({
          'exception': error,
          'msg': f'Not able to attach policy {policy_name} to user {username}.',
        })
        if ExceptionHandler.is_throttled_error(exception=error):
          raise error
    return policy