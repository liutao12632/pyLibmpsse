
import ctypes
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from pyLibmpsse.consts import FT_STATUS, SPI_TRANSFER_OPTIONS
from pyLibmpsse.common import FTHandle, ChannelInfo
from pyLibmpsse.libmpsse_bindings import NativeFT_DEVICE_LIST_INFO_NODE, NativeChannelConfig


def _reject_bit_mode(transfer_options: int) -> None:
    """Guard for the byte-oriented helpers, which cannot honor bit-sized transfers.

    Raises ValueError if ``SPI_TRANSFER_OPTIONS_SIZE_IN_BITS`` is set, since the
    high-level ``read`` / ``write`` / ``read_write`` helpers size their buffers in
    whole bytes. Use the low-level ``SPI_Read`` / ``SPI_Write`` / ``SPI_ReadWrite``
    for bit-granular transfers.
    """
    if transfer_options & SPI_TRANSFER_OPTIONS.SPI_TRANSFER_OPTIONS_SIZE_IN_BITS:
        raise ValueError(
            "Byte-oriented helper does not support SPI_TRANSFER_OPTIONS_SIZE_IN_BITS; "
            "use the low-level SPI_Read / SPI_Write / SPI_ReadWrite for bit transfers."
        )


@dataclass(frozen=True)
class SPIChannelConfig:
    clock_rate: int
    latency_timer: int
    config_options: int
    pin: int
    reserved: int = 0  # Reserved field for alignment, default to 0

class SPIInterface:
    """SPI access for libMPSSE, exposed as two tiers of methods.

    Low-level bindings (``SPI_*`` / ``FT_*``)
        Thin, 1:1 wrappers around the C functions in libMPSSE. They mirror the C
        signatures and return the raw ``FT_STATUS`` code. The caller is
        responsible for ctypes pointer/buffer handling and memory management.
        Intended for internal use or advanced callers who need direct access to
        the underlying C API.

    Pythonic helpers (``get_num_channels``, ``read``, ``write`` ...)
        High-level methods built on top of the low-level bindings. They perform
        the pointer/buffer marshalling, accept and return native Python types
        (``bytes``, ``int``), and raise ``RuntimeError`` on failure instead of
        returning a status code. These are the recommended entry points.
    """

    def __init__(self, bindings):
        self.bindings = bindings

    # ==================================================================
    # Low-level bindings: direct 1:1 wrappers of the libMPSSE C functions.
    # The caller manages ctypes pointers/buffers; each method returns the
    # raw FT_STATUS code. Prefer the Pythonic helpers below unless you need
    # direct access to the C API.
    # ==================================================================
    def SPI_GetNumChannels(self, numChannels) -> int:
        """
        Get the number of available SPI channels.
        param numChannels: Pointer to a DWORD that will receive the number of channels.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_GetNumChannels(numChannels)
        return status

    def SPI_GetChannelInfo(self, index, chanInfo) -> int:
        """
        Get information about a specific SPI channel.
        param index: Index of the channel to query.
        param chanInfo: Pointer to an FT_DEVICE_LIST_INFO_NODE structure that will receive the channel information.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_GetChannelInfo(index, chanInfo)
        return status
    
    def SPI_OpenChannel(self, index, handle) -> int:
        """
        Open a specific SPI channel.
        param index: Index of the channel to open.
        param handle: Pointer to an FT_HANDLE that will receive the handle to the opened channel.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_OpenChannel(index, handle)
        return status
    
    def SPI_InitChannel(self, handle, config) -> int:
        """
        Initialize a specific SPI channel.
        param handle: Handle to the channel to initialize.
        param config: Pointer to a ChannelConfig structure that contains the channel configuration.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_InitChannel(handle, config)
        return status

    def SPI_CloseChannel(self, handle) -> int:
        """ 
        Close a specific SPI channel.
        param handle: Handle to the channel to close.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_CloseChannel(handle)
        return status
    
    def SPI_Read(self, handle, buffer, sizeToTransfer, sizeTransferred, transferOptions) -> int:
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
    
    def SPI_Write(self, handle, buffer, sizeToTransfer, sizeTransferred, transferOptions) -> int:
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
    
    def SPI_ReadWrite(self, handle, inBuffer, outBuffer, sizeToTransfer, sizeTransferred, transferOptions) -> int:
        """
        Read and write data to/from a specific SPI channel.
        param handle: Handle to the channel to read from and write to.
        param inBuffer: Pointer to a buffer that will receive the read (clocked-in) data.
        param outBuffer: Pointer to a buffer that contains the data to write (clocked out).
        param sizeToTransfer: Number of bytes to transfer.
        param sizeTransferred: Pointer to a variable that will receive the number of bytes actually transferred.
        param transferOptions: Options for the transfer.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_ReadWrite(handle, inBuffer, outBuffer, sizeToTransfer, sizeTransferred, transferOptions)
        return status
    
    def SPI_IsBusy(self, handle, state) -> int:
        """
        Read the logic state of the SPI MISO line without clocking the bus.
        param handle: Handle to the channel to check.
        param state: Pointer to a DWORD that will receive the MISO line state (non-zero = high).
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_IsBusy(handle, state)
        return status

    def SPI_ChangeCS(self, handle, configOptions) -> int:
        """
        Change the chip select configuration for a specific SPI channel.
        param handle: Handle to the channel to change.
        param configOptions: Options for the chip select configuration.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_ChangeCS(handle, configOptions)
        return status
    
    def SPI_ToggleCS(self, handle, state) -> int:
        """
        Toggle the chip select line for a specific SPI channel.
        param handle: Handle to the channel to toggle.
        param state: True to assert (select) the CS line, False to de-assert (deselect) it.
                     The electrical level depends on the CS active-high/low configuration.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.SPI_ToggleCS(handle, state)
        return status
    
    def FT_WriteGPIO(self, handle, dir, value) -> int:
        """
        Write to the GPIO pins of a specific SPI channel.
        param handle: Handle to the channel to write to.
        param dir: Direction of the GPIO pins (1 for output, 0 for input).
        param value: Value to write to the GPIO pins.
        return: FT_STATUS indicating success or failure.
        """
        status = self.bindings.libmpsse_dll.FT_WriteGPIO(handle, dir, value)
        return status
    
    def FT_ReadGPIO(self, handle, value) -> int:
        """
        Read the value of the GPIO pins of a specific SPI channel.
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
    # return native Python types, and raise RuntimeError on failure
    # instead of returning a status code.
    # ==================================================================
    def get_num_channels(self) -> int:
        """
        Get the number of available SPI channels.
        return: Number of available SPI channels."""
        num_channels = ctypes.c_uint32()
        status = self.SPI_GetNumChannels(ctypes.byref(num_channels))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to get number of channels. Status: {status}")
        return num_channels.value
    
    def get_channel_info(self, index) -> ChannelInfo:
        """
        Get information about a specific SPI channel.
        param index: Index of the channel to retrieve information for.
        return: ChannelInfo object containing the channel information.
        """
        chan_info = NativeFT_DEVICE_LIST_INFO_NODE()
        status = self.SPI_GetChannelInfo(index, ctypes.byref(chan_info))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to get channel info. Status: {status}")
        info_wrapper = ChannelInfo(
            flags=chan_info.Flags,
            type=chan_info.Type,
            id=chan_info.ID,
            loc_id=chan_info.LocId,
            serial_number=chan_info.SerialNumber.decode('utf-8', errors='replace').rstrip('\x00'),
            description=chan_info.Description.decode('utf-8', errors='replace').rstrip('\x00'),
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

    @contextmanager
    def open_initialized(self, index: int, config: SPIChannelConfig) -> Iterator[FTHandle]:
        """
        Open and initialize an SPI channel as a context manager (recommended).

        Opens the channel at ``index``, initializes it with ``config``, and yields
        the resulting handle. The channel is always closed when leaving the
        ``with`` block, even if an exception is raised inside it, so the handle
        can never leak.

        This is a convenience wrapper over ``open_channel`` / ``init_channel`` /
        ``close_channel``; those methods remain fully usable for manual lifecycle
        management when a single ``with`` block is not a good fit.

        param index: Index of the channel to open.
        param config: Configuration applied via init_channel.
        return: Context manager yielding the opened, initialized FTHandle.
                Raises RuntimeError if opening or initialization fails.

        Example:
            with spi.open_initialized(0, config) as handle:
                spi.read_write(handle, data)
        """
        handle = self.open_channel(index)
        try:
            self.init_channel(handle, config)
            yield handle
        finally:
            self.close_channel(handle)

    def read(self, handle: FTHandle, size: int, transfer_options: int = 0) -> bytes:
        """
        Read data from a specific SPI channel.
        param handle: Handle to the channel to read from.
        param size: Number of bytes to read.
        param transfer_options: Options for the SPI transfer.
        return: Bytes object containing the read data. Raises RuntimeError on failure.
        """
        _reject_bit_mode(transfer_options)
        read_data_buffer = (ctypes.c_ubyte * size)()    #Initial value is set to default 0.#
        size_transferred = ctypes.c_uint32()
        native_handle = ctypes.c_void_p(handle.value)
        native_size = ctypes.c_uint32(size)
        native_transfer_options = ctypes.c_uint32(transfer_options)

        status = self.SPI_Read(native_handle,
                                read_data_buffer,
                                native_size,
                                ctypes.byref(size_transferred),
                                native_transfer_options)
        
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to read from channel. Status: {status}")
        return bytes(read_data_buffer[:size_transferred.value])

    def write(self, handle: FTHandle, data: bytes, transfer_options: int = 0) -> int:
        """
        Write data to a specific SPI channel.
        param handle: Handle to the channel to write to.
        param data: Bytes object containing the data to write.
        param transfer_options: Options for the SPI transfer.
        return: Number of bytes actually written. Raises RuntimeError on failure.
        """
        _reject_bit_mode(transfer_options)
        size_to_transfer = len(data)
        write_data_buffer = (ctypes.c_ubyte * size_to_transfer).from_buffer_copy(data)
        size_transferred = ctypes.c_uint32()
        native_handle = ctypes.c_void_p(handle.value)
        native_size = ctypes.c_uint32(size_to_transfer)
        native_transfer_options = ctypes.c_uint32(transfer_options)

        status = self.SPI_Write(native_handle,
                                 write_data_buffer,
                                 native_size,
                                 ctypes.byref(size_transferred),
                                 native_transfer_options)

        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to write to channel. Status: {status}")
        return size_transferred.value
    
    def read_write(self, handle: FTHandle, write_data: bytes, transfer_options: int = 0) -> bytes:
        """
        Write data to a specific SPI channel and read data back in a single operation.
        param handle: Handle to the channel to write to and read from.
        param write_data: Bytes object containing the data to write.
        param transfer_options: Options for the SPI transfer (byte-mode only).
        return: Bytes object containing the read data. Raises RuntimeError on failure.
        """
        _reject_bit_mode(transfer_options)
        size_to_transfer = len(write_data)
        write_data_buffer = (ctypes.c_ubyte * size_to_transfer).from_buffer_copy(write_data)
        read_data_buffer = (ctypes.c_ubyte * size_to_transfer)()
        size_transferred = ctypes.c_uint32()    
        native_handle = ctypes.c_void_p(handle.value)
        native_size = ctypes.c_uint32(size_to_transfer)
        native_transfer_options = ctypes.c_uint32(transfer_options)

        status = self.SPI_ReadWrite(native_handle,
                                    read_data_buffer,
                                    write_data_buffer,
                                    native_size,
                                    ctypes.byref(size_transferred),
                                    native_transfer_options)
        
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to write/read from channel. Status: {status}")        
        
        return bytes(read_data_buffer[:size_transferred.value])

    def is_busy(self, handle: FTHandle) -> bool:
        """
        Read the SPI MISO line state without clocking the bus.
        param handle: Handle to the channel to check.
        return: True if the MISO line is high, False if low. Whether "high" means
                the slave is busy is device-specific. Raises RuntimeError on failure.
        """
        state = ctypes.c_uint32()
        native_handle = ctypes.c_void_p(handle.value)
        status = self.SPI_IsBusy(native_handle, ctypes.byref(state))
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to check if channel is busy. Status: {status}")
        return bool(state.value)
    
    def change_cs(self, handle: FTHandle, config_options: int) -> None:
        """
        Change the chip select configuration for a specific SPI channel.
        param handle: Handle to the channel to change.
        param config_options: Options for the chip select configuration.
        return: None. Raises RuntimeError on failure.
        """
        native_handle = ctypes.c_void_p(handle.value)
        native_config_options = ctypes.c_uint32(config_options)
        status = self.SPI_ChangeCS(native_handle, native_config_options)
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to change chip select configuration. Status: {status}")

    def toggle_cs(self, handle: FTHandle, state: bool) -> None:
        """
        Assert or de-assert the chip select line for a specific SPI channel.
        param handle: Handle to the channel to toggle.
        param state: True to assert (select) the CS line, False to de-assert (deselect) it.
                     The electrical level depends on the CS active-high/low configuration.
        return: None. Raises RuntimeError on failure.
        """
        native_handle = ctypes.c_void_p(handle.value)
        native_state = ctypes.c_uint32(1 if state else 0)
        status = self.SPI_ToggleCS(native_handle, native_state)
        if status != FT_STATUS.FT_OK.value:
            raise RuntimeError(f"Failed to toggle chip select. Status: {status}")

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
