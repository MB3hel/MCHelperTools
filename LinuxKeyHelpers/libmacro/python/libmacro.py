
from enum import IntEnum
import ctypes
import os
import traceback
from typing import Callable, Any


class EventType(IntEnum):
    KEYPRESS = 0
    KEYRELEASE = 1
    MOUSEPRESS = 2
    MOUSERELEASE = 3
    MOUSESCROLL_VERTICAL = 4
    MOUSESCROLL_HORIZONTAL = 5


class Event(ctypes.Structure):
    _fields_ = [
        ('event_type', ctypes.c_int),
        ('event_value', ctypes.c_int)
    ]


def libmacro_run(callback: Callable[[EventType, int], Any]):
    # Setup interface to libmacro c library
    lib_name = "libmacro.so"
    lib_path = os.path.dirname(__file__)
    libmacro = ctypes.CDLL(os.path.join(lib_path, lib_name))
    libmacro.libmacro_init.argtypes = None
    libmacro.libmacro_init.restype = ctypes.c_void_p
    libmacro.libmacro_deinit.argtypes = [ctypes.c_void_p]
    libmacro.libmacro_deinit.restype = None
    libmacro.libmacro_wait_for_event.argtypes = [ctypes.c_void_p]
    libmacro.libmacro_wait_for_event.restype = Event

    # Setup
    context = libmacro.libmacro_init()
    if not context:
        print("ERROR: Unable to initialize libmacro!")
        return

    if not callback or not callable(callback):
        print("ERROR: Invalid callback provided!")
        return

    # Event loop
    try:
        while True:
            event = libmacro.libmacro_wait_for_event(context)
            callback(EventType(event.event_type), event.event_value)
    except KeyboardInterrupt:
        # Silent exit. User triggered.
        pass
    except:
        traceback.print_exc()

    libmacro.libmacro_deinit(context)