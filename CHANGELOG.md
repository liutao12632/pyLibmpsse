# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-15

First stable release. This is the first documented release and consolidates the
earlier `0.x` prototyping into a stable, Windows-only wrapper for FTDI's
LibMPSSE library.

### Added
- SPI support via `SPIInterface`: low-level 1:1 C bindings plus Pythonic helpers
  (`read`, `write`, `read_write`, `is_busy`, `change_cs`, `toggle_cs`, GPIO,
  version) and an `open_initialized` context manager.
- I2C support via `I2CInterface`: low-level 1:1 C bindings plus Pythonic helpers
  (`read`, `write`, `get_device_id`, GPIO, version) and an `open_initialized`
  context manager.
- High-byte GPIO helpers (`write_gpio` / `read_gpio`) on both interfaces.
- Protocol-agnostic shared types `FTHandle` and `ChannelInfo` in `common.py`.
- Constants for `FT_STATUS`, SPI, I2C and GPIO in `consts.py`.
- Hardware-free unit tests (in-memory fake DLL) and hardware-gated integration
  tests selected via the `integration` marker and DLL-path environment variables.
- MIT `LICENSE` file.
- `test` optional-dependency group, installable with `pip install -e .[test]`.

### Changed
- Marked the package `Development Status :: 5 - Production/Stable`.
- Rewrote the README with installation instructions and SPI/I2C quick-start
  examples, and refreshed the architecture overview.
- Unified the I2C channel-index documentation to 0-based across `open_channel`
  and `open_initialized` (the FTDI header comment's "1 to N" wording is a known
  documentation error; the library is 0-based).

### Removed
- Dropped the unimplemented JTAG claim from the package description and keywords.
- Removed `requirements.txt`; the runtime has no third-party dependencies and
  test dependencies now live in the `test` optional-dependency group.

### Fixed
- `LibMPSSELoader` now raises `PlatformError` immediately on non-Windows
  platforms instead of failing later with an obscure `ctypes` error.

[1.0.0]: https://github.com/liutao12632/pyLibmpsse/releases/tag/v1.0.0
