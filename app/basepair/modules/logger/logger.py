'''Logger factory'''

# General imports
import importlib

INSTANCES = {}

class Logger(): # pylint: disable=too-few-public-methods
  '''Log factory class'''

  @staticmethod
  def get_instance(cfg={}): # pylint: disable=dangerous-default-value
    '''logger instantiation'''
    driver = cfg.get('driver', 'logbook')
    driver_module = importlib.import_module(f'basepair.modules.logger.drivers.{driver}')
    INSTANCES[driver] = INSTANCES.get(driver) or driver_module.Instance()
    INSTANCES[driver].set_config(cfg)
    return INSTANCES[driver]
