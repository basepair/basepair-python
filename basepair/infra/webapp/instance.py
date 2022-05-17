'''Instance webapp api wrapper'''

# Lib imports
import json
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class Instance(Abstract):
  '''Webapp Instance class'''
  def __init__(self, cfg):
    super(Instance, self).__init__(cfg)
    self.endpoint += 'instances/'

  def get_instances(self, payload={}, verify=True):
    '''Get available instances'''
    try:
      response = requests.get(
        self.endpoint,
        data=json.dumps(payload),
        headers=self.headers,
        params=self.payload,
        verify=verify,
      )
      return self._parse_response(response)
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}