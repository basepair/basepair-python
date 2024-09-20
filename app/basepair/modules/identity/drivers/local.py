from datetime import datetime

from basepair.modules.identity.drivers import IdentityAbstract


class Driver(IdentityAbstract):
  def __init__(self, cfg=None):
    self.iam_settings = cfg.get('settings', {})
    self.iam_credentials = cfg.get('credentials', {})
    self.username_pattern = cfg.get('username_pattern') or '_tmp_{}'

  def delete_access_keys(self, username):
    '''Method to delete access keys'''
    pass

  def delete_inline_policies(self, username):
    '''Method to delete delete inline policies'''
    pass

  def delete_policy(self, policy_arn):
    '''Method to delete policy'''
    pass

  def get_policy_versions(self, policy_arn):
    '''Method to get policy version'''
    pass

  def delete_user(self, uid, ignore_format=False):
    '''Method to delete user'''
    pass

  def detach_policies(self, username, delete=True):
    '''Method to detach policies'''
    pass

  def setup_user(self, uid, boundary='', tags=[]):
    '''Method to create a user'''
    # return username, access_key
    username = self.username_pattern.format(uid)
    credentials = {
      'AccessKeyId': self.iam_credentials.get('id'),
      'CreateDate': datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
      'SecretAccessKey': self.iam_credentials.get('secret'),
      'Status': 'Active',
      'UserName': username,
    }
    return username, credentials

  def set_inline_policy(self, policy_scheme, username, replace=True):
    '''Method to set inline policy'''
    pass

  def set_policy(self, policy_scheme, username, force=True, sufix='', tags=[]):
    '''Method to set policy'''
    pass
