'''File webapp api wrapper'''

# General imports
import requests
import json

# App imports
from .abstract import Abstract

class File(Abstract):
  '''Webapp File class'''
  def __init__(self, cfg):
    super(File, self).__init__(cfg)
    self.endpoint += 'files/'

  def get_presigned_url(self, key):
    '''Method to call the http request to sign the url'''
    payload = {'key': key}
    return self._file_post_request('get_presigned_url', payload)

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