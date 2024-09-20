'''Driver for GitHub repositories'''

# Libs import
from opsgenie_sdk import AlertApi, CreateAlertPayload
from opsgenie_sdk.api_client import ApiClient
from opsgenie_sdk.configuration import Configuration

# App imports
from .abstract import AlertAbstract

class Instance(AlertAbstract):
  '''OPSGenie Implementation of Abstract class'''

  def critical(self, msg, payload):
    '''Send critical severity alert'''
    return self._send_alert(self._parse_payload(msg, payload, 'P1'))

  def high(self, msg, payload):
    '''Send high severity alert'''
    return self._send_alert(self._parse_payload(msg, payload, 'P2'))

  def info(self, msg, payload):
    '''Send very low severity alert'''
    return self._send_alert(self._parse_payload(msg, payload, 'P5'))

  def low(self, msg, payload):
    '''Send low severity alert'''
    return self._send_alert(self._parse_payload(msg, payload, 'P4'))

  def medium(self, msg, payload):
    '''Send medium severity alert'''
    return self._send_alert(self._parse_payload(msg, payload, 'P3'))

  def set_config(self, cfg):
    self.cfg = Configuration()
    self.cfg.api_key['Authorization'] = cfg.get('secret_key')
    self.api_client = ApiClient(configuration=self.cfg)
    self.alert_api = AlertApi(api_client=self.api_client)

  def _parse_payload(self, msg, payload, priority='P3'):
    '''Helper to parse payload'''
    payload = payload or {}
    payload['priority'] = priority
    payload['message'] = msg
    return payload

  def _send_alert(self, payload):
    '''Helper to send alerts'''
    return self.alert_api.create_alert(create_alert_payload=CreateAlertPayload(**payload))
