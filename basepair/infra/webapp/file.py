'''File webapp api wrapper'''
# General imports
import json
import requests

# App imports
from .abstract import Abstract

class File(Abstract):
  '''Webapp File class'''
  def __init__(self, cfg):
    super(File, self).__init__(cfg)
    self.endpoint += 'files/'

  def start_restore(self, key, notification=False):
    '''Start the restore of the file'''
    payload = {'key': key, 'notification': notification,}
    return self._file_post_request('restore', payload)

  def storage_status(self, key):
    '''Get the storage status of the files using its key'''
    payload = {'key': key}
    return self._file_post_request('check_restore_status', payload)

  def _file_post_request(self, route, payload):
    '''Call the appropriate endpoint'''
    try:
      response = requests.post(
        f'{self.endpoint}{route}',
        data=json.dumps(payload),
        params=self.payload,
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
