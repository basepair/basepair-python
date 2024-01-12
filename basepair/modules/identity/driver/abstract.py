def raise_no_implemented():
  '''Helper to raise exception when call no implemented method'''
  raise Exception('Abstract method require to be implemented.')

class IdentityAbstract:

    def __init__(self, cfg=None):
        raise Exception('Abstract class cannot be instantiated.')

    def delete_access_keys(self, username):
        raise_no_implemented()

    def delete_inline_policies(self, username):
        raise_no_implemented()

    def delete_policy(self, policy_arn):
        raise_no_implemented()

    def get_policy_versions(self, policy_arn):
        raise_no_implemented()

    def delete_user(self, uid, ignore_format=False):
        raise_no_implemented()

    def detach_policies(self, username, delete=True):
        raise_no_implemented()

    def setup_user(self, uid, boundary='', tags=[]):  # pylint: disable=dangerous-default-value,too-many-branches
        raise_no_implemented()

    def set_inline_policy(self, policy_scheme, username, replace=True):
        raise_no_implemented()

    def set_policy(self, policy_scheme, username, force=True, sufix='', tags=[]):  # pylint: disable=too-many-arguments,dangerous-default-value
        raise_no_implemented()