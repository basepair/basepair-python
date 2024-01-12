from datetime import datetime

from basepair.modules.identity.driver import IdentityAbstract


class Driver(IdentityAbstract):
    def __init__(self, cfg=None):
        self.iam_settings = cfg.get('settings', {})
        self.iam_credentials = cfg.get('credentials', {})
        self.username_pattern = cfg.get('username_pattern') or '_tmp_{}'

    def delete_access_keys(self, username):
        pass

    def delete_inline_policies(self, username):
        pass

    def delete_policy(self, policy_arn):
        pass

    def get_policy_versions(self, policy_arn):
        pass

    def delete_user(self, uid, ignore_format=False):
        pass

    def detach_policies(self, username, delete=True):
        pass

    def setup_user(self, uid, boundary='', tags=[]):
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
        pass

    def set_policy(self, policy_scheme, username, force=True, sufix='', tags=[]):
        pass