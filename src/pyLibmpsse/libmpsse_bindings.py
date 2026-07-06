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

class LibMPSSEBindings:

    def __init__(self, ftd2xx_path=None, libmpsse_path=None):
        self.ftd2xx_dll = None
        self.libmpsse_dll = None
        self.load_ftd2xx_path = None
        self.load_mpsse_path = None
        
    def load_dlls(self,
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
    
