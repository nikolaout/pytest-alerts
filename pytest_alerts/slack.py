from dataclasses import dataclass
import requests

@dataclass
class SlackConfig:
    """Configuration for Slack notifications."""
    hook: str = None
    message_prefix: str = None
    test_name: str = None
    timeout: int = 10
    config: object = None

    @classmethod
    def from_pytest_config(cls, config):
        """Create SlackConfig from pytest config."""
        return cls(
            hook=config.option.slack_hook,
            message_prefix=config.option.slack_message_prefix,
            test_name=config.option.slack_test_name,
            timeout=config.option.slack_timeout,
            config=config
        )

def add_slack_options(parser):
    group = parser.getgroup('pytest-notify[slack]')

    # Required settings
    group.addoption('--slack_hook', help='Slack webhook URL')

    # Message styling
    group.addoption('--slack_message_prefix', help='Prefix for test results')
    group.addoption('--slack_test_name', help='Test suite name')

    # Behavior settings
    group.addoption('--slack_timeout', type=int, default=10, help='Request timeout')

def format_message(test_result, config: SlackConfig, exitstatus: int) -> dict:
    """Format the Slack message with all styling"""
    status = "Passed" if exitstatus == 0 else "Failed"
    color = "#36a64f" if exitstatus == 0 else "#dc3545"

    sections = []

    # Add test name if provided
    if config.test_name:
        sections.append(f"*Test Suite: {config.test_name}*")

    # Test results summary
    results = [
        f"Status={status}",
        f"Passed={test_result.passed}",
        f"Failed={test_result.failed}",
        f"Skipped={test_result.skipped}",
        f"Error={test_result.error}",
        f"XFailed={test_result.xfailed}",
        f"XPassed={test_result.xpassed}"
    ]
    sections.append(" ".join(results))

    # Failed tests details only if show_details is enabled
    if test_result.failed > 0 and config.config.option.show_details:
        failed = ["*Failed Tests:*"]
        for test in test_result.failed_tests:
            if not config.config.option.hide_errors and test in test_result.failed_details:
                error = test_result.failed_details[test].split('\n')[0]
                failed.append(f"• `{test}`\n  ↳ _{error}_")
            else:
                failed.append(f"• `{test}`")
        sections.append("\n".join(failed))

    text = "\n\n".join(sections)
    if config.message_prefix:
        text = f"{config.message_prefix}\n\n{text}"

    return {
        "attachments": [{
            "color": color,
            "text": text,
            "mrkdwn_in": ["text", "pretext", "fields"]
        }]
    }

def slack_send_message(test_result, config: SlackConfig, exitstatus: int):
    """Send test results to Slack."""
    # Skip if no hook
    if not config.hook:
        return False

    try:
        message = format_message(test_result, config, exitstatus)
        
        response = requests.post(
            config.hook,
            json=message,
            timeout=config.timeout
        )
        response.raise_for_status()
        return True
    except Exception:
        return False
