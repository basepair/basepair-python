'''SSFTP general ftp client'''

# General imports
import importlib

class SSFTP: # pylint: disable=too-few-public-methods
  '''SSFTP class'''

  def __init__(self, config):
    '''SSFTP constructor'''
    driver = config.get('driver', 'ftp')
    driver_module = importlib.import_module(f'basepair.modules.ssftp.drivers.{driver}')
    self.driver = getattr(driver_module, driver.upper())(config)

  def download(self, remote_path, local_path):
    '''Download file'''
    return self.driver.download(remote_path, local_path)

  def download_directory(self, remote_path, local_path):
    '''Download file'''
    return self.driver.download_directory(remote_path, local_path)
