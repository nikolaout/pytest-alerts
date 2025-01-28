import pytest
from unittest.mock import patch, MagicMock
from pytest_alerts.core import TestResult
from pytest_alerts.slack import SlackConfig
from pytest_alerts.telegram import TelegramConfig


def test_test_result_initialization():
    """Test that TestResult is properly initialized with default values."""
    result = TestResult()
    assert result.failed == 0
    assert result.passed == 0
    assert result.skipped == 0
    assert result.error == 0
    assert result.xfailed == 0
    assert result.xpassed == 0
    assert result.failed_tests == []
    assert result.failed_details == {}

@pytest.fixture
def mock_config():
    config = MagicMock()
    # Slack options
    config.option.slack_hook = "https://hooks.slack.com/services/xxx/yyy/zzz"
    config.option.slack_message_prefix = "Test Run"
    config.option.slack_test_name = "Test Suite"
    config.option.slack_timeout = 10
    # Telegram options
    config.option.telegram_bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    config.option.telegram_chat_id = "12345678"
    config.option.telegram_message_prefix = "Test Run"
    config.option.telegram_test_name = "Test Suite"
    config.option.telegram_timeout = 10
    # Shared options
    config.option.show_details = True
    config.option.hide_errors = False
    return config

@pytest.fixture
def mock_test_result():
    result = TestResult()
    result.failed = 1
    result.passed = 2
    result.skipped = 0
    result.error = 0
    result.xfailed = 0
    result.xpassed = 0
    result.failed_tests = ["test_something"]
    result.failed_details = {
        "test_something": "AssertionError: expected True but got False"
    }
    return result

@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock:
        mock.return_value = MagicMock()
        mock.return_value.status_code = 200
        mock.return_value.raise_for_status.return_value = None
        yield mock

def test_slack_message_formatting(mock_test_result, mock_config):
    """Test that Slack messages are properly formatted."""
    from pytest_alerts.slack import format_message
    
    slack_config = SlackConfig.from_pytest_config(mock_config)
    message = format_message(mock_test_result, slack_config, exitstatus=1)
    
    assert message is not None
    attachment = message['attachments'][0]
    assert attachment['color'] == '#dc3545'  # Error color
    text = attachment['text']
    assert 'Test Suite: Test Suite' in text
    assert 'Status=Failed' in text
    assert 'Failed=1' in text
    assert 'test_something' in text
    assert 'AssertionError' in text

def test_telegram_message_formatting(mock_test_result, mock_config):
    """Test that Telegram messages are properly formatted."""
    from pytest_alerts.telegram import format_message
    
    telegram_config = TelegramConfig.from_pytest_config(mock_config)
    message = format_message(mock_test_result, telegram_config, exitstatus=1)
    
    assert message is not None
    assert '📢 <b>Test Run</b>' in message
    assert '❌ <b>Status: FAILED</b>' in message
    assert 'Failed Tests Details' in message
    assert '<code>test_something</code>' in message
    assert '<i>AssertionError: expected True but got False</i>' in message

def test_slack_send_message(mock_test_result, mock_config, mock_requests):
    """Test that Slack messages are properly sent."""
    from pytest_alerts.slack import slack_send_message
    
    slack_config = SlackConfig.from_pytest_config(mock_config)
    slack_send_message(mock_test_result, slack_config, exitstatus=1)
    
    mock_requests.assert_called_once()
    args, kwargs = mock_requests.call_args
    assert kwargs.get('json') is not None
    assert slack_config.hook in args[0]
    assert kwargs.get('timeout') == slack_config.timeout

def test_telegram_send_message(mock_test_result, mock_config, mock_requests):
    """Test that Telegram messages are properly sent."""
    from pytest_alerts.telegram import telegram_send_message
    
    telegram_config = TelegramConfig.from_pytest_config(mock_config)
    telegram_send_message(mock_test_result, telegram_config, exitstatus=1)
    
    mock_requests.assert_called_once()
    args, kwargs = mock_requests.call_args
    assert kwargs.get('json') is not None
    assert telegram_config.bot_token in args[0]
    assert kwargs.get('timeout') == telegram_config.timeout

def test_successful_run_formatting(mock_config):
    """Test message formatting for successful test runs."""
    from pytest_alerts.slack import format_message
    
    result = TestResult()
    result.passed = 5
    slack_config = SlackConfig.from_pytest_config(mock_config)
    message = format_message(result, slack_config, exitstatus=0)
    
    assert message is not None
    attachment = message['attachments'][0]
    text = attachment['text']
    assert 'Status=Passed' in text
    assert 'Passed=5' in text
    assert attachment['color'] == '#36a64f'  # Success color

def test_failed_run_formatting(mock_config):
    """Test message formatting for failed test runs."""
    from pytest_alerts.slack import format_message
    
    result = TestResult()
    result.failed = 1
    result.passed = 4
    slack_config = SlackConfig.from_pytest_config(mock_config)
    message = format_message(result, slack_config, exitstatus=1)
    
    assert message is not None
    attachment = message['attachments'][0]
    text = attachment['text']
    assert 'Status=Failed' in text
    assert 'Failed=1' in text
    assert 'Passed=4' in text
    assert attachment['color'] == '#dc3545'  # Error color
