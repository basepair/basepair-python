'''Upload webapp api wrapper'''

# General imports
import json

# Lib imports
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class Upload(Abstract):
  '''Webapp Upload class'''
  def __init__(self, cfg):
    super(Upload, self).__init__(cfg)
    self.endpoint += 'uploads/'

  def bulk_import(self, payload={}, verify=True):
    '''Import sample from s3'''
    try:
      response = requests.post(
        '{}bulk_import'.format(self.endpoint),
        data=json.dumps(payload),
        headers=self.headers,
        params=self.payload,
        verify=verify,
      )
      return self._parse_response(response)
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}
