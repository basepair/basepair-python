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
    endpoint = self.endpoint
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
  '''Exception when file is in cold storage'''
  def __init__(self, key, restore_status, msg=None):
    self.restore_status = restore_status
    prefix = f'Could not download file: {key}.'
    message = {
      'restore_error': 'Could not start restore.',
      'restore_in_progress': 'Restore in progress. You should be able to download the file in a bit.',
      'restore_not_started': 'Could not start restore',
    }
    error = f'{prefix}\tCause: {msg or message.get(restore_status)}'
    super().__init__(error)
