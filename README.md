# PyLibmpsse #

## 1.Introduction ##

A sample wrapper for libmpsse library.

## 2.Requirements ##

- Windows platform
- Python 3.12
- libmpsse.dll
- Install d2xx driver

## 3.Architecture ##

pyLibMPSSE/
├── pyLibMPSSE/                 # 主包目录
│   ├── __init__.py             # 包初始化，导出主要接口（如 I2C, SPI 类）
│   ├── libmpsse_bindings.py    # 绑定层：加载DLL，声明C函数原型，定义结构体
│   ├── constants.py            # 常量层：定义FT_STATUS、I2C/SPI配置等枚举和常量
│   ├── i2c.py                  # I2C功能高层封装
│   ├── spi.py                  # SPI功能高层封装
│   ├── gpio.py                 # GPIO功能高层封装
│   └── exceptions.py           # 自定义异常类
├── tests/                      # 单元测试目录
├── examples/                   # 示例脚本目录
├── doc/                        # 开发所用到的手册#
├── README.md
└── setup.py                    # 安装脚本