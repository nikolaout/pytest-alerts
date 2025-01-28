# pytest-alerts

A pytest plugin that sends test results to Slack and Telegram with beautiful, customizable formatting.

[![PyPI version](https://badge.fury.io/py/pytest-alerts.svg)](https://badge.fury.io/py/pytest-alerts)
[![Python Versions](https://img.shields.io/pypi/pyversions/pytest-alerts.svg)](https://pypi.org/project/pytest-alerts/)

## Overview

pytest-alerts is a powerful pytest plugin that automatically sends your test results to Slack and Telegram. It provides:

- 📲 Real-time test notifications to Slack and Telegram
- 🎨 Modern, visually appealing message formatting
- 📊 Comprehensive test statistics with progress bars
- 🔍 Configurable error reporting and details
- ⚙️ Extensive customization options
- 🔄 Full compatibility with pytest-xdist

## Quick Start

### Installation

```bash
pip install pytest-alerts
```

### Basic Usage

1. Configure your messaging platform:

   **For Slack:**
   ```bash
   pytest --slack_webhook=YOUR_WEBHOOK_URL
   ```

   **For Telegram:**
   ```bash
   pytest --telegram_bot_token=BOT_TOKEN --telegram_chat_id=CHAT_ID
   ```

2. Run with both platforms:
   ```bash
   pytest --slack_webhook=URL --telegram_bot_token=TOKEN --telegram_chat_id=ID
   ```

## Configuration Options

### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--show_details` | Include error details in notifications | False |
| `--hide_errors` | Hide error messages from notifications | False |

### Slack-specific Options

| Option | Description | Required |
|--------|-------------|----------|
| `--slack_webhook` | Slack webhook URL | Yes |
| `--slack_icon` | Bot icon emoji | No |

### Telegram-specific Options

| Option | Description | Required |
|--------|-------------|----------|
| `--telegram_bot_token` | Bot API token | Yes |
| `--telegram_chat_id` | Target chat ID | Yes |

## Message Formatting

### Default Format
Messages include:
- Test run summary (passed/failed/skipped)
- Progress bars for visual representation
- Duration of test run
- Error details (if enabled)
- Project/branch information (if available)

### Customization
- Use `--show_details` for full error traces
- Use `--hide_errors` to omit error messages
- Platform-specific formatting options available

## Advanced Usage

### CI/CD Integration
Example GitHub Actions workflow:
```yaml
steps:
  - uses: actions/checkout@v2
  - name: Run tests with notifications
    run: |
      pip install pytest-alerts
      pytest --slack_webhook=${{ secrets.SLACK_WEBHOOK }} --telegram_bot_token=${{ secrets.TELEGRAM_BOT_TOKEN }} --telegram_chat_id=${{ secrets.TELEGRAM_CHAT_ID }}
```

## Limitations

- Maximum message size varies by platform
- Rate limits apply (platform-specific)
- Some formatting options are platform-dependent

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/nikolaout/pytest-alerts)
- 🐛 [Issue Tracker](https://github.com/nikolaout/pytest-alerts/issues)
- 💬 [Discussions](https://github.com/nikolaout/pytest-alerts/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
