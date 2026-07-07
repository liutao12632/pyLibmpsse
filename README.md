# PyLibmpsse #

## 1. Introduction ##

A sample wrapper for LibMPSSE library.

## 2. Requirements ##

- Windows platform
- Python >= 3.12
- libmpsse.dll
- Install d2xx driver

## 3. Architecture ##

```text
pyLibMPSSE/
├── pyLibMPSSE/                 # 主包目录
│   ├── __init__.py             # 包初始化，导出主要接口（如 I2C, SPI 类）
│   ├── libmpsse_bindings.py    # 绑定层：加载 DLL，声明 C 函数原型，定义结构体
│   ├── constants.py            # 常量层：定义 FT_STATUS、I2C/SPI 配置等枚举和常量
│   ├── i2c.py                  # I2C 功能高层封装
│   ├── spi.py                  # SPI 功能高层封装
│   ├── gpio.py                 # GPIO 功能高层封装
│   └── exceptions.py           # 自定义异常类
├── tests/                      # 单元测试目录
├── examples/                   # 示例脚本目录
├── doc/                        # 开发所用到的手册
├── README.md
└── setup.py                    # 安装脚本
```
