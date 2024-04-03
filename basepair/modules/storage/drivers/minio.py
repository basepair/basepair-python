"""Driver for AWS S3 compute"""

# App import
from .aws_s3 import Driver as S3Driver
from .abstract import raise_no_implemented


class Driver(S3Driver):
    """Min IO Driver class"""
    def __init__(self, cfg=None):
        super().__init__(cfg)

    def get_lifecycle(self, bucket=None):
        """Get storage lifecycle"""
        raise_no_implemented("MinIO does not support lifecycle")

    def get_storage_context(self):
        """Get the context for Minio"""
        return {
            **super().get_storage_context(),
            'storage_driver': 'minio',
            'storage_url': self.storage_settings.get('endpoint_url'),
            'storage_sse_enabled': 'False'
        }

    def restore_from_cold(self, uri, days):
        """Restore file from cold storage"""
        raise_no_implemented("MinIO does not support restore from cold")

    def set_lifecycle(self, **kwargs):
        """Set storage lifecycle"""
        raise_no_implemented("MinIO does not support lifecycle")
