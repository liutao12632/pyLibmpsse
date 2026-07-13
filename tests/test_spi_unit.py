"""Hardware-free unit tests for the SPIInterface marshalling logic.

These tests replace ``libmpsse_dll`` with an in-memory fake, so the pointer /
buffer handling in the Pythonic helpers can be verified without any FTDI
hardware or the real DLL. They run by default (no ``integration`` marker).
"""

import ctypes

import pytest

from pyLibmpsse.consts import FT_STATUS, SPI_TRANSFER_OPTIONS
from pyLibmpsse.spi import FTHandle, SPIChannelConfig, SPIInterface

OK = FT_STATUS.FT_OK.value
BITS = SPI_TRANSFER_OPTIONS.SPI_TRANSFER_OPTIONS_SIZE_IN_BITS


def _deref(byref_arg):
    """Return the ctypes object underlying a ``ctypes.byref()`` argument."""
    return byref_arg._obj


class FakeDll:
    """Minimal stand-in for ``libmpsse_dll``.

    Every bound function returns ``self.status`` and fills its out-parameters
    from the configured attributes, recording each call for assertions.
    """

    def __init__(self, status=OK):
        self.status = status
        self.calls = []
        self.num_channels = 0
        self.read_payload = b""
        self.gpio_value = 0
        self.miso_state = 0
        self.version = (0, 0)

    def _record(self, name, args):
        self.calls.append((name, args))

    def SPI_GetNumChannels(self, num_channels):
        self._record("SPI_GetNumChannels", ())
        _deref(num_channels).value = self.num_channels
        return self.status

    def SPI_OpenChannel(self, index, handle):
        self._record("SPI_OpenChannel", (index,))
        _deref(handle).value = 0xABCD
        return self.status

    def SPI_InitChannel(self, handle, config):
        self._record("SPI_InitChannel", ())
        return self.status

    def SPI_CloseChannel(self, handle):
        self._record("SPI_CloseChannel", ())
        return self.status

    def SPI_Read(self, handle, buffer, size, transferred, options):
        self._record("SPI_Read", (size.value, options.value))
        n = min(len(self.read_payload), size.value)
        for i in range(n):
            buffer[i] = self.read_payload[i]
        _deref(transferred).value = n
        return self.status

    def SPI_Write(self, handle, buffer, size, transferred, options):
        self._record("SPI_Write", (size.value, options.value))
        _deref(transferred).value = size.value
        return self.status

    def SPI_ReadWrite(self, handle, in_buffer, out_buffer, size, transferred, options):
        self._record("SPI_ReadWrite", (size.value, options.value))
        n = min(len(self.read_payload), size.value)
        for i in range(n):
            in_buffer[i] = self.read_payload[i]
        _deref(transferred).value = n
        return self.status

    def SPI_IsBusy(self, handle, state):
        self._record("SPI_IsBusy", ())
        _deref(state).value = self.miso_state
        return self.status

    def SPI_ChangeCS(self, handle, options):
        self._record("SPI_ChangeCS", (options.value,))
        return self.status

    def SPI_ToggleCS(self, handle, state):
        self._record("SPI_ToggleCS", (state.value,))
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
def spi(dll):
    return SPIInterface(FakeBindings(dll))


@pytest.fixture
def handle():
    return FTHandle(0xABCD)


def test_get_num_channels(spi, dll):
    dll.num_channels = 3
    assert spi.get_num_channels() == 3


def test_get_num_channels_error_raises(spi, dll):
    dll.status = FT_STATUS.FT_INVALID_HANDLE.value
    with pytest.raises(RuntimeError):
        spi.get_num_channels()


def test_open_channel_returns_handle(spi):
    h = spi.open_channel(0)
    assert isinstance(h, FTHandle)
    assert h.value == 0xABCD


def test_init_and_close_channel_return_none(spi, handle):
    cfg = SPIChannelConfig(clock_rate=1_000_000, latency_timer=1, config_options=0, pin=0)
    assert spi.init_channel(handle, cfg) is None
    assert spi.close_channel(handle) is None


def test_read_returns_payload(spi, dll, handle):
    dll.read_payload = bytes([0x11, 0x22, 0x33])
    assert spi.read(handle, 3) == bytes([0x11, 0x22, 0x33])


def test_write_returns_count(spi, handle):
    assert spi.write(handle, bytes([1, 2, 3, 4])) == 4


def test_read_write_full_duplex(spi, dll, handle):
    dll.read_payload = bytes([0xAA, 0xBB])
    assert spi.read_write(handle, bytes([0x01, 0x02])) == bytes([0xAA, 0xBB])


@pytest.mark.parametrize("call", [
    lambda s, h: s.read(h, 4, transfer_options=BITS),
    lambda s, h: s.write(h, b"\x01", transfer_options=BITS),
    lambda s, h: s.read_write(h, b"\x01", transfer_options=BITS),
])
def test_bit_mode_is_rejected(spi, handle, call):
    with pytest.raises(ValueError):
        call(spi, handle)


def test_is_busy_reflects_miso_state(spi, dll, handle):
    dll.miso_state = 1
    assert spi.is_busy(handle) is True
    dll.miso_state = 0
    assert spi.is_busy(handle) is False


def test_toggle_cs_passes_state(spi, dll, handle):
    spi.toggle_cs(handle, True)
    assert dll.calls[-1] == ("SPI_ToggleCS", (1,))


def test_change_cs_passes_options(spi, dll, handle):
    spi.change_cs(handle, 0x20)
    assert dll.calls[-1] == ("SPI_ChangeCS", (0x20,))


def test_write_gpio_masks_to_8_bits(spi, dll, handle):
    spi.write_gpio(handle, direction=0x1FF, value=0x2AB)
    assert dll.calls[-1] == ("FT_WriteGPIO", (0xFF, 0xAB))


def test_read_gpio_returns_value(spi, dll, handle):
    dll.gpio_value = 0x5A
    assert spi.read_gpio(handle) == 0x5A


def test_get_version_returns_tuple(spi, dll):
    dll.version = (0x030109, 0x030228)
    assert spi.get_version() == (0x030109, 0x030228)


def test_error_status_raises_runtimeerror(spi, dll, handle):
    dll.status = FT_STATUS.FT_IO_ERROR.value
    with pytest.raises(RuntimeError):
        spi.write(handle, b"\x01")
