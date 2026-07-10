
import ctypes
from dataclasses import dataclass
from typing import Optional

from pyLibmpsse.consts import FT_STATUS
from pyLibmpsse.libmpsse_bindings import NativeFT_DEVICE_LIST_INFO_NODE, NativeChannelConfig

@dataclass(frozen=True)
class SPIChannelConfig:
    clock_rate: int
    latency_timer: int
    config_options: int
    pin: int
    reserved: int = 0  # Reserved field for alignment, default to 0

@dataclass(frozen=True)
class FTHandle:
    value: int

@dataclass(frozen=True)
class SPIChannelInfo:
    flags: int
    type: int
    id: int
    loc_id: int
    serial_number: str
    description: str
    ft_handle: Optional[FTHandle]

class SPIInterface:
    def __init__(self, bindings):
        self.bindings = bindings
    
    """
    Original low-level wrapper for SPI functions. 
    Functions under this level are direct wrappers of the C functions in libMPSSE.
    They are designed to be used internally by the higher-level Pythonic wrapper methods
    or for those who want direct access to the underlying C functions.
    Please note that these functions may require additional handling of pointers and memory
    management, as they are direct bindings to the C library.
    """
    def SPI_GetNumChannels(self, numChannels) -> ctypes.c_uint32:
        """
        Get the number of available SPI channels.
        param numChannels: Pointer to a DWORD that will receive the number of channels.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_GetNumChannels(numChannels)
        return status

    def SPI_GetChannelInfo(self, index, chanInfo) -> ctypes.c_uint32:
        """
        Get information about a specific SPI channel.
        param index: Index of the channel to query.
        param chanInfo: Pointer to an FT_DEVICE_LIST_INFO_NODE structure that will receive the channel information.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_GetChannelInfo(index, chanInfo)
        return status
    
    def SPI_OpenChannel(self, index, handle) -> ctypes.c_uint32:
        """
        Open a specific SPI channel.
        param index: Index of the channel to open.
        param handle: Pointer to an FT_HANDLE that will receive the handle to the opened channel.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_OpenChannel(index, handle)
        return status
    
    def SPI_InitChannel(self, handle, config) -> ctypes.c_uint32:
        """
        Initialize a specific SPI channel.
        param handle: Handle to the channel to initialize.
        param config: Pointer to a ChannelConfig structure that contains the channel configuration.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_InitChannel(handle, config)
        return status

    def SPI_CloseChannel(self, handle) -> ctypes.c_uint32:
        """ 
        Close a specific SPI channel.
        param handle: Handle to the channel to close.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_CloseChannel(handle)
        return status
    
    def SPI_Read(self, handle, buffer, sizeToTransfer, sizeTransferred, transferOptions) -> ctypes.c_uint32:
        """
        Read data from a specific SPI channel.
        param handle: Handle to the channel to read from.
        param buffer: Pointer to a buffer that will receive the read data.
        param sizeToTransfer: Number of bytes to read.
        param sizeTransferred: Pointer to a variable that will receive the number of bytes actually read.
        param transferOptions: Options for the transfer.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_Read(handle, buffer, sizeToTransfer, sizeTransferred, transferOptions)
        return status
    
    def SPI_Write(self, handle, buffer, sizeToTransfer, sizeTransferred, transferOptions) -> ctypes.c_uint32:
        """
        Write data to a specific SPI channel.
        param handle: Handle to the channel to write to.
        param buffer: Pointer to a buffer that contains the data to write.
        param sizeToTransfer: Number of bytes to write.
        param sizeTransferred: Pointer to a variable that will receive the number of bytes actually written.
        param transferOptions: Options for the transfer.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_Write(handle, buffer, sizeToTransfer, sizeTransferred, transferOptions)
        return status
    
    def SPI_ReadWrite(self, handle, inBuffer, outBuffer, sizeToTransfer, sizeTransferred, transferOptions) -> ctypes.c_uint32:
        """
        Read and write data to/from a specific SPI channel.
        param handle: Handle to the channel to read from and write to.
        param inBuffer: Pointer to a buffer that contains the data to write.
        param outBuffer: Pointer to a buffer that will receive the read data.
        param sizeToTransfer: Number of bytes to transfer.
        param sizeTransferred: Pointer to a variable that will receive the number of bytes actually transferred.
        param transferOptions: Options for the transfer.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_ReadWrite(handle, inBuffer, outBuffer, sizeToTransfer, sizeTransferred, transferOptions)
        return status
    
    def SPI_IsBusy(self, handle, state) -> ctypes.c_uint32:
        """
        Check if a specific SPI channel is busy.
        param handle: Handle to the channel to check.
        param state: Pointer to a boolean that will receive the busy state (True if busy, False if not).
        return: FT_STATUS indicating success or failure.
        """ 
        status = self.bindings.libmpsse_dll.SPI_IsBusy(handle, state)
        return status

    def SPI_ChangeCS(self, handle, configOptions) -> ctypes.c_uint32:
        """
        Change the chip select configuration for a specific SPI channel.
        param handle: Handle to the channel to change.
        param configOptions: Options for the chip select configuration.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_ChangeCS(handle, configOptions)
        return status
    
    """
    Pythonic wrapper methods for SPI functions.
    Suggest to use these methods for a more Pythonic interface to the SPI functions.
    These methods handle the necessary pointer and memory management, and return Python-native types.
    """
    def get_num_channels(self) -> int:
        """
        Get the number of available SPI channels.
        return: Number of available SPI channels."""
        num_channels = ctypes.c_uint32()
        status = self.SPI_GetNumChannels(ctypes.byref(num_channels))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to get number of channels. Status: {status}")
        return num_channels.value
    
    def get_channel_info(self, index) -> SPIChannelInfo:
        """
        Get information about a specific SPI channel.
        param index: Index of the channel to retrieve information for.
        return: SPIChannelInfo object containing the channel information.
        """
        chan_info = NativeFT_DEVICE_LIST_INFO_NODE()
        status = self.SPI_GetChannelInfo(index, ctypes.byref(chan_info))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to get channel info. Status: {status}")
        info_wrapper = SPIChannelInfo(
            flags=chan_info.Flags,
            type=chan_info.Type,
            id=chan_info.ID,
            loc_id=chan_info.LocId,
            serial_number=chan_info.SerialNumber.decode('utf-8').rstrip('\x00'),
            description=chan_info.Description.decode('utf-8').rstrip('\x00'),
            ft_handle=FTHandle(chan_info.ftHandle) if chan_info.ftHandle else None
        )
        return info_wrapper

    def open_channel(self, index) -> FTHandle:
        """
        Open a specific SPI channel.
        param index: Index of the channel to open.
        return: FTHandle object representing the opened channel.
        """
        handle = ctypes.c_void_p()
        status = self.SPI_OpenChannel(index, ctypes.byref(handle))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to open channel. Status: {status}")
        return FTHandle(handle.value)
    
    def init_channel(self, handle: FTHandle, config: SPIChannelConfig) -> None:
        """
        Initialize a specific SPI channel.
        param handle: Handle to the channel to initialize.
        param config: Configuration for the SPI channel.
        return: None. Raises RuntimeError on failure.
        """
        # Assuming default configuration for initialization
        # Manual truncation for now: keep low bits matching native field width.
        native_config = NativeChannelConfig(
            ClockRate=config.clock_rate & 0xFFFFFFFF,
            LatencyTimer=config.latency_timer & 0xFF,
            configOptions=config.config_options & 0xFFFFFFFF,
            Pin=config.pin & 0xFFFFFFFF,
            Reserved=0x0  # Reserved field for alignment
        )
        native_handle = ctypes.c_void_p(handle.value)
        status = self.SPI_InitChannel(native_handle, ctypes.byref(native_config))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to initialize channel. Status: {status}")
    
    def close_channel(self, handle: FTHandle) -> None:
        """
        Close a specific SPI channel.
        param handle: Handle to the channel to close.
        return: None. Raises RuntimeError on failure.
        """
        status = self.SPI_CloseChannel(ctypes.c_void_p(handle.value))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to close channel. Status: {status}")

    