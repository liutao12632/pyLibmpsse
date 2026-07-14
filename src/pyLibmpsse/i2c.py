
import ctypes
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from pyLibmpsse.consts import FT_STATUS
from pyLibmpsse.common import FTHandle, ChannelInfo
from pyLibmpsse.libmpsse_bindings import (
    NativeFT_DEVICE_LIST_INFO_NODE,
    NativeI2CChannelConfig,
)


@dataclass(frozen=True)
class I2CChannelConfig:
    clock_rate: int          # Hz, or a value from consts.I2C_CLOCK_RATE
    latency_timer: int       # ms, valid range 2..255
    options: int = 0         # bitmask from consts.I2C_CONFIG_OPTIONS
    pin: int = 0             # initial/final pin direction & value bytes


class I2CInterface:
    """I2C access for libMPSSE, exposed as two tiers of methods.

    Low-level bindings (``I2C_*`` / ``FT_*``)
        Thin, 1:1 wrappers around the C functions in libMPSSE. They mirror the C
        signatures and return the raw ``FT_STATUS`` code. The caller is
        responsible for ctypes pointer/buffer handling and memory management, and
        arguments (including the device address and transfer options) are passed
        through unchanged. Intended for internal use or advanced callers.

    Pythonic helpers (``get_num_channels``, ``read``, ``write`` ...)
        High-level methods built on top of the low-level bindings. They perform
        the pointer/buffer marshalling, accept and return native Python types
        (``bytes``, ``int``), treat the device address as a 7-bit value, and raise
        ``RuntimeError`` on failure instead of returning a status code. These are
        the recommended entry points.
    """

    def __init__(self, bindings):
        self.bindings = bindings

    # ==================================================================
    # Low-level bindings: direct 1:1 wrappers of the libMPSSE C functions.
    # The caller manages ctypes pointers/buffers and passes every argument
    # (address, options, ...) through unchanged; each method returns the raw
    # FT_STATUS code. Prefer the Pythonic helpers below unless you need direct
    # access to the C API.
    # ==================================================================
    def I2C_GetNumChannels(self, numChannels) -> int:
        """
        Get the number of available I2C channels.
        param numChannels: Pointer to a DWORD that will receive the number of channels.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.I2C_GetNumChannels(numChannels)
        return status

    def I2C_GetChannelInfo(self, index, chanInfo) -> int:
        """
        Get information about a specific I2C channel.
        param index: Index of the channel to query (see get_channel_info for the 0-based note).
        param chanInfo: Pointer to an FT_DEVICE_LIST_INFO_NODE structure that will receive the info.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.I2C_GetChannelInfo(index, chanInfo)
        return status

    def I2C_OpenChannel(self, index, handle) -> int:
        """
        Open a specific I2C channel.
        param index: Index of the channel to open.
        param handle: Pointer to an FT_HANDLE that will receive the handle to the opened channel.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.I2C_OpenChannel(index, handle)
        return status

    def I2C_InitChannel(self, handle, config) -> int:
        """
        Initialize a specific I2C channel.
        param handle: Handle to the channel to initialize.
        param config: Pointer to a ChannelConfig structure with the channel configuration.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.I2C_InitChannel(handle, config)
        return status

    def I2C_CloseChannel(self, handle) -> int:
        """
        Close a specific I2C channel.
        param handle: Handle to the channel to close.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.I2C_CloseChannel(handle)
        return status

    def I2C_DeviceRead(self, handle, deviceAddress, sizeToTransfer, buffer, sizeTransferred, options) -> int:
        """
        Read data from an addressed I2C slave.
        param handle: Handle to the channel.
        param deviceAddress: Slave address passed through unchanged (no masking at this layer).
        param sizeToTransfer: Number of bytes (or bits, for fast-transfer options) to read.
        param buffer: Pointer to a buffer that will receive the read data.
        param sizeTransferred: Pointer to a variable that will receive the number of bytes read.
        param options: Bitmask of I2C_TRANSFER_OPTIONS (see read() for the flag meanings).
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.I2C_DeviceRead(
            handle, deviceAddress, sizeToTransfer, buffer, sizeTransferred, options)
        return status

    def I2C_DeviceWrite(self, handle, deviceAddress, sizeToTransfer, buffer, sizeTransferred, options) -> int:
        """
        Write data to an addressed I2C slave.
        param handle: Handle to the channel.
        param deviceAddress: Slave address passed through unchanged (no masking at this layer).
        param sizeToTransfer: Number of bytes (or bits, for fast-transfer options) to write.
        param buffer: Pointer to a buffer that contains the data to write.
        param sizeTransferred: Pointer to a variable that will receive the number of bytes written.
        param options: Bitmask of I2C_TRANSFER_OPTIONS (see write() for the flag meanings).
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.I2C_DeviceWrite(
            handle, deviceAddress, sizeToTransfer, buffer, sizeTransferred, options)
        return status

    def I2C_GetDeviceID(self, handle, deviceAddress, deviceID) -> int:
        """
        Retrieve the 3-byte I2C device ID.
        param handle: Handle to the channel.
        param deviceAddress: Slave address passed through unchanged (no masking at this layer).
        param deviceID: Pointer to a 3-byte buffer that will receive the device ID.
        return: FT_STATUS indicating success or failure (FT_NOT_SUPPORTED if the library
                was built without device-ID support).
        """
        status = self.bindings.libmpsse_dll.I2C_GetDeviceID(handle, deviceAddress, deviceID)
        return status

    def FT_WriteGPIO(self, handle, dir, value) -> int:
        """
        Write to the GPIO pins of a specific channel.
        param handle: Handle to the channel to write to.
        param dir: Direction of the GPIO pins (1 for output, 0 for input).
        param value: Value to write to the GPIO pins.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.FT_WriteGPIO(handle, dir, value)
        return status

    def FT_ReadGPIO(self, handle, value) -> int:
        """
        Read the value of the GPIO pins of a specific channel.
        param handle: Handle to the channel to read from.
        param value: Pointer to a UCHAR that will receive the GPIO state.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.FT_ReadGPIO(handle, value)
        return status

    def Ver_libMPSSE(self, libmpsse, libftd2xx) -> int:
        """
        Get the version numbers of the libMPSSE and libFTD2XX libraries.
        param libmpsse: Pointer to a DWORD that will receive the libMPSSE version.
        param libftd2xx: Pointer to a DWORD that will receive the libFTD2XX version.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.Ver_libMPSSE(libmpsse, libftd2xx)
        return status

    # ==================================================================
    # Pythonic helpers (recommended): built on top of the low-level
    # bindings above. They handle pointer/buffer marshalling, accept and
    # return native Python types, treat the device address as 7-bit, and
    # raise RuntimeError on failure instead of returning a status code.
    # ==================================================================
    def get_num_channels(self) -> int:
        """
        Get the number of available I2C channels.
        return: Number of available I2C channels. Raises RuntimeError on failure.
        """
        num_channels = ctypes.c_uint32()
        status = self.I2C_GetNumChannels(ctypes.byref(num_channels))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to get number of channels. Status: {status}")
        return num_channels.value

    def get_channel_info(self, index: int) -> ChannelInfo:
        """
        Get information about a specific I2C channel.
        param index: 0-based channel index (0 to get_num_channels() - 1).
        return: ChannelInfo object containing the channel information. Raises RuntimeError on failure.
        """
        chan_info = NativeFT_DEVICE_LIST_INFO_NODE()
        status = self.I2C_GetChannelInfo(index, ctypes.byref(chan_info))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to get channel info. Status: {status}")
        return ChannelInfo(
            flags=chan_info.Flags,
            type=chan_info.Type,
            id=chan_info.ID,
            loc_id=chan_info.LocId,
            serial_number=chan_info.SerialNumber.decode('utf-8').rstrip('\x00'),
            description=chan_info.Description.decode('utf-8').rstrip('\x00'),
            ft_handle=FTHandle(chan_info.ftHandle) if chan_info.ftHandle else None,
        )

    def open_channel(self, index: int) -> FTHandle:
        """
        Open a specific I2C channel.
        param index: 0-based channel index (0 to get_num_channels() - 1), per libMPSSE_i2c.h.
        return: FTHandle representing the opened channel. Raises RuntimeError on failure.
        """
        handle = ctypes.c_void_p()
        status = self.I2C_OpenChannel(index, ctypes.byref(handle))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to open channel. Status: {status}")
        return FTHandle(handle.value)

    def init_channel(self, handle: FTHandle, config: I2CChannelConfig) -> None:
        """
        Initialize a specific I2C channel.
        param handle: Handle to the channel to initialize.
        param config: Configuration for the I2C channel.
        return: None. Raises RuntimeError on failure.
        """
        native_config = NativeI2CChannelConfig(
            ClockRate=config.clock_rate & 0xFFFFFFFF,
            LatencyTimer=config.latency_timer & 0xFF,
            Options=config.options & 0xFFFFFFFF,
            Pin=config.pin & 0xFFFFFFFF,
            currentPinState=0,
        )
        native_handle = ctypes.c_void_p(handle.value)
        status = self.I2C_InitChannel(native_handle, ctypes.byref(native_config))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to initialize channel. Status: {status}")

    def close_channel(self, handle: FTHandle) -> None:
        """
        Close a specific I2C channel.
        param handle: Handle to the channel to close.
        return: None. Raises RuntimeError on failure.
        """
        status = self.I2C_CloseChannel(ctypes.c_void_p(handle.value))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to close channel. Status: {status}")

    @contextmanager
    def open_initialized(self, index: int, config: I2CChannelConfig) -> Iterator[FTHandle]:
        """
        Open and initialize an I2C channel as a context manager (recommended).

        Opens the channel at ``index``, initializes it with ``config``, and yields
        the resulting handle. The channel is always closed when leaving the
        ``with`` block, even if an exception is raised inside it, so the handle
        can never leak.

        This is a convenience wrapper over ``open_channel`` / ``init_channel`` /
        ``close_channel``; those methods remain fully usable for manual lifecycle
        management when a single ``with`` block is not a good fit.

        param index: 1-based channel index (per libMPSSE_i2c.h).
        param config: Configuration applied via init_channel.
        return: Context manager yielding the opened, initialized FTHandle.
                Raises RuntimeError if opening or initialization fails.

        Example:
            with i2c.open_initialized(1, config) as handle:
                i2c.write(handle, addr, data, options)
        """
        handle = self.open_channel(index)
        try:
            self.init_channel(handle, config)
            yield handle
        finally:
            self.close_channel(handle)

    def read(self, handle: FTHandle, device_address: int, size: int, options: int) -> bytes:
        """
        Read bytes from an addressed I2C slave.
        param handle: Handle to the channel.
        param device_address: 7-bit slave address. Only bits[6:0] are used; the read
                              direction bit is appended by libMPSSE (this is a read).
        param size: Number of bytes to read.
        param options: Bitmask of I2C_TRANSFER_OPTIONS (required; the caller decides):
            START_BIT (0x01)      - generate a START condition before the transfer.
            STOP_BIT (0x02)       - generate a STOP condition after the transfer.
            BREAK_ON_NACK (0x04)  - stop transferring when the slave NACKs.
            NACK_LAST_BYTE (0x08) - have the master NACK the last byte read (many
                                    slaves require this to terminate a read).
            FAST_TRANSFER_BYTES (0x10) / FAST_TRANSFER_BITS (0x20) - fast-transfer
                                    modes; with BITS, ``size`` is counted in bits.
            NO_ADDRESS (0x40)     - skip the address phase.
        return: Bytes read (length equals the number actually transferred).
                Raises RuntimeError on failure.
        """
        read_buffer = (ctypes.c_ubyte * size)()
        size_transferred = ctypes.c_uint32()
        native_handle = ctypes.c_void_p(handle.value)
        native_address = ctypes.c_uint8(device_address & 0x7F)
        native_size = ctypes.c_uint32(size)
        native_options = ctypes.c_uint32(options)

        status = self.I2C_DeviceRead(native_handle,
                                     native_address,
                                     native_size,
                                     read_buffer,
                                     ctypes.byref(size_transferred),
                                     native_options)

        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to read from I2C device. Status: {status}")
        return bytes(read_buffer[:size_transferred.value])

    def write(self, handle: FTHandle, device_address: int, data: bytes, options: int) -> int:
        """
        Write bytes to an addressed I2C slave.
        param handle: Handle to the channel.
        param device_address: 7-bit slave address. Only bits[6:0] are used; the write
                              direction bit is appended by libMPSSE (this is a write).
        param data: Bytes object containing the data to write.
        param options: Bitmask of I2C_TRANSFER_OPTIONS (required; the caller decides):
            START_BIT (0x01)      - generate a START condition before the transfer.
            STOP_BIT (0x02)       - generate a STOP condition after the transfer.
            BREAK_ON_NACK (0x04)  - stop transferring when the slave NACKs.
            NACK_LAST_BYTE (0x08) - read-only flag; not applicable to writes.
            FAST_TRANSFER_BYTES (0x10) / FAST_TRANSFER_BITS (0x20) - fast-transfer
                                    modes; with BITS, the size is counted in bits.
            NO_ADDRESS (0x40)     - skip the address phase.
        return: Number of bytes actually written. Raises RuntimeError on failure.
        """
        size_to_transfer = len(data)
        write_buffer = (ctypes.c_ubyte * size_to_transfer).from_buffer_copy(data)
        size_transferred = ctypes.c_uint32()
        native_handle = ctypes.c_void_p(handle.value)
        native_address = ctypes.c_uint8(device_address & 0x7F)
        native_size = ctypes.c_uint32(size_to_transfer)
        native_options = ctypes.c_uint32(options)

        status = self.I2C_DeviceWrite(native_handle,
                                      native_address,
                                      native_size,
                                      write_buffer,
                                      ctypes.byref(size_transferred),
                                      native_options)

        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to write to I2C device. Status: {status}")
        return size_transferred.value

    def get_device_id(self, handle: FTHandle, device_address: int) -> bytes:
        """
        Retrieve the 3-byte I2C device ID of an addressed slave.
        param handle: Handle to the channel.
        param device_address: 7-bit slave address (only bits[6:0] are used).
        return: 3-byte device ID. Raises RuntimeError on failure (including
                FT_NOT_SUPPORTED when the library lacks device-ID support).
        """
        device_id = (ctypes.c_ubyte * 3)()
        native_handle = ctypes.c_void_p(handle.value)
        native_address = ctypes.c_uint8(device_address & 0x7F)
        status = self.I2C_GetDeviceID(native_handle, native_address, device_id)
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to get I2C device ID. Status: {status}")
        return bytes(device_id)

    def write_gpio(self, handle: FTHandle, direction: int, value: int) -> None:
        """
        Write to the 8 GPIO lines on the high byte (ACBUS/BCBUS) of the MPSSE channel.
        param handle: Handle to the channel.
        param direction: Direction bitmask for the 8 lines (bit = 1 output, bit = 0 input).
        param value: Output level for each line (only bits configured as output take effect).
        return: None. Raises RuntimeError on failure.
        """
        native_handle = ctypes.c_void_p(handle.value)
        native_direction = ctypes.c_uint8(direction & 0xFF)
        native_value = ctypes.c_uint8(value & 0xFF)
        status = self.FT_WriteGPIO(native_handle, native_direction, native_value)
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to write GPIO. Status: {status}")

    def read_gpio(self, handle: FTHandle) -> int:
        """
        Read the 8 GPIO lines on the high byte (ACBUS/BCBUS) of the MPSSE channel.
        param handle: Handle to the channel.
        return: 8-bit integer with the input state of the GPIO lines (bit = 1 high).
                Raises RuntimeError on failure.
        note: The line directions must first be set to input via write_gpio().
        """
        value = ctypes.c_uint8()
        native_handle = ctypes.c_void_p(handle.value)
        status = self.FT_ReadGPIO(native_handle, ctypes.byref(value))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to read GPIO. Status: {status}")
        return value.value

    def get_version(self) -> tuple[int, int]:
        """
        Get the version numbers of the libMPSSE and libFTD2XX libraries.
        return: A tuple ``(libmpsse_version, libftd2xx_version)`` of raw version
                DWORDs (e.g. 0x030109 encodes version 3.1.9). Raises RuntimeError
                on failure.
        """
        libmpsse_version = ctypes.c_uint32()
        libftd2xx_version = ctypes.c_uint32()
        status = self.Ver_libMPSSE(ctypes.byref(libmpsse_version),
                                   ctypes.byref(libftd2xx_version))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to get library version. Status: {status}")
        return (libmpsse_version.value, libftd2xx_version.value)
