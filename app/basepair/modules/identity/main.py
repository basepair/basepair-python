import importlib


class Identity:
  '''Identity Class'''

  def __init__(self, cfg):
    '''Identity constructor'''
    driver = cfg.get('driver')
    module = importlib.import_module(f'basepair.modules.identity.drivers.{driver}')
    self.driver = module.Driver(cfg)

  def delete_access_keys(self, username):
    '''Method to delete access keys'''
    return self.driver.delete_access_keys(username)

  def delete_inline_policies(self, username):
    '''Method to delete inline policies'''
    return self.driver.delete_inline_policies(username)

  def delete_policy(self, policy_arn):
    '''Method to delete policies'''
    return self.driver.delete_policy(policy_arn)

  def get_policy_versions(self, policy_arn):
    '''Method to get policy version'''
    return self.driver.get_policy_versions(policy_arn)

  def delete_user(self, uid, ignore_format=False):
    '''Method to delete user'''
    return self.driver.delete_user(uid, ignore_format)

  def detach_policies(self, username, delete=True):
    '''Method to detach policies'''
    return self.driver.detach_policies(username, delete)

  def setup_user(self, uid, boundary='', tags=[]):  # pylint: disable=dangerous-default-value,too-many-branches
    '''Method to create user'''
    return self.driver.setup_user(uid, boundary, tags)

  def set_inline_policy(self, policy_scheme, username, replace=True):
    '''Method to set inline policy'''
    return self.driver.set_inline_policy(policy_scheme, username, replace)

  def set_policy(self, policy_scheme, username, force=True, sufix='', tags=[]):  # pylint: disable=too-many-arguments,dangerous-default-value
    '''Method to set policy'''
    return self.driver.set_policy(policy_scheme, username, force, sufix, tags)
