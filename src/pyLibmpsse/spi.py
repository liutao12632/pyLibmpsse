
import ctypes
from dataclasses import dataclass
from typing import Optional

from .libmpsse_bindings import FT_DEVICE_LIST_INFO_NODE, ChannelConfig
from .consts import FT_STATUS

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
    Original wrapper methods for SPI functions
    """
    def SPI_GetNumChannels(self) -> ctypes.c_uint32:
        num_channels = ctypes.c_uint32()
        status = self.bindings.libmpsse_dll.SPI_GetNumChannels(ctypes.byref(num_channels))
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to get number of SPI channels. Status: {status}")
        return num_channels

    def SPI_GetChannelInfo(self, index, chan_info: ) -> ctypes.c_uint32:
        chan_info = FT_DEVICE_LIST_INFO_NODE()
        status = self.bindings.libmpsse_dll.SPI_GetChannelInfo(index, ctypes.byref(chan_info))
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to get channel info for index {index}. Status: {status}")
        return chan_info
    
    def SPI_OpenChannel(self, index) -> ctypes.c_void_p:
        handle = ctypes.c_void_p()
        status = self.bindings.libmpsse_dll.SPI_OpenChannel(index, ctypes.byref(handle))
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to open channel for index {index}. Status: {status}")
        return handle
    
    def SPI_InitChannel(self, handle, config: ChannelConfig) -> ctypes.c_uint32:
        status = self.bindings.libmpsse_dll.SPI_InitChannel(handle, ctypes.byref(config))
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to initialize channel. Status: {status}")
        return status

    def SPI_CloseChannel(self, handle) -> ctypes.c_uint32:
        status = self.bindings.libmpsse_dll.SPI_CloseChannel(handle)
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to close channel. Status: {status}")
        return status
    
    def SPI_Read(self, handle, buffer, sizeToTransfer, sizeTransferred, transferOptions) -> ctypes.c_uint32:
        status = self.bindings.libmpsse_dll.SPI_Read(handle, buffer, sizeToTransfer, ctypes.byref(sizeTransferred), transferOptions)
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to read from channel. Status: {status}")   
        return status
    
    def SPI_Write(self, handle, buffer, sizeToTransfer, sizeTransferred, transferOptions) -> ctypes.c_uint32:
        status = self.bindings.libmpsse_dll.SPI_Write(handle, buffer, sizeToTransfer, ctypes.byref(sizeTransferred), transferOptions)
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to write to channel. Status: {status}")
        return status
    
    def SPI_ReadWrite(self, handle, inBuffer, outBuffer, sizeToTransfer, sizeTransferred, transferOptions) -> ctypes.c_uint32:
        status = self.bindings.libmpsse_dll.SPI_ReadWrite(handle, inBuffer, outBuffer, sizeToTransfer, ctypes.byref(sizeTransferred), transferOptions)
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to read/write from/to channel. Status: {status}")
        return status
    
    def SPI_IsBusy(self, handle, state) -> ctypes.c_uint32:
        status = self.bindings.libmpsse_dll.SPI_IsBusy(handle, ctypes.byref(state))
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to check if channel is busy. Status: {status}")
        return state

    def SPI_ChangeCS(self, handle, configOptions) -> ctypes.c_uint32:
        status = self.bindings.libmpsse_dll.SPI_ChangeCS(handle, configOptions)
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to change chip select. Status: {status}")
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
    