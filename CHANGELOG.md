# Changelog

All notable changes to pytest-alerts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.4.0] - 2025-01-28

### Added
- Added support for Python 3.8 through 3.11
- Added `typing_extensions` dependency for Python versions < 3.10

### Fixed
- Fixed TypeAlias import compatibility across Python versions
- Updated dependencies to ensure compatibility across all supported Python versions

## [1.2.0] - 2025-01-28

### Changed
- Removed `--slack_channel` option as it's now configured via webhook URL
- Simplified Slack configuration by removing redundant options
- Updated documentation for clearer setup instructions

### Fixed
- Fixed Slack webhook integration to use webhook-configured channels
- Improved error handling for Slack notifications

## [1.1.0] - 2025-01-28

### Added
- Support for Telegram thread_id
- Improved error handling for API rate limits
- Enhanced progress bar visualization

### Changed
- Updated minimum pytest requirement to 6.0.0
- Improved message formatting for better readability
- Enhanced error details formatting

### Fixed
- Issue with xdist worker coordination
- Message truncation in Slack for long error messages

## [1.0.0] - Initial Release

### Added
- Initial release with core functionality
- Slack integration with webhook support
- Telegram integration with bot API
- Customizable message formatting
- Support for pytest-xdist
- Environment variable configuration
- Comprehensive error handling
