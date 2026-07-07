
import ctypes
from dataclasses import dataclass
from typing import Optional

from .libmpsse_bindings import FT_DEVICE_LIST_INFO_NODE
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

    def SPI_GetChannelInfo(self, index) -> FT_DEVICE_LIST_INFO_NODE:
        chan_info = FT_DEVICE_LIST_INFO_NODE()
        status = self.bindings.libmpsse_dll.SPI_GetChannelInfo(index, ctypes.byref(chan_info))
        if status != FT_STATUS.FT_OK.value:
            raise Exception(f"Failed to get channel info for index {index}. Status: {status}")
        return chan_info
    
    

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
    