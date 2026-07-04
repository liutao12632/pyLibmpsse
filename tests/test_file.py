import pytest
import pyLibmpsse


def test_dll_loader():
    loader = pyLibmpsse.LibraryLoader()
    assert loader is not None