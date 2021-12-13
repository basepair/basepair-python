'''Analysis webapp api wrapper'''

# Lib imports
import json
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class Analysis(Abstract):
  '''Webapp Analysis class'''
  def __init__(self, cfg):
    super(Analysis, self).__init__(cfg)
    self.endpoint += 'analyses/'

  def bulk_start(self, payload={}, verify=True):
    '''Import sample from s3'''
    try:
      response = requests.post(
        '{}bulk_start'.format(self.endpoint),
        data=json.dumps(payload),
        headers=self.headers,
        params=self.payload,
        verify=verify,
      )
      return self._parse_response(response)
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}

  def reanalyze(self, payload={}, verify=True):
    '''Restart analysis'''
    try:
      response = requests.post(
        '{}reanalyze'.format(self.endpoint),
        data=json.dumps(payload),
        headers=self.headers,
        params=self.payload,
        verify=verify,
      )
      return self._parse_response(response)
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}
