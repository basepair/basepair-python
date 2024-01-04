'''Abstract class for storage drivers'''

def raise_no_implemented(msg='Abstract method require to be implemented.'):
  '''Helper to raise exception when call no implemented method'''
  raise Exception(msg)

# pylint: disable=no-self-use,unused-argument
class StorageAbstract:
  '''Abstract Driver class'''

  def __init__(self, cfg=None):
    '''Instance constructor'''
    raise Exception('Abstract class cannot be instantiated.')

  def bulk_delete(self, uris):
    '''Delete list of files by their uris'''
    raise_no_implemented()

  def delete(self, uri):
    '''Delete file from storage'''
    raise_no_implemented()

  def download(self, uri, callback=None, file=None):
    '''Download file from storage'''
    raise_no_implemented()

  def get_body(self, uri):
    '''Get file body'''
    raise_no_implemented()

  def get_head(self, uri):
    '''Get file head'''
    raise_no_implemented()

  def get_lifecycle(self, bucket=None):
    '''Get storage lifecycle'''
    raise_no_implemented()

  def get_public_url(self, uri):
    '''Get a public accessible url'''
    raise_no_implemented()

  def get_status(self, uri):
    '''Get the file status'''
    raise_no_implemented()

  def get_uri(self, key):
    '''Get uri using key and storage settings'''
    raise_no_implemented()

  def restore_from_cold(self, uri, days):
    '''Restore file from cold storage'''
    raise_no_implemented()

  def set_body(self, body, uri):
    '''Set file body'''
    raise_no_implemented()

  def set_lifecycle(self, **kwargs):
    '''Set storage lifecycle'''
    raise_no_implemented()

  def upload(self, file_name, full_path, force=False):
    '''Upload file to storage'''
    raise_no_implemented()
