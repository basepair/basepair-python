from basepair.modules.aws import IAM

from basepair.modules.identity.driver import IdentityAbstract


class Driver(IdentityAbstract):
    def __init__(self, cfg=None):
        iam_settings = cfg.get('settings', {})
        prefix = iam_settings.get('prefix', None)
        self.iam_service = IAM({
            'credentials': iam_settings.get('credentials', None),
            'username_pattern': prefix + '{}' if prefix else None,
        })

    def delete_access_keys(self, username):
        return self.iam_service.delete_access_keys(username)

    def delete_inline_policies(self, username):
        return self.iam_service.delete_inline_policies(username)

    def delete_policy(self, policy_arn):
        return self.iam_service.delete_policy(policy_arn)

    def get_policy_versions(self, policy_arn):
        return self.iam_service.get_policy_versions(policy_arn)

    def delete_user(self, uid, ignore_format=False):
        return self.iam_service.delete_user(uid, ignore_format)

    def detach_policies(self, username, delete=True):
        return self.iam_service.detach_policies(username, delete)

    def setup_user(self, uid, boundary='', tags=[]):  # pylint: disable=dangerous-default-value,too-many-branches
        return self.iam_service.setup_user(uid, boundary, tags)

    def set_inline_policy(self, policy_scheme, username, replace=True):
        return self.iam_service.set_inline_policy(policy_scheme, username, replace)

    def set_policy(self, policy_scheme, username, force=True, sufix='', tags=[]):  # pylint: disable=too-many-arguments,dangerous-default-value
        return self.iam_service.set_policy(policy_scheme, username, force, sufix, tags)