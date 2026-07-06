"""
Constants and enumerations for the libMPSSE library.

All values are derived from the official FTDI documentation:
  - D2XX Programmer's Guide (FT_000071)
  - AN_177 User Guide For LibMPSSE-I2C (FT_000466)
  - AN_178 User Guide For LibMPSSE-SPI (FT_000492)

These constants mirror those defined in the C headers ``ftd2xx.h``,
``libMPSSE_i2c.h``, and ``libMPSSE_spi.h``.
"""

from enum import IntEnum


# ──────────────────────────────────────────────────────────────────────
#  FT_STATUS  –  return codes shared by D2XX and libMPSSE APIs
# ──────────────────────────────────────────────────────────────────────

class FT_STATUS(IntEnum):
    """D2XX / libMPSSE status codes returned by most API functions."""
    FT_OK                          = 0
    FT_INVALID_HANDLE              = 1
    FT_DEVICE_NOT_FOUND            = 2
    FT_DEVICE_NOT_OPENED           = 3
    FT_IO_ERROR                    = 4
    FT_INSUFFICIENT_RESOURCES      = 5
    FT_INVALID_PARAMETER           = 6
    FT_INVALID_BAUD_RATE           = 7
    FT_DEVICE_NOT_OPENED_FOR_ERASE = 8
    FT_DEVICE_NOT_OPENED_FOR_WRITE = 9
    FT_FAILED_TO_WRITE_DEVICE      = 10
    FT_EEPROM_READ_FAILED          = 11
    FT_EEPROM_WRITE_FAILED         = 12
    FT_EEPROM_ERASE_FAILED         = 13
    FT_EEPROM_NOT_PRESENT          = 14
    FT_EEPROM_NOT_PROGRAMMED       = 15
    FT_INVALID_ARGS                = 16
    FT_NOT_SUPPORTED               = 17
    FT_OTHER_ERROR                 = 18


# ──────────────────────────────────────────────────────────────────────
#  FT_DEVICE  –  device type identifiers
# ──────────────────────────────────────────────────────────────────────

class FT_DEVICE(IntEnum):
    """FTDI chip type identifiers (see ``FT_GetDeviceInfoDetail``)."""
    FT_DEVICE_232BM   = 0
    FT_DEVICE_232AM   = 1
    FT_DEVICE_100AX   = 2
    FT_DEVICE_UNKNOWN = 3
    FT_DEVICE_2232C   = 4
    FT_DEVICE_232R    = 5
    FT_DEVICE_2232H   = 6
    FT_DEVICE_4232H   = 7
    FT_DEVICE_232H    = 8
    FT_DEVICE_X_SERIES = 9


# ──────────────────────────────────────────────────────────────────────
#  Flags for FT_ListDevices
# ──────────────────────────────────────────────────────────────────────

class FT_LIST_FLAGS(IntEnum):
    """Flags passed to ``FT_ListDevices``."""
    FT_LIST_NUMBER_ONLY = 0x80000000
    FT_LIST_BY_INDEX    = 0x40000000
    FT_LIST_ALL         = 0x20000000


# ──────────────────────────────────────────────────────────────────────
#  Flags for FT_OpenEx
# ──────────────────────────────────────────────────────────────────────

class FT_OPEN_TYPE(IntEnum):
    """Flags passed to ``FT_OpenEx``."""
    FT_OPEN_BY_SERIAL_NUMBER = 1
    FT_OPEN_BY_DESCRIPTION   = 2
    FT_OPEN_BY_LOCATION      = 4


# ──────────────────────────────────────────────────────────────────────
#  FT_DRIVER_TYPE
# ──────────────────────────────────────────────────────────────────────

class FT_DRIVER_TYPE(IntEnum):
    """Driver type returned by ``FT_GetDriverType``."""
    FT_DRIVER_TYPE_D2XX = 0
    FT_DRIVER_TYPE_VCP  = 1


# ──────────────────────────────────────────────────────────────────────
#  Data characteristics  (see FT_SetDataCharacteristics)
# ──────────────────────────────────────────────────────────────────────

class FT_DATA_BITS(IntEnum):
    """Word length for UART mode."""
    FT_BITS_8 = 8
    FT_BITS_7 = 7


class FT_STOP_BITS(IntEnum):
    """Stop-bit count for UART mode."""
    FT_STOP_BITS_1 = 0
    FT_STOP_BITS_2 = 2


class FT_PARITY(IntEnum):
    """Parity setting for UART mode."""
    FT_PARITY_NONE  = 0
    FT_PARITY_ODD   = 1
    FT_PARITY_EVEN  = 2
    FT_PARITY_MARK  = 3
    FT_PARITY_SPACE = 4


# ──────────────────────────────────────────────────────────────────────
#  Flow control  (see FT_SetFlowControl)
# ──────────────────────────────────────────────────────────────────────

class FT_FLOW_CONTROL(IntEnum):
    """Flow-control options for UART mode."""
    FT_FLOW_NONE     = 0x0000
    FT_FLOW_RTS_CTS  = 0x0100
    FT_FLOW_DTR_DSR  = 0x0200
    FT_FLOW_XON_XOFF = 0x0400


# ──────────────────────────────────────────────────────────────────────
#  Buffer purge  (see FT_Purge)
# ──────────────────────────────────────────────────────────────────────

class FT_PURGE(IntEnum):
    """Flags for ``FT_Purge``."""
    FT_PURGE_RX = 1
    FT_PURGE_TX = 2


# ──────────────────────────────────────────────────────────────────────
#  Event notifications  (see FT_SetEventNotification)
# ──────────────────────────────────────────────────────────────────────

class FT_EVENT(IntEnum):
    """Event types for ``FT_SetEventNotification``."""
    FT_EVENT_RXCHAR       = 1
    FT_EVENT_MODEM_STATUS = 2
    FT_EVENT_LINE_STATUS  = 4


# ──────────────────────────────────────────────────────────────────────
#  Bit modes  (see FT_SetBitMode)
# ──────────────────────────────────────────────────────────────────────

class FT_BIT_MODE(IntEnum):
    """Operating modes passed to ``FT_SetBitMode``.

    ``FT_BITMODE_MPSSE`` is **required** to enable the MPSSE engine
    before calling any I²C / SPI / JTAG function.
    """
    FT_BITMODE_RESET         = 0x00
    FT_BITMODE_ASYNC_BITBANG = 0x01
    FT_BITMODE_MPSSE         = 0x02
    FT_BITMODE_SYNC_BITBANG  = 0x04
    FT_BITMODE_MCU_HOST      = 0x08
    FT_BITMODE_FAST_SERIAL   = 0x10
    FT_BITMODE_CBUS_BITBANG  = 0x20
    FT_BITMODE_SYNC_FIFO     = 0x40


# ══════════════════════════════════════════════════════════════════════
#  I²C  constants  (AN_177,  libMPSSE_i2c.h)
# ══════════════════════════════════════════════════════════════════════

# ──  I²C Clock Rate  ─────────────────────────────────────────────────

class I2C_CLOCK_RATE(IntEnum):
    """Standard I²C bus clock rates (Hz).

    A custom integer value in the range 0 – 3 400 000 may also be used.
    """
    I2C_CLOCK_STANDARD_MODE   = 100000   # 100 kHz
    I2C_CLOCK_FAST_MODE       = 400000   # 400 kHz
    I2C_CLOCK_FAST_MODE_PLUS  = 1000000  # 1 MHz
    I2C_CLOCK_HIGH_SPEED_MODE = 3400000  # 3.4 MHz


# ──  I²C Channel Configuration Options  ───────────────────────────────
#     (ChannelConfig.Options field)

class I2C_CONFIG_OPTIONS(IntEnum):
    """Bit masks for the ``Options`` field of the I²C ``ChannelConfig``.

    Notes
    -----
    * 3-phase-clocking is available only on Hi-Speed devices
      (FT232H, FT2232H, FT4232H), not on FT2232D.
    * Drive-Only-Zero is available only on the FT232H.
    """
    I2C_DISABLE_3PHASE_CLOCKING  = 0x00000001  # BIT0
    I2C_ENABLE_DRIVE_ONLY_ZERO   = 0x00000002  # BIT1


# ──  I²C Transfer Options  ───────────────────────────────────────────

class I2C_TRANSFER_OPTIONS(IntEnum):
    """Bit masks for the *options* parameter of
    ``I2C_DeviceRead`` / ``I2C_DeviceWrite``.

    These flags can be combined with bitwise-OR.
    """
    I2C_TRANSFER_OPTIONS_START_BIT         = 0x00000001  # BIT0
    I2C_TRANSFER_OPTIONS_STOP_BIT          = 0x00000002  # BIT1
    I2C_TRANSFER_OPTIONS_BREAK_ON_NACK     = 0x00000004  # BIT2  (Write only)
    I2C_TRANSFER_OPTIONS_NACK_LAST_BYTE    = 0x00000008  # BIT3  (Read only)
    I2C_TRANSFER_OPTIONS_FAST_TRANSFER_BYTES = 0x00000010  # BIT4
    I2C_TRANSFER_OPTIONS_FAST_TRANSFER_BITS  = 0x00000020  # BIT5
    I2C_TRANSFER_OPTIONS_NO_ADDRESS        = 0x00000040  # BIT6


# ══════════════════════════════════════════════════════════════════════
#  SPI  constants  (AN_178,  libMPSSE_spi.h)
# ══════════════════════════════════════════════════════════════════════

# ──  SPI Mode  (configOptions BIT1 – BIT0)  ──────────────────────────

class SPI_CONFIG_MODE(IntEnum):
    """SPI mode selection (``configOptions`` BIT1–BIT0).

    ======  ============  ============================================
    Mode    CPOL / CPHA   Description
    ======  ============  ============================================
    MODE0   CPOL=0 CPHA=0 Data captured on rising  edge, propagated on falling edge
    MODE1   CPOL=0 CPHA=1 Data captured on falling edge, propagated on rising  edge
    MODE2   CPOL=1 CPHA=0 Data captured on falling edge, propagated on rising  edge
    MODE3   CPOL=1 CPHA=1 Data captured on rising  edge, propagated on falling edge
    ======  ============  ============================================
    """
    SPI_CONFIG_OPTION_MODE0 = 0x00000000
    SPI_CONFIG_OPTION_MODE1 = 0x00000001
    SPI_CONFIG_OPTION_MODE2 = 0x00000002
    SPI_CONFIG_OPTION_MODE3 = 0x00000003


# ──  SPI Chip‑Select line  (configOptions BIT4 – BIT2)  ──────────────

class SPI_CONFIG_CS(IntEnum):
    """Chip-select line selection (``configOptions`` BIT4–BIT2).

    DBUS3 through DBUS7 map to ADBUS[3…7] on the first MPSSE channel
    or BDBUS[3…7] on the second (when available).
    """
    SPI_CONFIG_OPTION_CS_DBUS3 = 0x00000000  # 000 << 2
    SPI_CONFIG_OPTION_CS_DBUS4 = 0x00000004  # 001 << 2
    SPI_CONFIG_OPTION_CS_DBUS5 = 0x00000008  # 010 << 2
    SPI_CONFIG_OPTION_CS_DBUS6 = 0x0000000C  # 011 << 2
    SPI_CONFIG_OPTION_CS_DBUS7 = 0x00000010  # 100 << 2


# ──  SPI CS active-low flag  (configOptions BIT5)  ───────────────────

class SPI_CONFIG_CS_POLARITY(IntEnum):
    """Chip-select polarity (``configOptions`` BIT5).

    When OR'd into ``configOptions`` the selected CS line is active **low**;
    otherwise it is active high.
    """
    SPI_CONFIG_OPTION_CS_ACTIVELOW = 0x00000020


# ──  SPI Transfer Options  ───────────────────────────────────────────

class SPI_TRANSFER_OPTIONS(IntEnum):
    """Bit masks for the *transferOptions* parameter of
    ``SPI_Read`` / ``SPI_Write`` / ``SPI_ReadWrite``.

    These flags can be combined with bitwise-OR.
    """
    SPI_TRANSFER_OPTIONS_SIZE_IN_BYTES     = 0x00000000  # BIT0 = 0
    SPI_TRANSFER_OPTIONS_SIZE_IN_BITS      = 0x00000001  # BIT0 = 1
    SPI_TRANSFER_OPTIONS_CHIPSELECT_ENABLE  = 0x00000002  # BIT1
    SPI_TRANSFER_OPTIONS_CHIPSELECT_DISABLE = 0x00000004  # BIT2


# ══════════════════════════════════════════════════════════════════════
#  GPIO constants
# ══════════════════════════════════════════════════════════════════════

class GPIO_DIRECTION(IntEnum):
    """Direction for a single GPIO line.

    Used when composing the *dir* byte for ``FT_WriteGPIO``.
    """
    GPIO_DIR_INPUT  = 0
    GPIO_DIR_OUTPUT = 1


class GPIO_VALUE(IntEnum):
    """Logic level for a single GPIO line."""
    GPIO_LOW  = 0
    GPIO_HIGH = 1


# ──────────────────────────────────────────────────────────────────────
#  Convenience aliases  (flat, module-level names)
# ──────────────────────────────────────────────────────────────────────

# FT_STATUS shortcuts
FT_OK                           = FT_STATUS.FT_OK
FT_INVALID_HANDLE               = FT_STATUS.FT_INVALID_HANDLE
FT_DEVICE_NOT_FOUND             = FT_STATUS.FT_DEVICE_NOT_FOUND
FT_DEVICE_NOT_OPENED            = FT_STATUS.FT_DEVICE_NOT_OPENED
FT_IO_ERROR                     = FT_STATUS.FT_IO_ERROR
FT_INSUFFICIENT_RESOURCES       = FT_STATUS.FT_INSUFFICIENT_RESOURCES
FT_INVALID_PARAMETER            = FT_STATUS.FT_INVALID_PARAMETER
FT_OTHER_ERROR                  = FT_STATUS.FT_OTHER_ERROR

# FT_BIT_MODE shortcuts
FT_BITMODE_RESET         = FT_BIT_MODE.FT_BITMODE_RESET
FT_BITMODE_MPSSE         = FT_BIT_MODE.FT_BITMODE_MPSSE
FT_BITMODE_ASYNC_BITBANG = FT_BIT_MODE.FT_BITMODE_ASYNC_BITBANG
FT_BITMODE_SYNC_BITBANG  = FT_BIT_MODE.FT_BITMODE_SYNC_BITBANG
FT_BITMODE_MCU_HOST      = FT_BIT_MODE.FT_BITMODE_MCU_HOST
FT_BITMODE_FAST_SERIAL   = FT_BIT_MODE.FT_BITMODE_FAST_SERIAL
FT_BITMODE_CBUS_BITBANG  = FT_BIT_MODE.FT_BITMODE_CBUS_BITBANG
FT_BITMODE_SYNC_FIFO     = FT_BIT_MODE.FT_BITMODE_SYNC_FIFO
