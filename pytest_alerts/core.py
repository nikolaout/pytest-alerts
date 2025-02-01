import pytest
from _pytest.terminal import TerminalReporter
from _pytest.config import Config
from _pytest.reports import TestReport
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import sys

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from .slack import slack_send_message, add_slack_options, SlackConfig
from .telegram import telegram_send_message, add_telegram_options, TelegramConfig

# Type alias for test report
TestReport: TypeAlias = TestReport

@dataclass
class TestResult:
    """Container for test execution results and details."""
    failed: int = 0
    passed: int = 0
    skipped: int = 0
    error: int = 0
    xfailed: int = 0
    xpassed: int = 0
    failed_tests: List[str] = field(default_factory=list)
    failed_details: Dict[str, str] = field(default_factory=dict)

def pytest_addoption(parser: pytest.Parser) -> None:
    """Add pytest-notify plugin options to the pytest command line."""
    # Add shared options first
    group = parser.getgroup('pytest-notify[shared]')
    group.addoption(
        '--show_details',
        action='store_true',
        help='Show error details in notifications'
    )
    group.addoption(
        '--hide_errors',
        action='store_true',
        help='Hide error details from notifications'
    )

    # Add platform-specific options
    add_slack_options(parser)
    add_telegram_options(parser)

def extract_error_message(report: TestReport) -> str:
    """Extract error message from test report in a safe manner."""
    try:
        if hasattr(report, 'longrepr'):
            if hasattr(report.longrepr, 'reprcrash'):
                return str(report.longrepr.reprcrash.message)
            return str(report.longrepr)
    except Exception:
        return "Error details unavailable"
    return "No error message"

@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(
    terminalreporter: TerminalReporter,
    exitstatus: int,
    config: Config
) -> None:
    """
    pytest hook to process test results and send notifications.
    
    Args:
        terminalreporter: Terminal reporter object containing test statistics
        exitstatus: Exit status of the test run
        config: pytest configuration object
    """
    yield

    # Skip processing for pytest-xdist workers
    if hasattr(terminalreporter.config, 'workerinput'):
        return

    test_result = TestResult()
    
    # Process test statistics
    stats = terminalreporter.stats
    failed_reports = stats.get('failed', [])
    test_result.failed = len(failed_reports)
    test_result.passed = len(stats.get('passed', []))
    test_result.skipped = len(stats.get('skipped', []))
    test_result.error = len(stats.get('error', []))
    test_result.xfailed = len(stats.get('xfailed', []))
    test_result.xpassed = len(stats.get('xpassed', []))

    # Collect failed test information
    test_result.failed_tests = [report.nodeid for report in failed_reports]
    test_result.failed_details = {
        report.nodeid: extract_error_message(report)
        for report in failed_reports
    }

    # Send notifications based on configuration
    if config.option.slack_webhook:
        slack_config = SlackConfig.from_pytest_config(config)
        slack_send_message(test_result, slack_config, exitstatus)
    
    if config.option.telegram_bot_token:
        telegram_config = TelegramConfig.from_pytest_config(config)
        telegram_send_message(test_result, telegram_config, exitstatus)
