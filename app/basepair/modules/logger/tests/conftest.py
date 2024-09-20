''' this module contains fixtures for logger resources tests '''

# Import Libs
import pytest
import rollbar

@pytest.fixture
def mock_rollbar_report_exc_info(monkeypatch):
  ''' mock rollbar report_message '''

  def mock_report_exc_info(exc_info=None, request=None, extra_data=None, payload_data=None, level=None, **kw):  # pylint: disable=unused-argument
    print('Mock rollbar.report_exc_info:\n')
    print(exc_info, extra_data, payload_data)

  monkeypatch.setattr(rollbar, 'report_exc_info', mock_report_exc_info)

@pytest.fixture
def mock_rollbar_report_message(monkeypatch):
  ''' mock rollbar report_message '''

  def mock_report_message(message, level='error', request=None, extra_data=None, payload_data=None, **kw):  # pylint: disable=unused-argument
    print('Mock rollbar.report_message:\n')
    print(message, level, extra_data, payload_data)

  monkeypatch.setattr(rollbar, 'report_message', mock_report_message)
