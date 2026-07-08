
import ctypes
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SPIChannelInfo:
    flags: int
    type: int
    id: int
    loc_id: int
    serial_number: str
    description: str
    ft_handle: Optional[int]

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
    Pythonic wrapper methods for SPI functions
    """
    def get_num_channels(self) -> int:
        num_channels = self.SPI_GetNumChannels()
        return num_channels.value
    
    def get_channel_info(self, index) -> SPIChannelInfo:
        info = self.SPI_GetChannelInfo(index)
        info_wrapper = SPIChannelInfo(
            flags=info.Flags,
            type=info.Type,
            id=info.ID,
            loc_id=info.LocId,
            serial_number=info.SerialNumber.decode('utf-8').rstrip('\x00'),
            description=info.Description.decode('utf-8').rstrip('\x00'),
            ft_handle=info.ftHandle if info.ftHandle else None
        )
        return info_wrapper
    