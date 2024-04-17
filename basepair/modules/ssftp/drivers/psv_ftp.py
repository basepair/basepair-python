import ftplib
import socket


# Reference: https://stackoverflow.com/a/50066672/13056176
class PassiveFTP(ftplib.FTP):
  '''Custom FTP class for passive connection to ftp server'''
  def makepasv(self):
    '''Override makepasv because sometimes the ftp server return improper IP, when server is ill configured'''
    if self.af == socket.AF_INET:
      host, port = ftplib.parse227(self.sendcmd('PASV'))
    else:
      host, port = ftplib.parse229(self.sendcmd('EPSV'),self.sock.getpeername())
    if '0.0.0.0' == host:
      ''' this ip will be unroutable, we copy Filezilla and return the host instead '''
      host = self.host
    return host, port
