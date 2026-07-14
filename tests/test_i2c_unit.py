"""Hardware-free unit tests for the I2CInterface marshalling logic.

Like ``test_spi_unit.py``, these replace ``libmpsse_dll`` with an in-memory fake
so the pointer / buffer / address handling in the Pythonic helpers can be
verified without any FTDI hardware or the real DLL. They run by default.
"""

import ctypes

import pytest

from pyLibmpsse.consts import FT_STATUS, I2C_TRANSFER_OPTIONS
from pyLibmpsse.common import FTHandle
from pyLibmpsse.i2c import I2CChannelConfig, I2CInterface

OK = FT_STATUS.FT_OK.value
START = I2C_TRANSFER_OPTIONS.I2C_TRANSFER_OPTIONS_START_BIT
STOP = I2C_TRANSFER_OPTIONS.I2C_TRANSFER_OPTIONS_STOP_BIT


def _deref(byref_arg):
    """Return the ctypes object underlying a ``ctypes.byref()`` argument."""
    return byref_arg._obj


class FakeDll:
    """Minimal stand-in for ``libmpsse_dll`` covering the I2C functions."""

    def __init__(self, status=OK):
        self.status = status
        self.calls = []
        self.num_channels = 0
        self.read_payload = b""
        self.device_id = b"\x00\x00\x00"
        self.gpio_value = 0
        self.version = (0, 0)

    def _record(self, name, args):
        self.calls.append((name, args))

    def I2C_GetNumChannels(self, num_channels):
        self._record("I2C_GetNumChannels", ())
        _deref(num_channels).value = self.num_channels
        return self.status

    def I2C_OpenChannel(self, index, handle):
        self._record("I2C_OpenChannel", (index,))
        _deref(handle).value = 0xABCD
        return self.status

    def I2C_InitChannel(self, handle, config):
        self._record("I2C_InitChannel", ())
        return self.status

    def I2C_CloseChannel(self, handle):
        self._record("I2C_CloseChannel", ())
        return self.status

    def I2C_DeviceRead(self, handle, address, size, buffer, transferred, options):
        self._record("I2C_DeviceRead", (address.value, size.value, options.value))
        n = min(len(self.read_payload), size.value)
        for i in range(n):
            buffer[i] = self.read_payload[i]
        _deref(transferred).value = n
        return self.status

    def I2C_DeviceWrite(self, handle, address, size, buffer, transferred, options):
        self._record("I2C_DeviceWrite", (address.value, size.value, options.value))
        _deref(transferred).value = size.value
        return self.status

    def I2C_GetDeviceID(self, handle, address, device_id):
        self._record("I2C_GetDeviceID", (address.value,))
        for i in range(3):
            device_id[i] = self.device_id[i]
        return self.status

    def FT_WriteGPIO(self, handle, direction, value):
        self._record("FT_WriteGPIO", (direction.value, value.value))
        return self.status

    def FT_ReadGPIO(self, handle, value):
        self._record("FT_ReadGPIO", ())
        _deref(value).value = self.gpio_value
        return self.status

    def Ver_libMPSSE(self, libmpsse, libftd2xx):
        self._record("Ver_libMPSSE", ())
        _deref(libmpsse).value = self.version[0]
        _deref(libftd2xx).value = self.version[1]
        return self.status


class FakeBindings:
    def __init__(self, dll):
        self.libmpsse_dll = dll


@pytest.fixture
def dll():
    return FakeDll()


@pytest.fixture
def i2c(dll):
    return I2CInterface(FakeBindings(dll))


@pytest.fixture
def handle():
    return FTHandle(0xABCD)


def test_get_num_channels(i2c, dll):
    dll.num_channels = 2
    assert i2c.get_num_channels() == 2


def test_get_num_channels_error_raises(i2c, dll):
    dll.status = FT_STATUS.FT_DEVICE_NOT_FOUND.value
    with pytest.raises(RuntimeError):
        i2c.get_num_channels()


def test_open_channel_returns_handle(i2c):
    h = i2c.open_channel(1)
    assert isinstance(h, FTHandle)
    assert h.value == 0xABCD


def test_init_and_close_channel_return_none(i2c, handle):
    cfg = I2CChannelConfig(clock_rate=400000, latency_timer=2, options=0, pin=0)
    assert i2c.init_channel(handle, cfg) is None
    assert i2c.close_channel(handle) is None


def test_read_returns_payload(i2c, dll, handle):
    dll.read_payload = bytes([0xDE, 0xAD])
    assert i2c.read(handle, 0x50, 2, options=START | STOP) == bytes([0xDE, 0xAD])


def test_read_masks_address_to_7_bits(i2c, dll, handle):
    # 0xA5 (8-bit) must be reduced to its low 7 bits, 0x25, before hitting the DLL.
    i2c.read(handle, 0xA5, 1, options=START | STOP)
    name, args = dll.calls[-1]
    assert name == "I2C_DeviceRead"
    assert args[0] == 0x25          # masked address
    assert args[2] == (START | STOP)  # options passed through unchanged


def test_write_returns_count_and_masks_address(i2c, dll, handle):
    n = i2c.write(handle, 0xC4, bytes([1, 2, 3]), options=START | STOP)
    assert n == 3
    name, args = dll.calls[-1]
    assert name == "I2C_DeviceWrite"
    assert args[0] == 0x44          # 0xC4 & 0x7F


def test_get_device_id_returns_three_bytes(i2c, dll, handle):
    dll.device_id = bytes([0x11, 0x22, 0x33])
    assert i2c.get_device_id(handle, 0x50) == bytes([0x11, 0x22, 0x33])


def test_write_gpio_masks_to_8_bits(i2c, dll, handle):
    i2c.write_gpio(handle, direction=0x1FF, value=0x2AB)
    assert dll.calls[-1] == ("FT_WriteGPIO", (0xFF, 0xAB))


def test_read_gpio_returns_value(i2c, dll, handle):
    dll.gpio_value = 0x5A
    assert i2c.read_gpio(handle) == 0x5A


def test_get_version_returns_tuple(i2c, dll):
    dll.version = (0x030109, 0x030228)
    assert i2c.get_version() == (0x030109, 0x030228)


def test_error_status_raises_runtimeerror(i2c, dll, handle):
    dll.status = FT_STATUS.FT_IO_ERROR.value
    with pytest.raises(RuntimeError):
        i2c.write(handle, 0x50, b"\x01", options=START | STOP)


def test_open_initialized_opens_inits_and_closes(i2c, dll):
    cfg = I2CChannelConfig(clock_rate=400000, latency_timer=2, options=0, pin=0)
    with i2c.open_initialized(1, cfg) as h:
        assert isinstance(h, FTHandle)
        assert h.value == 0xABCD
    names = [name for name, _ in dll.calls]
    assert names == ["I2C_OpenChannel", "I2C_InitChannel", "I2C_CloseChannel"]


def test_open_initialized_closes_on_exception(i2c, dll):
    cfg = I2CChannelConfig(clock_rate=400000, latency_timer=2, options=0, pin=0)
    with pytest.raises(ValueError):
        with i2c.open_initialized(1, cfg):
            raise ValueError("boom")
    # The channel must still be released even though the body raised.
    assert [name for name, _ in dll.calls][-1] == "I2C_CloseChannel"
