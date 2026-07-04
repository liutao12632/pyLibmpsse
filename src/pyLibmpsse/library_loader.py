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

class LibraryLoader:

    def __init__(self, ftd2xx_path=None, libmpsse_path=None):
        self.ftd2xx_dll = None
        self.libmpsse_dll = None
        self.load_ftd2xx_from = None
        self.load_mpsse_from = None
        
    
    def _search_libmpsse_path(self) -> str:
        candidates = []

        # Caller's directory
        try:
            caller = inspect.stack()[2].filename
            if caller not in ('<stdin>', '<input>', '<string>'):
                candidates.append(os.path.join(os.path.dirname(os.path.abspath(caller)), "libmpsse.dll"))
        except Exception:
            pass

        # Current working directory
        candidates.append(os.path.join(os.getcwd(), "libmpsse.dll"))

        # System PATH directories
        candidates.append("libmpsse.dll")

        for path in candidates:
            if os.path.exists(path) or path == "libmpsse.dll":
                return path

        raise DLLLoadError(
            "libmpsse.dll not found. Please provide the full path, "
            "or place it alongside your script or in the current working directory."
        )

    def load_dll(self,
                  libmpsse_path: Optional[str] = None,
                  ftd2xx_path: Optional[str] = None) -> None:
        """
           Load ftd2xx.dll and libmpsse.dll into the loader instance.
    
              ftd2xx.dll is loaded first, followed by libmpsse.dll. The loaded
           library objects are stored as ``self.ftd2xx_dll`` and
           ``self.libmpsse_dll`` respectively.
    
              Parameters
           ----------
           libmpsse_path : str | None, optional
               Path to ``libmpsse.dll``. If *None* (default), the loader searches
               in the following order:
    
                  1. The directory of the **calling script** (the file that invoked
                  this method — obtained via ``inspect.stack()``).
               2. The current working directory (``os.getcwd()``).
               3. System-wide search (lets Windows locate the DLL via the standard
                  DLL search order, including ``PATH``).
    
                  The first match is used. Raises :exc:`DLLLoadError` if none of the
               locations contain ``libmpsse.dll``.
    
              ftd2xx_path : str | None, optional
               Path to ``ftd2xx.dll``. If *None* (default), the loader relies on
               Windows' built-in DLL search order (typically finds it in
               ``C:\\Windows\\System32`` or ``C:\\Windows\\SysWOW64``).
    
              Raises
           ------
           PlatformError
               If the operating system is not Windows.
           DLLLoadError
               If either DLL fails to load (file not found, architecture mismatch,
               missing dependencies, etc.). The error message includes whether the
               path was user-provided or auto-searched.
    
              Notes
           -----
           - ``ftd2xx.dll`` is expected to be installed system-wide via the FTDI
             D2XX driver. It is loaded with :func:`ctypes.WinDLL` (``stdcall``
             calling convention).
           - ``libmpsse.dll`` is a third-party library and is NOT bundled with
             this package. The user must obtain it separately and either place it
             alongside their script, in the current working directory, or provide
             an explicit path. It is loaded with :func:`ctypes.CDLL` (``cdecl``
             calling convention).
           - After a successful call, ``self.load_ftd2xx_from`` and
             ``self.load_mpsse_from`` indicate how each DLL path was resolved
             (``"User provided path"`` or ``"Searched path"``).
           """

        # Determine the path to the DLL based on the operating system
        if not sys.platform.startswith('win'):
            raise PlatformError("Unsupported operating system. Must be Windows.")
        
        try:
            if ftd2xx_path is None:
                ftd2xx_path = "ftd2xx.dll"  # Default to system search if not provided
                self.load_ftd2xx_from = "Searched path"
            else:
                self.load_ftd2xx_from = "User provided path"
            self.ftd2xx_dll = ctypes.WinDLL(ftd2xx_path)
        except OSError as e:
            raise DLLLoadError(f"Failed to load ftd2xx.dll: {e}")
        
        try:
            if libmpsse_path is None:
                libmpsse_path = self._search_libmpsse_path()
                self.load_mpsse_from = "Searched path"
            else:
                self.load_mpsse_from = "User provided path"
            self.libmpsse_dll = ctypes.CDLL(libmpsse_path)
        except OSError as e:
            raise DLLLoadError(f"Failed to load libmpsse.dll from {self.load_mpsse_from}: {e}")