'''Webapp API'''

# General imports
import json
import os

# Lib imports
import requests

# App imports
from basepair.helpers import eprint

class Abstract(object):
  '''Webapp abastract class'''
  def __init__(self, cfg):
    protocol = 'https' if cfg.get('ssl', True) else 'http'
    self.endpoint = protocol + '://' + cfg.get('host') + cfg.get('prefix')
    self.payload = {
      'username': cfg.get('username'),
      'api_key': cfg.get('key')
    }
    self.headers = {'content-type': 'application/json'}

  def delete(self, obj_id, verify=True):
    '''Delete resource'''
    try:
      response = requests.delete(
        '{}{}'.format(self.endpoint, obj_id),
        params=self.payload,
        verify=verify
      )
      return self._parse_response(response)
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}

  def get(self, obj_id, cache=False, params={}, verify=True): # pylint: disable=dangerous-default-value
    '''Get detail of an resource'''
    if cache:
      filename = os.path.expanduser(cache)
      if os.path.exists(filename) and os.path.getsize(filename):
        return json.loads(open(filename, 'r').read().strip())

    params.update(self.payload)
    try:
      response = requests.get(
        self.resource_url(obj_id),
        params=params,
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

  def list(self, params={'limit': 100}, verify=True): # pylint: disable=dangerous-default-value
    '''Get a list of items'''
    params.update(self.payload)
    try:
      response = requests.get(
        self.endpoint.rstrip('/'),
        params=params,
        verify=verify,
      )
      return self._parse_response(response)
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}

  def list_all(self): # pylint: disable=dangerous-default-value
    '''Get a list of all items'''
    item_list = []
    limit = 500
    offset = 0
    total_count = 1
    while len(item_list) < total_count:
      response = self.list({'limit': limit, 'offset': offset})
      if response.get('error'):
        return {'error': True, 'msg': response.get('msg')}
      total_count = response.get('meta', {}).get('total_count')
      item_list += response.get('objects')
      offset += limit
    return item_list

  def resource_url(self, obj_id):
    '''Generate resource uri from obj id'''
    return '{}{}'.format(self.endpoint, obj_id)

  def save(self, obj_id=None, params={}, payload={}, verify=True): # pylint: disable=dangerous-default-value
    '''Save or update resource'''
    params.update(self.payload)
    try:
      response = getattr(requests, 'put' if obj_id else 'post')(
        self.resource_url(obj_id) if obj_id else self.endpoint,
        data=json.dumps(payload),
        headers=self.headers,
        params=params,
        verify=verify,
      )
      return self._parse_response(response)
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}

  @classmethod
  def _parse_response(cls, response):
    '''General response parser'''
    error_msgs = {
      401: 'You don\'t have access to this resource.',
      404: 'Resource not found.',
      500: 'Error retrieving data from API!'
    }

    if response.status_code in error_msgs:
      eprint('ERROR: {}'.format(error_msgs[response.status_code]))
      return {'error': True, 'msg': error_msgs[response.status_code]}

    if response.status_code == 204:  # for delete response
      return {'error': False}

    try:
      response = response.json()

      error = response and response.get('error')
      if error and isinstance(error, dict):
        response = error

        if response.get('error_msgs'):
          eprint('ERROR: {}'.format(response['error_msgs']))

        if response.get('warning_msgs'):
          eprint('WARNING: {}'.format(response['warning_msgs']))

      return response
    except json.decoder.JSONDecodeError as error:
      msg = 'ERROR: Not able to parse response: {}.'.format(error)
      eprint(msg)
      return {'error': True, 'msg': msg}
