"""Shared data structures used across the SPI and I2C interfaces.

These types are protocol-agnostic and intentionally kept in one place so the
per-protocol modules (``spi.py``, ``i2c.py``) can reuse them without duplicating
data-structure definitions.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FTHandle:
    """Opaque FTDI device handle returned by ``*_OpenChannel``."""
    value: int


@dataclass(frozen=True)
class ChannelInfo:
    """Decoded ``FT_DEVICE_LIST_INFO_NODE`` describing an MPSSE channel.

    Shared by SPI and I2C since the native device-list node is the same for both.
    """
    flags: int
    type: int
    id: int
    loc_id: int
    serial_number: str
    description: str
    ft_handle: Optional[FTHandle]
