''' this module contains fixtures for alert resources tests '''

# Import Libs
import pytest
from opsgenie_sdk import AlertApi

@pytest.fixture
def mock_opsgenie_sdk(monkeypatch):
  ''' mock opsgenie_sdk create_alert '''
  def mock_init(obj, api_client):
    print('Mock AlertApi:', api_client)

  def mock_create_alert(self, create_alert_payload):  # pylint: disable=unused-argument
    print('Mock AlertApi.create_alert:\n', create_alert_payload)
    return {
      'data': None,
      'request_id': '234f4632-af6f-4b73-9d06-681882b4f782',
      'result': 'Request will be processed',
      'took': 0.007
    }

  monkeypatch.setattr(AlertApi, '__init__', mock_init)
  monkeypatch.setattr(AlertApi, 'create_alert', mock_create_alert)
