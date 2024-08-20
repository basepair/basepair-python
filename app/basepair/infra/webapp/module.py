'''Module webapp api wrapper'''
import requests
# App imports
from .abstract import Abstract
from basepair.helpers import eprint

class Module(Abstract):
  '''Webapp Module class'''
  def __init__(self, cfg):
    super(Module, self).__init__(cfg)
    self.api_endpoint = '{}pipelines/get_module'.format(self.endpoint)
    self.endpoint += 'modules/'

  def get_pipeline_modules(self, obj_id, cache=False, params={}, verify=True): # pylint: disable=dangerous-default-value
    '''Get modules of an pipeline'''
    params.update(self.payload)
    try:
      response = requests.get(
        '{}?workflow={}'.format(self.api_endpoint, obj_id),
        params=params,
        verify=verify,
      )
      parsed = self._parse_obj_response(response, obj_id)
      return parsed.get('objects')
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}
