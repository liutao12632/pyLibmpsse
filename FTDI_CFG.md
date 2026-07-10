# FTDI Config Summary (from mpsse_tst.FTDImpsse.cs)

This document summarizes the effective FTDI I2C/SPI configuration extracted from:

- D:\Code\Repo\CCID\mpsse_tst.FTDImpsse.cs

## 1. I2C Channel Init

In `InitI2c(uint ch, uint baud)`:

- `ClockRate = baud`
- `LatencyTimer = 1`
- `Options = 3`

Notes:

- `Options = 3` equals `1 + 2`:
  - `I2C_TRANSFER_OPTIONS_START_BIT = 1`
  - `I2C_TRANSFER_OPTIONS_BREAK_ON_NACK = 2`

## 2. SPI Channel Init

In `InitSpi(uint ch, uint baud)`:

- `ClockRate = baud`
- `LatencyTimer = 1`
- `configOptions = 0`
- `Pin = (dir | (dir << 8) | (dir << 16) | (dir << 24))`

Static defaults in the same file:

- `dir = 139` (`0x8B`)
- `gpo = 128` (`0x80`)

Therefore initial SPI pin config resolves to:

- `Pin = 0x8B8B8B8B` (decimal `2341178251`)

## 3. Transfer Options Used at Runtime

### 3.1 I2C transfer option

Common I2C read/write path uses:

- `TRANSFER_OPTION_I2C = 19`

`19` equals:

- `1` (`START_BIT`)
- `2` (`BREAK_ON_NACK`)
- `16` (`FAST_TRANSFER_BYTES`)

Not included:

- `STOP_BIT = 4`

### 3.2 SPI transfer option

Common SPI read/write paths use:

- `TRANSFER_OPTION_SPI = 0`

Most `SPI_Write`, `SPI_Read`, and `SPI_ReadWrite` calls pass `options = 0`.

## 4. CS Handling Behavior

- `_pass_through_spi = true` by default.
- With this default, wrapper-level `setCS()/clrCS()` is usually skipped.
- Some code paths still manually bracket a transaction with:
  - `SPI_ToggleCS(..., false)`
  - transfer
  - `SPI_ToggleCS(..., true)`

## 5. Suggested Mapping to pyLibmpsse

Recommended values to replicate this tool's behavior:

- I2C init:
  - `clock_rate = baud`
  - `latency_timer = 1`
  - `options = 3`

- SPI init:
  - `clock_rate = baud`
  - `latency_timer = 1`
  - `config_options = 0`
  - `pin = 0x8B8B8B8B`

- Runtime transfer options:
  - I2C: `19`
  - SPI: `0`

## 6. Caveat

This summary is based on decompiled code. If behavior differs on hardware, trust observed bus-level traces (logic analyzer) as final authority.
