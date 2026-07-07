"""
Load ftd2xx.dll and libmpsse.dll.
Now only support windows platform.
"""

import inspect
import os
import sys
import ctypes
from typing import Optional
from .errors import DLLLoadError, PlatformError

class FT_DEVICE_LIST_INFO_NODE(ctypes.Structure):
    """
    C structure definition for FT_DEVICE_LIST_INFO_NODE.

    Attributes:
        Flags: Device status flags from D2XX/libMPSSE.
        Type: FTDI device type identifier.
        ID: Vendor/device identifier.
        LocId: Physical location ID reported by the driver.
        SerialNumber: Null-terminated serial number buffer, length 16.
        Description: Null-terminated device description buffer, length 64.
        ftHandle: Native FTDI device handle, or NULL if unopened.
    """
    """
    C definition:
        typedef struct _ft_device_list_info_node {
            DWORD Flags;
            DWORD Type;
            DWORD ID;
            DWORD LocId;
            char SerialNumber[16];
            char Description[64];
            FT_HANDLE ftHandle;
        } FT_DEVICE_LIST_INFO_NODE;
    """
    _fields_ = [
        ("Flags", ctypes.c_uint32),
        ("Type", ctypes.c_uint32),
        ("ID", ctypes.c_uint32),
        ("LocId", ctypes.c_uint32),
        ("SerialNumber", ctypes.c_char * 16),
        ("Description", ctypes.c_char * 64),
        ("ftHandle", ctypes.c_void_p)
    ]

class LibMPSSELoader:

    def __init__(self, ftd2xx_path=None, libmpsse_path=None):
        self.ftd2xx_dll = None
        self.libmpsse_dll = None
        
        if ftd2xx_path is None:
            raise ValueError("ftd2xx_path must be provided.")
        if libmpsse_path is None:
            raise ValueError("libmpsse_path must be provided.")
        
        self.load_ftd2xx_path = ftd2xx_path
        self.load_mpsse_path = libmpsse_path

        self._load_dlls(libmpsse_path, ftd2xx_path)
        self._bind_MPSSE_function()

    def _bind_SPI_functions(self):
        # Bind SPI functions

        # function prototype: FT_STATUS SPI_GetNumChannels(DWORD* numChannels)
        self.libmpsse_dll.SPI_GetNumChannels.argtypes = [
            ctypes.POINTER(ctypes.c_uint32)]
        self.libmpsse_dll.SPI_GetNumChannels.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_GetChannelInfo (uint32 index, FT_DEVICE_LIST_INFO_NODE *chanInfo)#
        self.libmpsse_dll.SPI_GetChannelInfo.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(FT_DEVICE_LIST_INFO_NODE)]
        self.libmpsse_dll.SPI_GetChannelInfo.restype = ctypes.c_uint32



    def _bind_MPSSE_function(self):
        if self.libmpsse_dll is None:
            raise PlatformError("libmpsse.dll is not loaded. Please call load_dlls() first.")
        
        self._bind_SPI_functions()

    def _load_dlls(self,
                  libmpsse_path: Optional[str] = None,
                  ftd2xx_path: Optional[str] = None) -> None:
        
        self.load_ftd2xx_path = ftd2xx_path
        self.load_mpsse_path = libmpsse_path
        try:
            self.ftd2xx_dll = ctypes.WinDLL(ftd2xx_path)
        except OSError as e:
            raise DLLLoadError(f"Failed to load ftd2xx.dll: {e}")
        
        try:
            self.libmpsse_dll = ctypes.CDLL(libmpsse_path)
        except OSError as e:
            raise DLLLoadError(f"Failed to load libmpsse.dll from {self.load_mpsse_path}: {e}")