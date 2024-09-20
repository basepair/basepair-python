"""Driver for AWS Health Omics"""

# General imports
import time

# Libs import
from basepair.modules.aws import HOS
from basepair.modules.aws import S3

# App import
from .aws_s3 import Driver as S3Driver

RESTORE_ERROR = 'restore_error'
RESTORE_IN_PROGRESS = 'restore_in_progress'
RESTORE_NOT_REQUIRED = 'restore_not_required'
RESTORE_NOT_STARTED = 'restore_not_started'


class Driver(S3Driver):
    """AWS Health Omics Driver class"""

    def __init__(self, cfg=None):
        """Instance constructor"""
        super().__init__(cfg=cfg)  # calling parent class(S3) constructor to create the S3 client

        storage_settings = cfg.get('settings', {})
        self.hos_service = HOS({
            'credentials': cfg.get('credentials'),
            'reference_store_id': storage_settings.get('ho_reference_store_id'),
            'sequence_store_id': storage_settings.get('ho_sequence_store_id'),
            'region': storage_settings.get('ho_region'),
            'role_arn': storage_settings.get('ho_import_export_role_arn'),
        })

    def get_public_url(self, uri):
        """Get the public URL of the file"""
        if not self._is_health_omics_uri(uri):
            # If the URI is not a Health Omics URI, then call the S3 driver method
            return super().get_public_url(uri)

        # If the URI is a Health Omics URI, then get the public URL of the file with bucket.
        # Note: The bucket is an S3 access point URL not actual bucket name.
        # But presign will work with S3 access point URL as bucket name.
        bucket = S3.get_bucket_from_uri(uri)
        key = S3.get_key_from_uri(uri, bucket=bucket)
        return self.s3_service.get_self_signed(key, bucket=bucket)

    def get_service(self):
        return self.hos_service

    def get_storage_context(self):
        """Get the context for AWS HOS"""
        return {
            **super().get_storage_context(),
            'storage_driver': 'aws_hos'
        }

    def get_status(self, uri):
        """Get the file status"""
        if not self._is_health_omics_uri(uri):
            # If the URI is not a Health Omics URI, then call the S3 driver method
            return super().get_status(uri)

        # If the URI is a Health Omics URI, then get the read set metadata and return the status
        read_set_id = uri.split('/')[-2]
        metadata = self.hos_service.get_read_set_metadata(read_set_id)
        storage_status = metadata.get('status')

        if storage_status == 'ARCHIVED':
            return RESTORE_NOT_STARTED, storage_status
        elif storage_status == 'ACTIVE':
            return RESTORE_NOT_REQUIRED, storage_status
        elif storage_status == 'ACTIVATING':
            return RESTORE_IN_PROGRESS, storage_status
        else:
            return RESTORE_ERROR, storage_status

    def restore_from_cold(self, uri, days):
        """Restore file from cold storage"""
        if not self._is_health_omics_uri(uri):
            # If the URI is not a Health Omics URI, then call the S3 driver method
            return super().restore_from_cold(uri, days)

        # If the URI is a Health Omics URI, then start the read set activation job
        read_set_id = uri.split('/')[-2]
        max_attempts = 100
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                return self.hos_service.start_read_set_activation_job([read_set_id])
            except Exception:
                time.sleep(60)
        raise Exception("Failed to start read set activation job.")


    @staticmethod
    def _is_health_omics_uri(uri):
        """Check if uri is a S3 access point URL. Because Health Omics URIs are generated via S3 access points."""
        return '-s3alias' in uri
