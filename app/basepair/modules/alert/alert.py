'''Alert factory'''

# General imports
import importlib

INSTANCES = {}

class Alert(): # pylint: disable=too-few-public-methods
  '''Alert factory class'''

  @staticmethod
  def get_instance(cfg=None): # pylint: disable=dangerous-default-value
    '''Alert instantiation'''
    if cfg is None:
      cfg = {}
    driver = cfg.get('driver')
    driver_module = importlib.import_module(f'basepair.modules.alert.drivers.{driver}')
    INSTANCES[driver] = INSTANCES.get(driver) or driver_module.Instance(cfg)
    INSTANCES[driver].set_config(cfg)
    return INSTANCES[driver]
