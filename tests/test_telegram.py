import pytest
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
from pytest_alerts.telegram import TelegramConfig, telegram_send_message, format_message
import requests

class MockOption:
    def __init__(self):
        # Telegram-specific options
        self.telegram_bot_token = "test_token"
        self.telegram_chat_id = "test_chat_id"
        self.telegram_message_prefix = "Test Prefix"
        self.telegram_test_name = "Test Suite"
        self.telegram_timeout = 10
        # Shared options
        self.show_details = True
        self.hide_errors = False

class MockConfig:
    def __init__(self):
        self.option = MockOption()

@pytest.fixture
def telegram_config():
    config = TelegramConfig(
        bot_token="test_token",
        chat_id="test_chat_id",
        message_prefix="Test Prefix",
        test_name="Test Suite"
    )
    config.config = MockConfig()
    return config

def test_telegram_config_initialization():
    bot_token = "test_token"
    chat_id = "test_chat_id"
    config = TelegramConfig(bot_token=bot_token, chat_id=chat_id)
    assert config.bot_token == bot_token
    assert config.chat_id == chat_id

@dataclass
class MockTestResult:
    passed: int = 1
    failed: int = 0
    skipped: int = 0
    error: int = 0
    xfailed: int = 0
    xpassed: int = 0
    duration: float = 10.5
    user: str = "test_user"
    nodeid: str = "test_module.py::test_function"
    failed_tests: list = None
    failed_details: dict = None

    def __post_init__(self):
        if self.failed_tests is None:
            self.failed_tests = []
        if self.failed_details is None:
            self.failed_details = {}

@patch('requests.post')
def test_telegram_send_message_success(mock_post, telegram_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    mock_post.return_value = mock_response

    test_result = MockTestResult()
    exitstatus = 0
    
    result = telegram_send_message(test_result, telegram_config, exitstatus)
    
    assert result is True
    mock_post.assert_called_once()
    expected_url = f"https://api.telegram.org/bottest_token/sendMessage"
    assert mock_post.call_args[0][0] == expected_url

@patch('requests.post')
def test_telegram_send_message_failure(mock_post, telegram_config):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"ok": False, "description": "Bad Request"}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    test_result = MockTestResult()
    exitstatus = 1
    
    result = telegram_send_message(test_result, telegram_config, exitstatus)
    
    assert result is False

def test_format_message(telegram_config):
    test_result = MockTestResult(
        passed=2, 
        failed=1, 
        skipped=1, 
        xfailed=1, 
        xpassed=1,
        failed_tests=["test_1"],
        failed_details={"test_1": "AssertionError: test failed"}
    )
    exitstatus = 1
    
    message = format_message(test_result, telegram_config, exitstatus)
    
    assert isinstance(message, str)
    assert "Test Prefix" in message
    assert "Status: FAILED" in message
    assert " PASSED:   2" in message
    assert " FAILED:   1" in message
    assert " SKIPPED:  1" in message
    assert " XFailed: 1" in message
    assert " XPassed: 1" in message
    assert "AssertionError: test failed" in message
