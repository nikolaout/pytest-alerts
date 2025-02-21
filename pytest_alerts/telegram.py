from dataclasses import dataclass
import requests
from datetime import datetime

@dataclass
class TelegramConfig:
    """Configuration for Telegram notifications."""
    bot_token: str = None
    chat_id: str = None
    message_prefix: str = None
    test_name: str = None
    timeout: int = 10
    config: object = None

    @classmethod
    def from_pytest_config(cls, config):
        """Create TelegramConfig from pytest config."""
        return cls(
            bot_token=config.option.telegram_bot_token,
            chat_id=config.option.telegram_chat_id,
            message_prefix=config.option.telegram_message_prefix,
            test_name=config.option.telegram_test_name,
            timeout=config.option.telegram_timeout,
            config=config
        )

def add_telegram_options(parser):
    group = parser.getgroup('pytest-alerts-telegram')

    # Required settings
    group.addoption('--alerts-telegram-bot-token', help='Telegram bot token', dest='telegram_bot_token')
    group.addoption('--alerts-telegram-chat-id', help='Telegram chat ID', dest='telegram_chat_id')

    # Message styling
    group.addoption('--alerts-telegram-message-prefix', help='Prefix for test results', dest='telegram_message_prefix')
    group.addoption('--alerts-telegram-test-name', help='Test suite name', dest='telegram_test_name')

    # Behavior settings
    group.addoption('--alerts-telegram-timeout', type=int, default=10, help='Request timeout', dest='telegram_timeout')

def format_message(test_result, config: TelegramConfig, exitstatus: int) -> str:
    """Format the test results message for Telegram."""
    message_parts = []
    
    # Header with test name and prefix
    header_parts = []
    if config.message_prefix:
        header_parts.append(f"📢 <b>{config.message_prefix}</b>")
    if config.test_name:
        header_parts.append(f"🔖 <b>Test Suite:</b> <i>{config.test_name}</i>")
    if header_parts:
        message_parts.append("\n".join(header_parts))
        message_parts.append("━━━━━━━━━━━━━━━━━━━━")

    # Calculate total and percentages
    total = test_result.failed + test_result.passed + test_result.skipped + test_result.error
    if total > 0:
        pass_pct = (test_result.passed / total) * 100
        fail_pct = (test_result.failed / total) * 100
        skip_pct = (test_result.skipped / total) * 100
        error_pct = (test_result.error / total) * 100
    else:
        pass_pct = fail_pct = skip_pct = error_pct = 0

    # Status with big emoji
    status_emoji = "✅" if exitstatus == 0 else "❌"
    status_text = "PASSED" if exitstatus == 0 else "FAILED"
    
    # Modern summary with blocks and bars
    summary = [
        f"{status_emoji} <b>Status: {status_text}</b>",
        "",
        "📊 <b>Test Results Overview</b>",
        f"Total Tests: {total}",
        "",
        # Pass/Fail Block
        "┌──────────────────────┐",
        f"│ ✅ PASSED: {str(test_result.passed).rjust(3)} │ {str(round(pass_pct, 1)).rjust(5)}% │",
        f"│ {'█' * int(pass_pct/5)}{'░' * (20-int(pass_pct/5))} │",
        "├──────────────────────┤",
        f"│ ❌ FAILED: {str(test_result.failed).rjust(3)} │ {str(round(fail_pct, 1)).rjust(5)}% │",
        f"│ {'█' * int(fail_pct/5)}{'░' * (20-int(fail_pct/5))} │",
        "├──────────────────────┤",
        f"│ ⏭️ SKIPPED: {str(test_result.skipped).rjust(2)} │ {str(round(skip_pct, 1)).rjust(5)}% │",
        f"│ {'█' * int(skip_pct/5)}{'░' * (20-int(skip_pct/5))} │",
        "├──────────────────────┤",
        f"│ ⚠️ ERRORS: {str(test_result.error).rjust(3)} │ {str(round(error_pct, 1)).rjust(5)}% │",
        f"│ {'█' * int(error_pct/5)}{'░' * (20-int(error_pct/5))} │",
        "└──────────────────────┘",
        "",
        "<b>Additional Info:</b>",
        f"🔄 XFailed: {test_result.xfailed}",
        f"⚡ XPassed: {test_result.xpassed}"
    ]
    message_parts.append("\n".join(summary))

    # Add failed tests details only if show_details is enabled
    if test_result.failed and test_result.failed_tests and config.config.option.show_details:
        message_parts.append("\n━━━━━━━━━━━━━━━━━━━━")
        message_parts.append("❌ <b>Failed Tests Details</b>")
        
        for i, test in enumerate(test_result.failed_tests, 1):
            # Add test name with number
            message_parts.append(f"\n{i}. <code>{test}</code>")
            
            # Add error details if not hidden
            if not config.config.option.hide_errors and test in test_result.failed_details:
                error = test_result.failed_details[test].strip()
                error_lines = error.split('\n')
                
                if error_lines:
                    # Format error message more concisely
                    main_error = error_lines[0].strip()
                    message_parts.append(f"   ↳ <i>{main_error}</i>")
                    
                    # If there are additional details, add them in a cleaner format
                    if len(error_lines) > 1:
                        additional_details = []
                        for line in error_lines[1:]:
                            if line.strip():  # Skip empty lines
                                additional_details.append(line.strip())
                        if additional_details:
                            details_text = "\n      ".join(additional_details)
                            message_parts.append(f"   ⮡ <code>{details_text}</code>")

    # Footer with timestamp
    message_parts.append("\n━━━━━━━━━━━━━━━━━━━━")
    timestamp = datetime.now().strftime("%H:%M:%S")
    message_parts.append(f"⏰ Report generated at <b>{timestamp}</b>")

    return "\n".join(message_parts)

def telegram_send_message(test_result, config: TelegramConfig, exitstatus: int):
    """
    Send test results to Telegram.

    Args:
        test_result: Test execution results
        config: Telegram configuration
        exitstatus: Exit status of the test run
    """
    # Skip if no token or chat id
    if not config.bot_token or not config.chat_id:
        return False

    try:
        message = format_message(test_result, config, exitstatus)
        
        # Send message to Telegram
        url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": config.chat_id,
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=config.timeout
        )
        response.raise_for_status()
        return True
    except Exception:
        return False
