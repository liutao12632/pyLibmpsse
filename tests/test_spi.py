import os

from pyLibmpsse.libmpsse_bindings import LibMPSSELoader
from pyLibmpsse.spi import SPIChannelConfig, SPIInterface

import pytest

ENV_FTD2XX_DLL = "PYLIBMPSSE_FTD2XX_DLL"
ENV_LIBMPSSE_DLL = "PYLIBMPSSE_LIBMPSSE_DLL"


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(
            f"Missing required environment variable: {name}. "
            "Use scripts/run_pytest_with_dll_env.ps1 to set variables and run tests."
        )
    return value


@pytest.fixture(scope="module")
def bindings() -> LibMPSSELoader:
    ftd2xx_path = _require_env(ENV_FTD2XX_DLL)
    libmpsse_path = _require_env(ENV_LIBMPSSE_DLL)
    return LibMPSSELoader(ftd2xx_path, libmpsse_path)


@pytest.mark.integration
def test_bindings_loads_dlls(bindings: LibMPSSELoader):
    assert bindings.ftd2xx_dll is not None, "ftd2xx.dll should be loaded."
    assert bindings.libmpsse_dll is not None, "libmpsse.dll should be loaded."
    assert hasattr(bindings.libmpsse_dll, "SPI_GetNumChannels"), "SPI_GetNumChannels should be bound."


@pytest.mark.integration
def test_spi_get_channels_and_info(bindings: LibMPSSELoader):
    """Querying the channel count and each channel's info must not raise."""
    spi = SPIInterface(bindings)

    num = spi.get_num_channels()
    assert isinstance(num, int) and num >= 0, "Channel count must be a non-negative int."

    for index in range(num):
        info = spi.get_channel_info(index)
        # Fields are decoded from the native struct; check their basic shape.
        assert isinstance(info.serial_number, str)
        assert isinstance(info.description, str)


@pytest.mark.integration
def test_spi_open_and_init_channel(bindings: LibMPSSELoader):
    """Open, initialize and close a channel must not raise.

    The SPI helpers return ``None`` on success and raise ``RuntimeError`` on
    failure, so simply calling them without an exception being raised is the
    assertion: pytest fails the test automatically if any call raises.
    """
    channel_config = SPIChannelConfig(
        clock_rate=20000000,  # 20 MHz
        latency_timer=1,      # 1 ms
        config_options=0,
        pin=0x8B8B8B8B,
    )
    spi = SPIInterface(bindings)
    if spi.get_num_channels() == 0:
        pytest.skip("No SPI channels available to test.")

    handle = spi.open_channel(0)
    assert handle.value, "open_channel should return a non-null handle."

    try:
        # Raises RuntimeError on failure; reaching the next line means success.
        spi.init_channel(handle, channel_config)
    finally:
        # Always release the channel, even if init_channel raised above.
        spi.close_channel(handle)

@pytest.mark.integration
def test_spi_read_write(bindings: LibMPSSELoader):
    """A full-duplex read_write transfer must not raise and must clock in one
    byte for every byte clocked out."""
    channel_config = SPIChannelConfig(
        clock_rate=4000000,   # 4 MHz
        latency_timer=1,      # 1 ms
        config_options=0,
        pin=0x8B8B8B8B,       #Indigo4 chip settings for CS, SK, DO, DI pins
    )
    spi = SPIInterface(bindings)
    if spi.get_num_channels() == 0:
        pytest.skip("No SPI channels available to test.")

    handle = spi.open_channel(0)
    assert handle.value, "open_channel should return a non-null handle."

    try:
        spi.init_channel(handle, channel_config)

        spi.toggle_cs(handle, False)  # pull down CS

        write_data = bytes([0xA4, 0x04, 0x30, 0x10, 0x60, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00])
        read_data = spi.read_write(handle, write_data, transfer_options=0x0)

        # SPI is full-duplex: exactly one byte is read for each byte written.
        assert len(read_data) == len(write_data)
    finally:
        spi.toggle_cs(handle, True)  # release CS
        spi.close_channel(handle)

