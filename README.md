# PyLibmpsse #

## 1. Introduction ##

pyLibmpsse is a Python wrapper for FTDI's LibMPSSE library. It provides SPI and
I2C access (plus high-byte GPIO) for FTDI MPSSE-capable devices such as the
FT232H, FT2232H and FT4232H.

The library exposes two tiers of API:

- **Pythonic helpers (recommended)** — methods such as `read` / `write` /
  `read_write` / `open_initialized` that accept and return native Python types
  (`bytes`, `int`) and raise `RuntimeError` on failure.
- **Low-level bindings** — thin, 1:1 wrappers over the C functions that mirror
  the original signatures and return the raw `FT_STATUS` code, for advanced or
  direct use.

> **Windows only.** pyLibmpsse targets the FTDI D2XX stack on Windows and uses
> `ctypes.WinDLL` / `ctypes.CDLL` to load the native DLLs. Constructing
> `LibMPSSELoader` on a non-Windows platform raises `PlatformError`. Linux and
> macOS are not supported.

## 2. Requirements ##

- **Windows only** (see the note above)
- Python >= 3.9
- `libmpsse.dll` and `ftd2xx.dll` — obtained from FTDI; **not** bundled with this package
- FTDI D2XX driver installed

## 3. Installation ##

pyLibmpsse has **no third-party runtime dependencies** (it uses only the Python
standard-library `ctypes`). Install it from a source checkout with pip:

```powershell
# regular install
pip install .

# or an editable/development install
pip install -e .
```

The native `libmpsse.dll` and `ftd2xx.dll` are not shipped with the package.
Download them from FTDI, install the D2XX driver, and pass the DLL paths to
`LibMPSSELoader` (see the Quick start below).

To run the test suite you also need pytest:

```powershell
pip install pytest
```

## 4. Quick start ##

### 4.1 SPI ###

```python
from pyLibmpsse.libmpsse_bindings import LibMPSSELoader
from pyLibmpsse.spi import SPIInterface, SPIChannelConfig

# Load the native DLLs (Windows only).
bindings = LibMPSSELoader(
    libmpsse_path=r"C:\path\to\libmpsse.dll",
    ftd2xx_path="ftd2xx.dll",   # name on PATH, or an absolute path
)

spi = SPIInterface(bindings)
print("SPI channels:", spi.get_num_channels())

config = SPIChannelConfig(
    clock_rate=1_000_000,   # 1 MHz
    latency_timer=1,        # ms
    config_options=0,       # MODE0, CS on DBUS3, active-high
    pin=0x8B8B8B8B,         # initial/final pin direction & value
)

# Recommended: the context manager opens, initializes and always closes the channel.
with spi.open_initialized(0, config) as handle:
    rx = spi.read_write(handle, bytes([0x9F, 0x00, 0x00, 0x00]))
    print("SPI read:", rx.hex())
```

### 4.2 I2C ###

```python
from pyLibmpsse.libmpsse_bindings import LibMPSSELoader
from pyLibmpsse.i2c import I2CInterface, I2CChannelConfig
from pyLibmpsse.consts import I2C_CLOCK_RATE, I2C_TRANSFER_OPTIONS

bindings = LibMPSSELoader(
    libmpsse_path=r"C:\path\to\libmpsse.dll",
    ftd2xx_path="ftd2xx.dll",
)

i2c = I2CInterface(bindings)

config = I2CChannelConfig(
    clock_rate=I2C_CLOCK_RATE.I2C_CLOCK_FAST_MODE,  # 400 kHz
    latency_timer=1,
    options=0,
    pin=0,
)

start_stop = (
    I2C_TRANSFER_OPTIONS.I2C_TRANSFER_OPTIONS_START_BIT
    | I2C_TRANSFER_OPTIONS.I2C_TRANSFER_OPTIONS_STOP_BIT
)

device_addr = 0x50  # 7-bit slave address
with i2c.open_initialized(0, config) as handle:
    i2c.write(handle, device_addr, bytes([0x00]), options=start_stop)
    data = i2c.read(handle, device_addr, 4, options=start_stop)
    print("I2C read:", data.hex())
```

## 5. Architecture ##

```text
pyLibmpsse/
├── src/
│   └── pyLibmpsse/                # package
│       ├── __init__.py           # initialize package, export SPIInterface / I2CInterface ...
│       ├── libmpsse_bindings.py  # binding level: load DLL, declare C prototype function and struct.
│       ├── consts.py             # const level: FT_STATUS、SPI/I2C/GPIO, eumn and other consts.
│       ├── common.py             # Share structure (FTHandle / ChannelInfo)
│       ├── spi.py                # SPI high level API + low level API (including GPIO function)
│       ├── i2c.py                # I2C high level API + low level API (including GPIO function)
│       └── errors.py             # Self defined exception（PlatformError / DLLLoadError）
├── tests/                        # test directory
├── scripts/                      # assistant script
├── doc/                          # FTDI offical header file and doc
├── pyproject.toml                # setuptools
├── LICENSE
└── README.md
```

## 6. SPI low-level API pointer contract (C-style) ##

The low-level SPI methods are intended to stay close to the original C API.
Rule of thumb:

- If the C prototype says T*, pass a ctypes pointer instance.
- If the C prototype says T (non-pointer), pass a value/handle directly.
- Do not pass Python int/bytes where a pointer is required.

### 6.1 Per-function pointer requirements ###

| Function | Parameter | C-side shape | Must be a pointer instance | Suggested ctypes value |
|---|---|---|---|---|
| SPI_GetNumChannels | numChannels | uint32* | Yes | ctypes.byref(ctypes.c_uint32()) |
| SPI_GetChannelInfo | chanInfo | FT_DEVICE_LIST_INFO_NODE* | Yes | ctypes.byref(FT_DEVICE_LIST_INFO_NODE()) |
| SPI_OpenChannel | handle | FT_HANDLE* | Yes | ctypes.byref(ctypes.c_void_p()) |
| SPI_InitChannel | handle | FT_HANDLE | No | ctypes.c_void_p(...) or returned handle |
| SPI_InitChannel | config | ChannelConfig* | Yes | ctypes.byref(ChannelConfig(...)) |
| SPI_CloseChannel | handle | FT_HANDLE | No | ctypes.c_void_p(...) or returned handle |
| SPI_Read | buffer | uint8* | Yes | (ctypes.c_uint8 * n)() |
| SPI_Read | sizeTransferred | uint32* | Yes | ctypes.byref(ctypes.c_uint32()) |
| SPI_Write | buffer | uint8* | Yes | (ctypes.c_uint8 * n).from_buffer_copy(data) |
| SPI_Write | sizeTransferred | uint32* | Yes | ctypes.byref(ctypes.c_uint32()) |
| SPI_ReadWrite | inBuffer | uint8* | Yes | (ctypes.c_uint8 * n)() |
| SPI_ReadWrite | outBuffer | uint8* | Yes | (ctypes.c_uint8 * n)() |
| SPI_ReadWrite | sizeTransferred | uint32* | Yes | ctypes.byref(ctypes.c_uint32()) |
| SPI_IsBusy | state | bool* | Yes | ctypes.byref(ctypes.c_bool()) |
| SPI_ChangeCS | handle | FT_HANDLE | No | ctypes.c_void_p(...) or returned handle |
| SPI_ChangeCS | configOptions | uint32 | No | int or ctypes.c_uint32 |

### 6.2 Important calling note ###

For low-level wrappers, keep one pointer layer only:

- If caller already passes a pointer instance, do not wrap it again with ctypes.byref(...).
- Use ctypes.byref(obj) when you own obj in the current scope.
- Use ctypes.pointer(obj) when you need a reusable pointer object.

Passing a NULL pointer (for example ctypes.POINTER(T)()) to output parameters is invalid unless the C API explicitly allows NULL.

### 6.3 Minimal low-level examples ###

```python
# SPI_GetNumChannels
num_channels = ctypes.c_uint32()
status = spi.SPI_GetNumChannels(ctypes.byref(num_channels))

# SPI_GetChannelInfo
info = FT_DEVICE_LIST_INFO_NODE()
status = spi.SPI_GetChannelInfo(0, ctypes.byref(info))

# SPI_IsBusy
busy = ctypes.c_bool(False)
status = spi.SPI_IsBusy(handle, ctypes.byref(busy))
```

## 7. Integration tests: DLL path via environment variables ##

The integration tests under tests/ no longer hardcode local DLL paths.
They read:

- PYLIBMPSSE_FTD2XX_DLL
- PYLIBMPSSE_LIBMPSSE_DLL

Run tests with the helper script:

```powershell
./scripts/run_pytest_with_dll_env.ps1 -LibMpsseDll "D:\\path\\to\\libmpsse.dll"
```

Optional parameters:

- Ftd2xxDll (default: ftd2xx.dll)
- Pytest args passed through after named parameters

Example with custom pytest args:

```powershell
./scripts/run_pytest_with_dll_env.ps1 -LibMpsseDll "D:\\path\\to\\libmpsse.dll" -Ftd2xxDll "D:\\path\\to\\ftd2xx.dll" -m integration -s
```
