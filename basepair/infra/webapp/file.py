'''File webapp api wrapper'''
# General imports
import requests

# App imports
from .abstract import Abstract

class File(Abstract):
  '''Webapp File class'''
  def __init__(self, cfg):
    super(File, self).__init__(cfg)
    self.endpoint += 'files/'

  def start_restore(self, key, bucket=None, notification=False):
    '''Start the restore of the file'''
    return self._file_get_request('restore', key, bucket, notification)

  def storage_status(self, key, bucket=None):
    '''Get the storage status of the files using its key'''
    return self._file_get_request('check_restore_status', key, bucket)

  def _file_get_request(self, route, key, bucket=None, notification=False):
    '''Call the appropriate endpoint'''
    params = self.payload
    endpoint = 'http://amiay.local/api/v2/files/'
    try:
      response = requests.get(
        f'{endpoint}{route}?key={key}&bucket={bucket or ""}&notification={notification or ""}',
        params=params,
        verify=True,
        headers={'content-type': 'application/json'}
      )
      return self._parse_response(response)
    except Exception as error:
      return {'error': True, 'msg': error}

class FileInColdStorageError(Exception):
    pass
