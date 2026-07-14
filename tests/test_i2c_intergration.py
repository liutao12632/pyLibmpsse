import os
import time

from pyLibmpsse.libmpsse_bindings import LibMPSSELoader
from pyLibmpsse.i2c import I2CChannelConfig, I2CInterface

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
    return LibMPSSELoader(libmpsse_path=libmpsse_path, ftd2xx_path=ftd2xx_path)


@pytest.mark.integration
def test_bindings_loads_dlls(bindings: LibMPSSELoader):
    assert bindings.ftd2xx_dll is not None, "ftd2xx.dll should be loaded."
    assert bindings.libmpsse_dll is not None, "libmpsse.dll should be loaded."
    assert hasattr(bindings.libmpsse_dll, "SPI_GetNumChannels"), "SPI_GetNumChannels should be bound."


@pytest.mark.integration
def test_i2c_get_channels_and_info(bindings: LibMPSSELoader):
    """Querying the channel count and each channel's info must not raise."""
    i2c = I2CInterface(bindings)
    num = i2c.get_num_channels()
    assert isinstance(num, int) and num >= 0, "Channel count must be a non-negative int."
    
    print(f"Found {num} I2C channels.")

    for index in range(num):
        info = i2c.get_channel_info(index)
        print(f"Channel {index}: Serial={info.serial_number}, Description={info.description}")
        # Fields are decoded from the native struct; check their basic shape.
        assert isinstance(info.serial_number, str)
        assert isinstance(info.description, str)

@pytest.mark.integration
def test_i2c_open_and_init_channel(bindings: LibMPSSELoader):
    """Open, initialize and close a channel must not raise.

    The I2C helpers return ``None`` on success and raise ``RuntimeError`` on
    failure, so simply calling them without an exception being raised is the
    assertion: pytest fails the test automatically if any call raises.
    """
    i2c = I2CInterface(bindings)
    channel_config = I2CChannelConfig(
        clock_rate=400000,  # 400 kHz
        latency_timer=1,
        options=3,
        pin=0
    )
    handle = i2c.open_channel(0)
    i2c.init_channel(handle, channel_config)
    i2c.close_channel(handle)

@pytest.mark.integration
def test_i2c_read_write(bindings: LibMPSSELoader):
    """Perform a read and write operation on an I2C channel.

    This test assumes that there is a device connected to the I2C bus that can
    respond to the read and write operations. Adjust the address and data as
    necessary for your specific hardware setup.
    """
    i2c = I2CInterface(bindings)
    channel_config = I2CChannelConfig(
        clock_rate=400000,  # 400 kHz
        latency_timer=1,
        options=3,
        pin=0x0
    )
    i2c_slave_addr = 0x32  # Example I2C slave address; change as needed
    handle = i2c.open_channel(1)
    try:
        i2c.init_channel(handle, channel_config)

        time.sleep(0.1)  # Allow some time for the device to be ready
        # Example write operation (adjust address and data as needed)
        write_data = bytes([0x02, 0x00, 0x20, 0x7C, 0x61])
        bytes_written = i2c.write(handle, i2c_slave_addr, write_data, 0x13)
        assert bytes_written == len(write_data), "Not all bytes were written."

        # Example read operation (adjust address and length as needed)
        read_length = 4
        read_data = i2c.read(handle, i2c_slave_addr, read_length, 0x13)
        assert len(read_data) == read_length, "Did not read the expected number of bytes."
    finally:
        # Always release the channel, even if a transfer above raised.
        i2c.close_channel(handle)