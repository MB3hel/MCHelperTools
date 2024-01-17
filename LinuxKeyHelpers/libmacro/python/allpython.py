
import ctypes
import os
from typing import Callable, Any
from enum import IntEnum

################################################################################
# libinput support
################################################################################

CFUNC_OPEN_RESTRICTED = ctypes.CFUNCTYPE( ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
CFUNC_CLOSE_RESTRICTED = ctypes.CFUNCTYPE(None,  ctypes.c_int,  ctypes.c_void_p)

class libinput_interface(ctypes.Structure):
    _fields_ = [
        ("open_restricted", CFUNC_OPEN_RESTRICTED),
        ("close_restricted",  CFUNC_CLOSE_RESTRICTED)
    ]

def libinput_open_restricted(path, flags, user_data):
    return os.open(path, flags)

def libinput_close_restricted(fd, user_data):
    os.close(fd)

libinput = ctypes.CDLL("libinput.so")

################################################################################

################################################################################
# libudev support
################################################################################

udev = ctypes.CDLL("libudev.so")
udev.udev_new.argtypes = None
udev.udev_new.restype = ctypes.c_void_p

################################################################################


################################################################################
# libmacro implementation
################################################################################

class EventType(IntEnum):
    KEYPRESS = 0
    KEYRELEASE = 1
    MOUSEPRESS = 2
    MOUSERELEASE = 3
    MOUSESCROLL_VERTICAL = 4
    MOUSESCROLL_HORIZONTAL = 5

def libmacro_run(callback: Callable[[EventType, int], Any]):
    # Initialize udev and libinput to monitor input events
    m_udev = udev.udev_new()
    libinput_context  = libinput_interface(CFUNC_OPEN_RESTRICTED(libinput_open_restricted), CFUNC_CLOSE_RESTRICTED(libinput_close_restricted))
    

################################################################################