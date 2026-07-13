# PyLibmpsse #

## 1. Introduction ##

A sample wrapper for LibMPSSE library.

## 2. Requirements ##

- Windows platform
- Python >= 3.9
- libmpsse.dll
- Install d2xx driver

## 3. Architecture ##

```text
pyLibmpsse/
├── src/
│   └── pyLibmpsse/                # 主包目录（src 布局）
│       ├── __init__.py           # 包初始化，导出 SPIInterface / SPIChannelConfig 等
│       ├── libmpsse_bindings.py  # 绑定层：加载 DLL，声明 C 函数原型，定义结构体
│       ├── consts.py             # 常量层：FT_STATUS、SPI/I2C/GPIO 等枚举与常量
│       ├── spi.py                # SPI 高层封装 + 低层绑定（含 GPIO 高层封装）
│       └── errors.py             # 自定义异常类（PlatformError / DLLLoadError）
├── tests/                        # 测试目录（pytest：集成测试 + 无硬件单元测试）
├── scripts/                      # 辅助脚本（设置 DLL 环境变量并运行测试）
├── doc/                          # FTDI 官方头文件与手册
├── pyproject.toml                # 打包与构建配置（setuptools）
├── requirements.txt
└── README.md
```

## 4. SPI low-level API pointer contract (C-style) ##

The low-level SPI methods are intended to stay close to the original C API.
Rule of thumb:

- If the C prototype says T*, pass a ctypes pointer instance.
- If the C prototype says T (non-pointer), pass a value/handle directly.
- Do not pass Python int/bytes where a pointer is required.

### 4.1 Per-function pointer requirements ###

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

### 4.2 Important calling note ###

For low-level wrappers, keep one pointer layer only:

- If caller already passes a pointer instance, do not wrap it again with ctypes.byref(...).
- Use ctypes.byref(obj) when you own obj in the current scope.
- Use ctypes.pointer(obj) when you need a reusable pointer object.

Passing a NULL pointer (for example ctypes.POINTER(T)()) to output parameters is invalid unless the C API explicitly allows NULL.

### 4.3 Minimal low-level examples ###

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

## 5. Integration tests: DLL path via environment variables ##

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
