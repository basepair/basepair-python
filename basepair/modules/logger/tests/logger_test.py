'''This module contain tests for alert module'''

# General imports
import os

# Libs import
import pytest
from allure import step

# App imports
from basepair.modules.logger import Logger

LOG_FILE = '/tmp/test_logger_logbook.log'

@pytest.mark.parametrize('log_type', ['debug', 'info', 'warning', 'error', 'exception'])
def test_logger_logbook(log_type):
  '''validates rollbar logger driver'''
  with step('Arrange: initialize logbook logger module'):
    logger = Logger.get_instance({
      'driver': 'logbook',
      'log_file': LOG_FILE
    })

  with step(f'Act: log {log_type}'):
    msg = f'Test {log_type}.'
    payload = {'details': {'key1': 'Val1'}}
    print(log_type, log_type == ' exception')
    if log_type == 'exception':
      getattr(logger, log_type)(payload)
    else:
      getattr(logger, log_type)(msg, payload)

  with step('Assert: logbook file exist'):
    assert os.path.isfile(LOG_FILE)

  if log_type != 'exception':
    with step('Assert: log added to file'):
      with open(LOG_FILE, 'r', encoding='utf-8') as file:
        assert msg in file.read()

@pytest.mark.parametrize('log_type', ['debug', 'info', 'warning', 'error', 'exception'])
def test_logger_rollbar(log_type, mock_rollbar_report_exc_info, mock_rollbar_report_message):
  '''validates rollbar logger driver'''
  with step('Arrange: initialize rollbar logger module'):
    logger = Logger.get_instance({'driver': 'rollbar'})

  with step(f'Act: log {log_type}'):
    msg = f'Test {log_type}.'
    payload = {'details': {'key1': 'Val1'}}
    if log_type == 'exception':
      getattr(logger, log_type)(payload)
    else:
      getattr(logger, log_type)(msg, payload)

