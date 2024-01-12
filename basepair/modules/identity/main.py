import importlib


class Identity:
    def __init__(self, cfg):
        '''Identity constructor'''
        driver = cfg.get('driver')
        module = importlib.import_module(f'infra.identity.driver.{driver}')
        self.driver = module.Driver(cfg)

    def delete_access_keys(self, username):
        return self.driver.delete_access_keys(username)

    def delete_inline_policies(self, username):
        return self.driver.delete_inline_policies(username)

    def delete_policy(self, policy_arn):
        return self.driver.delete_policy(policy_arn)

    def get_policy_versions(self, policy_arn):
        return self.driver.get_policy_versions(policy_arn)

    def delete_user(self, uid, ignore_format=False):
        return self.driver.delete_user(uid, ignore_format)

    def detach_policies(self, username, delete=True):
        return self.driver.detach_policies(username, delete)

    def setup_user(self, uid, boundary='', tags=[]):  # pylint: disable=dangerous-default-value,too-many-branches
        return self.driver.setup_user(uid, boundary, tags)

    def set_inline_policy(self, policy_scheme, username, replace=True):
        return self.driver.set_inline_policy(policy_scheme, username, replace)

    def set_policy(self, policy_scheme, username, force=True, sufix='', tags=[]):  # pylint: disable=too-many-arguments,dangerous-default-value
        return self.driver.set_policy(policy_scheme, username, force, sufix, tags)