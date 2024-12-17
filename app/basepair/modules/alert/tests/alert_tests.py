'''This module contain tests for alert module'''

# Libs import
import pytest
from allure import step

# App imports
from basepair.modules.alert import Alert

@pytest.mark.parametrize('alert_type', ['info', 'low', 'medium', 'high', 'critical'])
def test_alert_opsgenie(alert_type, mock_opsgenie_sdk):
  '''validates opsgenie alert driver'''

  with step('Arrange: initialize alert module'):
    alert = Alert.get_instance({
      'driver': 'opsgenie',
      'secret_key': 'whatever-because-mocked',
    })

  with step(f'Act: send {alert_type} alert'):
    msg = f'Test {alert_type}.'
    payload = {'details': {'key1': 'Val1'}}
    response = getattr(alert, alert_type)(msg, payload)

  with step('Assert: request succeded'):
    assert bool(response.get('request_id'))
