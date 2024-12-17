'''Sample webapp api wrapper'''

# Lib imports
import json
import os
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class Sample(Abstract):
  '''Webapp Sample class'''
  def __init__(self, cfg):
    super(Sample, self).__init__(cfg)
    self.endpoint += 'samples/'

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

  def by_name(self, name, project_id, cache=False, verify=True): # pylint: disable=dangerous-default-value
    '''Get detail of an resource'''
    if cache:
      filename = os.path.expanduser(cache)
      if os.path.exists(filename) and os.path.getsize(filename):
        return json.loads(open(filename, 'r').read().strip())

    try:
      params = {'name': name, 'project_id': project_id}
      params.update(self.payload)
      response = requests.get(
        '{}by_name'.format(self.endpoint),
        params=params,
        # params={'name': name, 'project_id': project_id, **self.payload}, #TODO: Uncomment when everything moved to py3
        verify=verify,
      )
      parsed = self._parse_response(response)

      # save in cache if required
      if cache and parsed and not parsed.get('error'):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
          os.makedirs(directory)
        with open(filename, 'w') as handle:
          handle.write(json.dumps(parsed, indent=2))
      return parsed
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}
