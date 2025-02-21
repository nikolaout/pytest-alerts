import pytest
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
from pytest_alerts.slack import SlackConfig, slack_send_message, format_message
import requests

class MockOption:
    def __init__(self):
        # Shared options
        self.show_details = True
        self.hide_errors = False
        # Slack-specific options
        self.slack_webhook = "https://hooks.slack.com/services/TEST/TEST/TEST"
        self.slack_message_prefix = "Test Prefix"
        self.slack_suite_name = "Test Suite"
        self.slack_timeout = 10

class MockConfig:
    def __init__(self):
        self.option = MockOption()

@pytest.fixture
def slack_config():
    config = SlackConfig(
        hook="https://hooks.slack.com/services/TEST/TEST/TEST",
        message_prefix="Test Prefix",
        test_name="Test Suite",
        timeout=10
    )
    config.config = MockConfig()
    return config

def test_slack_config_initialization():
    hook = "https://hooks.slack.com/services/TEST/TEST/TEST"
    config = SlackConfig(hook=hook)
    assert config.hook == hook

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
def test_slack_send_message_success(mock_post, slack_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    test_result = MockTestResult()
    exitstatus = 0
    
    result = slack_send_message(test_result, slack_config, exitstatus)
    
    assert result is True
    mock_post.assert_called_once()
    assert mock_post.call_args[0][0] == slack_config.hook

@patch('requests.post')
def test_slack_send_message_failure(mock_post, slack_config):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    test_result = MockTestResult()
    exitstatus = 1
    
    result = slack_send_message(test_result, slack_config, exitstatus)
    
    assert result is False

def test_format_message(slack_config):
    slack_config.config.option.show_details = True
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
    
    message = format_message(test_result, slack_config, exitstatus)
    
    assert isinstance(message, dict)
    assert "attachments" in message
    assert len(message["attachments"]) == 1
    text = message["attachments"][0]["text"]
    
    assert "Test Prefix" in text
    assert "Status=Failed" in text
    assert "Passed=2" in text
    assert "Failed=1" in text
    assert "Skipped=1" in text
    assert "XFailed=1" in text
    assert "XPassed=1" in text
    assert "test_1" in text
    assert "AssertionError: test failed" in text
