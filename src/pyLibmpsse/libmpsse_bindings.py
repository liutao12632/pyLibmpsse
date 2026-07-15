"""
Load ftd2xx.dll and libmpsse.dll.
Now only support windows platform.
"""

import ctypes
import sys
from typing import Optional
from .errors import DLLLoadError, PlatformError

class NativeChannelConfig (ctypes.Structure):
    """
    C structure definition for ChannelConfig.

    Attributes:
        ClockRate: Clock rate in Hz.
        LatencyTimer: Latency timer value in milliseconds.
        configOptions: Configuration options (bitmask).
        Pin: Pin configuration (bitmask).
        Reserved: Reserved field for alignment. Should not be used directly.
    """
    """
    C definition:
        typedef struct {
            uint32 ClockRate;
            uint8 LatencyTimer;
            uint32 configOptions;
            uint32 Pin;  
            uint16 Reserved;
        } ChannelConfig;
    """
    _fields_ = [
        ("ClockRate", ctypes.c_uint32),
        ("LatencyTimer", ctypes.c_uint8),
        ("configOptions", ctypes.c_uint32),
        ("Pin", ctypes.c_uint32),
        ("Reserved", ctypes.c_uint16)  # Reserved field for alignment
    ]

class NativeI2CChannelConfig(ctypes.Structure):
    """C structure definition for the I2C ChannelConfig.

    C definition (libMPSSE_i2c.h):
        typedef struct {
            I2C_CLOCKRATE ClockRate;   // uint32 enum
            UCHAR         LatencyTimer;
            DWORD         Options;
            DWORD         Pin;
            USHORT        currentPinState;
        } ChannelConfig;
    """
    _fields_ = [
        ("ClockRate", ctypes.c_uint32),
        ("LatencyTimer", ctypes.c_uint8),
        ("Options", ctypes.c_uint32),
        ("Pin", ctypes.c_uint32),
        ("currentPinState", ctypes.c_uint16),
    ]

class NativeFT_DEVICE_LIST_INFO_NODE(ctypes.Structure):
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

    def __init__(self, libmpsse_path=None, ftd2xx_path=None):
        if not sys.platform.startswith("win"):
            raise PlatformError(
                "pyLibmpsse is Windows-only; it requires the FTDI D2XX/libMPSSE "
                f"DLLs and cannot run on platform '{sys.platform}'."
            )
        self.ftd2xx_dll = None
        self.libmpsse_dll = None
        
        if ftd2xx_path is None:
            raise ValueError("ftd2xx_path must be provided.")
        if libmpsse_path is None:
            raise ValueError("libmpsse_path must be provided.")
        
        self.load_ftd2xx_path = ftd2xx_path
        self.load_mpsse_path = libmpsse_path

        self._load_dlls(libmpsse_path, ftd2xx_path)
        self._bind_common_functions()
        self._bind_SPI_functions()
        self._bind_I2C_functions()

    def _bind_common_functions(self):
        # Bind functions shared by all protocols (GPIO, library lifecycle, version).

        # function prototype: FT_STATUS FT_WriteGPIO(FT_HANDLE handle, UCHAR dir, UCHAR value)
        self.libmpsse_dll.FT_WriteGPIO.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint8]
        self.libmpsse_dll.FT_WriteGPIO.restype = ctypes.c_uint32

        # function prototype: FT_STATUS FT_ReadGPIO(FT_HANDLE handle, UCHAR *value)
        self.libmpsse_dll.FT_ReadGPIO.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8)]
        self.libmpsse_dll.FT_ReadGPIO.restype = ctypes.c_uint32

        # NOTE: On Windows, Init_libMPSSE() and Cleanup_libMPSSE() are invoked
        # automatically by the library's DllMain when libmpsse.dll is loaded and
        # unloaded, so this wrapper intentionally never calls them; they are bound
        # only for completeness / advanced use. Do NOT call Init_libMPSSE() again
        # while channels are open -- it re-initializes libMPSSE's internal channel
        # list and would invalidate existing handles. This auto-init behavior is
        # Windows-only; a non-Windows port would have to call Init_libMPSSE() once
        # explicitly after loading the library.
        # function prototype: void Init_libMPSSE(void)
        self.libmpsse_dll.Init_libMPSSE.argtypes = []
        self.libmpsse_dll.Init_libMPSSE.restype = None

        # function prototype: void Cleanup_libMPSSE(void);#
        self.libmpsse_dll.Cleanup_libMPSSE.argtypes = []
        self.libmpsse_dll.Cleanup_libMPSSE.restype = None

        # function prototype: FT_STATUS Ver_libMPSSE(LPDWORD libmpsse, LPDWORD libftd2xx);#
        self.libmpsse_dll.Ver_libMPSSE.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
        self.libmpsse_dll.Ver_libMPSSE.restype = ctypes.c_uint32

    def _bind_SPI_functions(self):
        # Bind SPI functions

        # function prototype: FT_STATUS SPI_GetNumChannels(DWORD* numChannels)
        self.libmpsse_dll.SPI_GetNumChannels.argtypes = [
            ctypes.POINTER(ctypes.c_uint32)]
        self.libmpsse_dll.SPI_GetNumChannels.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_GetChannelInfo (uint32 index, FT_DEVICE_LIST_INFO_NODE *chanInfo)#
        self.libmpsse_dll.SPI_GetChannelInfo.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(NativeFT_DEVICE_LIST_INFO_NODE)]
        self.libmpsse_dll.SPI_GetChannelInfo.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_OpenChannel (uint32 index, FT_HANDLE *handle)
        self.libmpsse_dll.SPI_OpenChannel.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)]
        self.libmpsse_dll.SPI_OpenChannel.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_InitChannel (FT_HANDLE handle, ChannelConfig *config)
        self.libmpsse_dll.SPI_InitChannel.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(NativeChannelConfig)]
        self.libmpsse_dll.SPI_InitChannel.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_CloseChannel (FT_HANDLE handle)
        self.libmpsse_dll.SPI_CloseChannel.argtypes = [ctypes.c_void_p]
        self.libmpsse_dll.SPI_CloseChannel.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_Read(FT_HANDLE handle, uint8 *buffer, uint32 sizeToTransfer, uint32 *sizeTransferred, uint32 transferOptions)#
        self.libmpsse_dll.SPI_Read.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        self.libmpsse_dll.SPI_Read.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_Write(FT_HANDLE handle, uint8 *buffer, uint32 sizeToTransfer, uint32 *sizeTransferred, uint32 transferOptions)#
        self.libmpsse_dll.SPI_Write.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        self.libmpsse_dll.SPI_Write.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_ReadWrite(FT_HANDLE handle, uint8 *inBuffer, uint8 *outBuffer, uint32 sizeToTransfer, uint32 *sizeTransferred, uint32 transferOptions)#
        self.libmpsse_dll.SPI_ReadWrite.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        self.libmpsse_dll.SPI_ReadWrite.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_IsBusy(FT_HANDLE handle, BOOL *state)
        self.libmpsse_dll.SPI_IsBusy.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.libmpsse_dll.SPI_IsBusy.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_ChangeCS(FT_HANDLE handle, uint32 configOptions)
        self.libmpsse_dll.SPI_ChangeCS.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.libmpsse_dll.SPI_ChangeCS.restype = ctypes.c_uint32

        # function prototype: FT_STATUS SPI_ToggleCS(FT_HANDLE handle, BOOL state)
        self.libmpsse_dll.SPI_ToggleCS.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.libmpsse_dll.SPI_ToggleCS.restype = ctypes.c_uint32

    def _bind_I2C_functions(self):
        # Bind I2C functions

        # function prototype: FT_STATUS I2C_GetNumChannels(DWORD *numChannels)
        self.libmpsse_dll.I2C_GetNumChannels.argtypes = [
            ctypes.POINTER(ctypes.c_uint32)]
        self.libmpsse_dll.I2C_GetNumChannels.restype = ctypes.c_uint32

        # function prototype: FT_STATUS I2C_GetChannelInfo(DWORD index, FT_DEVICE_LIST_INFO_NODE *chanInfo)
        self.libmpsse_dll.I2C_GetChannelInfo.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(NativeFT_DEVICE_LIST_INFO_NODE)]
        self.libmpsse_dll.I2C_GetChannelInfo.restype = ctypes.c_uint32

        # function prototype: FT_STATUS I2C_OpenChannel(DWORD index, FT_HANDLE *handle)
        self.libmpsse_dll.I2C_OpenChannel.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)]
        self.libmpsse_dll.I2C_OpenChannel.restype = ctypes.c_uint32

        # function prototype: FT_STATUS I2C_InitChannel(FT_HANDLE handle, ChannelConfig *config)
        self.libmpsse_dll.I2C_InitChannel.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(NativeI2CChannelConfig)]
        self.libmpsse_dll.I2C_InitChannel.restype = ctypes.c_uint32

        # function prototype: FT_STATUS I2C_CloseChannel(FT_HANDLE handle)
        self.libmpsse_dll.I2C_CloseChannel.argtypes = [ctypes.c_void_p]
        self.libmpsse_dll.I2C_CloseChannel.restype = ctypes.c_uint32

        # function prototype: FT_STATUS I2C_DeviceRead(FT_HANDLE handle, UCHAR deviceAddress, DWORD sizeToTransfer, UCHAR *buffer, LPDWORD sizeTransferred, DWORD options)
        self.libmpsse_dll.I2C_DeviceRead.argtypes = [
            ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        self.libmpsse_dll.I2C_DeviceRead.restype = ctypes.c_uint32

        # function prototype: FT_STATUS I2C_DeviceWrite(FT_HANDLE handle, UCHAR deviceAddress, DWORD sizeToTransfer, UCHAR *buffer, LPDWORD sizeTransferred, DWORD options)
        self.libmpsse_dll.I2C_DeviceWrite.argtypes = [
            ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        self.libmpsse_dll.I2C_DeviceWrite.restype = ctypes.c_uint32

        # function prototype: FT_STATUS I2C_GetDeviceID(FT_HANDLE handle, UCHAR deviceAddress, UCHAR *deviceID)
        self.libmpsse_dll.I2C_GetDeviceID.argtypes = [
            ctypes.c_void_p, ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8)]
        self.libmpsse_dll.I2C_GetDeviceID.restype = ctypes.c_uint32

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
