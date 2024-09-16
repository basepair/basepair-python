'''File webapp api wrapper'''
import json
import requests

# App imports
from .abstract import Abstract

class File(Abstract):
  '''Webapp File class'''
  def __init__(self, cfg):
    super(File, self).__init__(cfg)
    self.endpoint += 'files/'

  def start_restore(self, key):
    '''Start the restore of the file'''
    return self._file_get_request('start_restore', key)

  def storage_status(self, key):
    '''Get the storage status of the files using its key'''
    return self._file_get_request('storage_status', key)

  def _file_get_request(self, route, key):
    '''Call the appropriate endpoint'''
    params = self.payload
    params.update({'key': key})
    try:
      response = requests.get(
        '{}{}'.format(self.endpoint, route),
        params=params,
        verify=True,
        headers={'content-type': 'application/json'}
      )
      return self._parse_response(response)
    except Exception as error:
      print(f'ERROR: While getting the storage status of {key} at endpoint: {self.endpoint}storage_status')
      return {'error': True, 'msg': error}
