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
    spi = SPIInterface(bindings)
    num = spi.get_num_channels()
    print(f"Number of SPI channels: {num}")

    for index in range(num):
        channel_info = spi.get_channel_info(index)
        print(f"Channel {index}: {channel_info}")
    
@pytest.mark.integration
def test_spi_open_and_init_channel(bindings: LibMPSSELoader):
    
    channel_config = SPIChannelConfig(
        clock_rate=20000000,  # 20 MHz
        latency_timer=1,      # 1 ms
        config_options=0,     # Default options
        pin=0x8B8B8B8B        # Default pin
    )
    spi = SPIInterface(bindings)
    num = spi.get_num_channels()
    if num == 0:
        pytest.skip("No SPI channels available to test.")

    handle = spi.open_channel(0)
    assert handle is not None, "Failed to open SPI channel."

    status = spi.init_channel(handle, channel_config)
    assert status is None, "Failed to initialize SPI channel."

    status = spi.close_channel(handle)
    assert status is None, "Failed to close SPI channel."
