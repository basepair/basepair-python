'''FTP driver'''

# General imports
import ftplib
import os
from time import sleep

# App imports
from .psv_ftp import PassiveFTP

MAX_RETRIES = 10

class FTP: # pylint: disable=too-few-public-methods
  '''FTP class'''

  def __init__(self, config):
    '''FTP constructor'''
    self.config = config
    self.client = self._connect()

  def _connect(self):
    '''Return connection'''
    #ftp_client = ftplib.FTP()
    ftp_client = PassiveFTP()
    ftp_client.connect(self.config.get('host'), self.config.get('port'))
    ftp_client.login(self.config.get('username'), self.config.get('password'))
    return ftp_client

  def download(self, remote_path, local_path):
    '''Download files'''
    dir_path = os.path.dirname(remote_path)
    file_name = os.path.basename(remote_path)
    max_retries, num_tries = self.config.get('max_retries', MAX_RETRIES), 0

    while max_retries > num_tries:
      try:
        hand = open(local_path, 'wb')
        # Change working directory of ftp drive
        self.client.cwd(f'/{dir_path}')
        # Download file to local machine
        self.client.retrbinary('RETR ' + file_name, hand.write)
        break
      except ftplib.error_temp:
        print('FTP temp error, reconnecting...')
        sleep(1)
        self.client = self._connect()
        num_tries += 1
      except Exception as error: # pylint: disable=broad-except
        print(f'FTP File download failed, try # {num_tries}')
        print(error)
        print(self.client)
        sleep(6)
        self.client = self._connect()
        print(self.client)
        num_tries += 1
  
  def download_directory(self, remote_path, local_path):
    '''method to download directory from ftp server'''
    local_sub_path = os.path.join(local_path, remote_path)
    if not os.path.exists(local_sub_path):
      os.makedirs(local_sub_path)   # Create local subdirectory mirroring remote structure

    # Change to the remote directory
    self.client.cwd(f'/{remote_path}')

    # List all files and directories in the current remote directory
    files = []
    self.client.retrlines('LIST', files.append)
    # Download files and subdirectories preserving structure
    for line in files:
      _, _, filename = line.rpartition(' ')
      if filename not in ('.', '..'):
        if self.is_directory(filename):
          self.download_directory(
            os.path.join(remote_path, filename),
            local_path
          )
        else:
          local_file_path = os.path.join(local_path, remote_path, filename)
          with open(local_file_path, 'wb') as local_file:
            self.client.retrbinary('RETR ' + filename, local_file.write)
    # Move back to the parent directory after download
    self.client.cwd('..')

  def is_directory(self, filename):
    '''helper to check if the current path is a directory while navigating the FTP server'''
    try:
      self.client.cwd(filename)
      self.client.cwd('..')
      return True
    except Exception:
      return False
