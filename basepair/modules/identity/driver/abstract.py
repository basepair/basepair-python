def raise_no_implemented():
  '''Helper to raise exception when call no implemented method'''
  raise Exception('Abstract method require to be implemented.')

class IdentityAbstract:
  '''Identity Class'''

  def __init__(self, cfg=None):
    '''Identity constructor'''
    raise Exception('Abstract class cannot be instantiated.')

  def delete_access_keys(self, username):
    '''Method to delete the access keys'''
    raise_no_implemented()

  def delete_inline_policies(self, username):
    '''Method to delete inline policies'''
    raise_no_implemented()

  def delete_policy(self, policy_arn):
    '''Method to delete a policy'''
    raise_no_implemented()

  def get_policy_versions(self, policy_arn):
    '''Method to get policy version'''
    raise_no_implemented()

  def delete_user(self, uid, ignore_format=False):
    '''Method to delete user'''
    raise_no_implemented()

  def detach_policies(self, username, delete=True):
    '''Method to detach policies'''
    raise_no_implemented()

  def setup_user(self, uid, boundary='', tags=[]):  # pylint: disable=dangerous-default-value,too-many-branches
    '''Method to create a user'''
    raise_no_implemented()

  def set_inline_policy(self, policy_scheme, username, replace=True):
    '''Method to create a inline policy'''
    raise_no_implemented()

  def set_policy(self, policy_scheme, username, force=True, sufix='', tags=[]):  # pylint: disable=too-many-arguments,dangerous-default-value
    '''Method to create a policy'''
    raise_no_implemented()
