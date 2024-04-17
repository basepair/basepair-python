'''SFTP driver'''

# General imports
import paramiko

class SFTP: # pylint: disable=too-few-public-methods
  '''FTP class'''

  def __init__(self, config):
    '''FTP constructor'''
    self.config = config
    self.client = self._connect()

  def _connect(self):
    '''Return connection'''
    ftp_client = paramiko.SSHClient()
    ftp_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ftp_client.connect(
      self.config.get('host'),
      password=self.config.get('password'),
      port=self.config.get('port'),
      username=self.config.get('username'),
    )
    return ftp_client.open_sftp()

  def download(self, remote_path, local_path):
    '''Download files'''
    try:
      self.client.get(remote_path, local_path)
    except Exception as error: # pylint: disable=broad-except
      print(f'SFTP File download failed: {error}')
