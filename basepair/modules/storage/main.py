"""Storage manager"""

# General imports
import importlib


class Storage:
    """Storage class"""
    def __init__(self, cfg):
        """Storage constructor"""
        driver = cfg.get('driver') or 'aws_s3'
        module = importlib.import_module(f'basepair.modules.storage.drivers.{driver}')
        self.driver = module.Driver(cfg)

    def bulk_delete(self, uris):
        """Delete list of files by their uris"""
        return self.driver.bulk_delete(uris)

    def delete(self, uri):
        """Delete file from storage"""
        return self.driver.delete(uri)

    def download(self, uri, callback=None, file=None):
        """Download file from storage"""
        return self.driver.download(uri, callback, file)

    def get_body(self, uri):
        """Get file body"""
        return self.driver.get_body(uri)

    def get_head(self, uri):
        """Get file head"""
        return self.driver.get_head(uri)

    def get_lifecycle(self, bucket=None):
        """Get storage lifecycle"""
        return self.driver.get_lifecycle(bucket)

    def get_public_url(self, uri):
        """Get a public accessible url"""
        return self.driver.get_public_url(uri)

    def get_service(self):
        """Get storage service object"""
        return self.driver.get_service()

    def get_status(self, uri):
        """Get the file status"""
        return self.driver.get_status(uri)

    def get_storage_context(self):
        """Get the storage context"""
        return self.driver.get_storage_context()

    def get_uri(self, key):
        """Get uri using key and storage settings"""
        return self.driver.get_uri(key)

    def list(self, prefix, bucket=None):
        """List files in prefix"""
        return self.driver.list(prefix, bucket)

    def restore_files_from_cold(self, uris, days):
        """Restore files from cold storage"""
        return self.driver.restore_files_from_cold(uris, days)

    def restore_from_cold(self, uri, days):
        """Restore file from cold storage"""
        return self.driver.restore_from_cold(uri, days)

    def set_body(self, body, uri):
        """Set file body"""
        return self.driver.set_body(body, uri)

    def set_lifecycle(self, **kwargs):
        """Set storage lifecycle"""
        return self.driver.set_lifecycle(kwargs)

    def upload(self, file_name, full_path, **kwargs):
        """Upload file to storage"""
        return self.driver.upload(file_name, full_path, **kwargs)
    
    def upload_file_obj(self, file_obj, file_path, **kwargs):
        """Upload file object to storage"""
        return self.driver.upload_file_obj(file_obj, file_path, **kwargs)
