'''Analysis webapp api wrapper'''

# General imports
import json

# Lib imports
import requests

# App imports
from .abstract import Abstract
from basepair.helpers import eprint

class Analysis(Abstract):
  '''Webapp Analysis class'''
  def __init__(self, cfg):
    super(Analysis, self).__init__(cfg)
    self.endpoint += 'analyses/'

  def save(self, obj_id=None, params={}, payload={}, verify=True): # pylint: disable=dangerous-default-value
    '''Save or update resource'''
    params.update(self.payload)
    try:
      response = getattr(requests, 'put' if obj_id else 'post')(
        '{}{}'.format(self.endpoint, obj_id or ''),
        data=json.dumps(payload),
        headers=self.headers,
        params=params,
        verify=verify,
      )
      response = self._parse_response(response)
      if response and response.get('error'):

        if response.get('error') and isinstance(response.get('error'), dict):
          response = response['error']

          if response.get('error_msgs'):
            eprint('ERROR: {}'.format(response['error_msgs']))

          if response.get('warning_msgs'):
            eprint('WARNING: {}'.format(response['warning_msgs']))

      return response
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}
