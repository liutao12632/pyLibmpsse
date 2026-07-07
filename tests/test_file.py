import pytest
import pyLibmpsse
from pyLibmpsse.libmpsse_bindings import LibMPSSELoader

@pytest.mark.integration
def test_bindings_loads_dlls():
    # Provide the paths to the DLLs
    ftd2xx_path = "ftd2xx.dll"
    libmpsse_path = r"D:\Code\Repo\LibMPSSE_1.0.7\Windows\release\build\x64\DLL\libmpsse.dll"

    # Create an instance of LibMPSSEBindings
    bindings = pyLibmpsse.libmpsse_bindings.LibMPSSELoader(ftd2xx_path, libmpsse_path)

    # Check if the DLLs are loaded
    assert bindings.ftd2xx_dll is not None, "ftd2xx.dll should be loaded."
    assert bindings.libmpsse_dll is not None, "libmpsse.dll should be loaded."

    # Check if the SPI_GetNumChannels function is bound correctly
    assert hasattr(bindings.libmpsse_dll, 'SPI_GetNumChannels'), "SPI_GetNumChannels should be bound."

@pytest.mark.integration
def test_spi_get_channels_and_info():
    # Provide the paths to the DLLs
    ftd2xx_path = "ftd2xx.dll"
    libmpsse_path = r"D:\Code\Repo\LibMPSSE_1.0.7\Windows\release\build\x64\DLL\libmpsse.dll"

    # Create an instance of LibMPSSEBindings
    bindings = LibMPSSELoader(ftd2xx_path, libmpsse_path)

    # Check if the DLLs are loaded
    assert bindings.ftd2xx_dll is not None, "ftd2xx.dll should be loaded."
    assert bindings.libmpsse_dll is not None, "libmpsse.dll should be loaded."

    # Check if the SPI_GetNumChannels function is bound correctly
    assert hasattr(bindings.libmpsse_dll, 'SPI_GetNumChannels'), "SPI_GetNumChannels should be bound."

    SPI_instance = pyLibmpsse.SPIInterface(bindings)
    num = SPI_instance.get_num_channels()  # This will call the bound function and should not raise an exception
    print(f"Number of SPI channels: {num}")

    for index in range(num):
        channel_info = SPI_instance.get_channel_info(index)
        print(f"Channel {index}: {channel_info}")