
# Requires libudev and libinput installed by distro
# Requires python3-evdev package installed by distro

import ctypes
import os
import traceback
import importlib
from abc import ABC, abstractmethod
from typing import Callable, Any, List
from enum import IntEnum
from evdev import uinput, ecodes
import select


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

libinput.libinput_udev_create_context.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
libinput.libinput_udev_create_context.restype = ctypes.c_void_p

libinput.libinput_udev_assign_seat.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
libinput.libinput_udev_assign_seat.restype = ctypes.c_int

libinput.libinput_unref.argtypes = [ctypes.c_void_p]
libinput.libinput_unref.restype = ctypes.c_void_p

libinput.libinput_dispatch.argtypes = [ctypes.c_void_p]
libinput.libinput_dispatch.restype = ctypes.c_int

libinput.libinput_get_event.argtypes = [ctypes.c_void_p]
libinput.libinput_get_event.restype = ctypes.c_void_p

libinput.libinput_event_get_type.argtypes = [ctypes.c_void_p]
libinput.libinput_event_get_type.restype = ctypes.c_int

libinput.libinput_event_get_pointer_event.argtypes = [ctypes.c_void_p]
libinput.libinput_event_get_pointer_event.restype = ctypes.c_void_p

libinput.libinput_event_pointer_get_button.argtypes = [ctypes.c_void_p]
libinput.libinput_event_pointer_get_button.restype = ctypes.c_uint32

libinput.libinput_event_pointer_get_button_state.argtypes = [ctypes.c_void_p]
libinput.libinput_event_pointer_get_button_state.restype = ctypes.c_int

libinput.libinput_event_pointer_has_axis.argtypes = [ctypes.c_void_p, ctypes.c_int]
libinput.libinput_event_pointer_has_axis.restype = ctypes.c_int

libinput.libinput_event_pointer_get_scroll_value.argtypes = [ctypes.c_void_p, ctypes.c_int]
libinput.libinput_event_pointer_get_scroll_value.restype = ctypes.c_double

libinput.libinput_event_get_keyboard_event.argtypes = [ctypes.c_void_p]
libinput.libinput_event_get_keyboard_event.restype = ctypes.c_void_p

libinput.libinput_event_keyboard_get_key.argtypes = [ctypes.c_void_p]
libinput.libinput_event_keyboard_get_key.restype = ctypes.c_uint32

libinput.libinput_event_keyboard_get_key_state.argtypes = [ctypes.c_void_p]
libinput.libinput_event_keyboard_get_key_state.restype = ctypes.c_int

libinput.libinput_event_destroy.argtypes = [ctypes.c_void_p]
libinput.libinput_event_destroy.restype = None

libinput.libinput_get_fd.argtypes = [ctypes.c_void_p]
libinput.libinput_get_fd.restype = ctypes.c_int

################################################################################



################################################################################
# libudev support
################################################################################

udev = ctypes.CDLL("libudev.so")

udev.udev_new.argtypes = None
udev.udev_new.restype = ctypes.c_void_p

udev.udev_unref.argtypes = [ctypes.c_void_p]
udev.udev_unref.restype = ctypes.c_void_p

################################################################################



################################################################################
# libmacro implementation
################################################################################

class LibMacroScript(ABC):

    def __init__(self):
        self.lm = None

    @abstractmethod
    def handle_key(self, keycode: int, pressed: bool):
        pass

    @abstractmethod
    def handle_mouse_button(self, button: int, pressed: bool):
        pass

    @abstractmethod
    def handle_mouse_scroll(self, vertical: bool, distance: float):
        pass

    @abstractmethod
    def keys_generated(self) -> List[int]:
        pass

    def press_key(self, key):
        self.lm.ui.write(ecodes.EV_KEY, key, 1)
        self.lm.ui.syn()

    def release_key(self, key):
        self.lm.ui.write(ecodes.EV_KEY, key, 0)
        self.lm.ui.syn()
    
    def type_key(self, key):
        self.lm.ui.write(ecodes.EV_KEY, key, 1)
        self.lm.ui.write(ecodes.EV_KEY, key, 0)
        self.lm.ui.syn()

class LibMacro:

    # Scripts must have the following functions
    #   key_handler(keycode: int, pressed: bool)
    #   mouse_button_handler(button: int, pressed: bool)
    #   mouse_scroll_handler(vertical: bool, distance: float)
    #   keys_generated() -> List[int]

    def __init__(self, script: LibMacroScript):
        # Make sure given script file exists and has required attributes
        self.script = script
        self.script.lm = self

    def run(self):
        # Initialize udev and libinput to monitor input events
        self.m_udev = udev.udev_new()
        self.m_libinput_iface  = libinput_interface(CFUNC_OPEN_RESTRICTED(libinput_open_restricted), CFUNC_CLOSE_RESTRICTED(libinput_close_restricted))
        self.m_libinput = libinput.libinput_udev_create_context(ctypes.byref(self.m_libinput_iface), None, self.m_udev)
        rc = libinput.libinput_udev_assign_seat(self.m_libinput, "seat0".encode())
        if rc != 0:
            raise Exception("Failed to initialize libinput and udev. Try running as root.")
        
        # Create uinput object to generate input
        self.ui = uinput.UInput({
            ecodes.EV_KEY: self.script.keys_generated()
        })

        # Event loop
        # Polls file descriptor until events available (POLLIN)
        # Then handles all events
        # Then polls again
        poll = select.poll()
        poll.register(libinput.libinput_get_fd(self.m_libinput), select.POLLIN)    
        try:
            while True:
                revents = poll.poll()
                if len(revents) == 0:
                    # Nothing returned from polling. Just repeat poll.
                    continue

                # Got pollin (only thing polling for), handle all events
                while True:
                    libinput.libinput_dispatch(self.m_libinput)
                    ev = libinput.libinput_get_event(self.m_libinput)
                    if ev is None:
                        break # Back to polling (no more events to handle)

                    evtype = libinput.libinput_event_get_type(ev)
                    if evtype == 402:                   # LIBINPUT_EVENT_POINTER_BUTTON
                        # Mouse buttons
                        pev = libinput.libinput_event_get_pointer_event(ev)
                        button = libinput.libinput_event_pointer_get_button(pev)
                        if libinput.libinput_event_pointer_get_button_state(pev):
                            self.script.handle_mouse_button(button, True)
                        else:
                            self.script.handle_mouse_button(button, False)

                    elif evtype == 404:                 # LIBINPUT_EVENT_POINTER_SCROLL_WHEEL
                        # Scroll wheel (0 = vertical, 1 = horizontal)
                        pev = libinput.libinput_event_get_pointer_event(ev)
                        if libinput.libinput_event_pointer_has_axis(pev, 0):
                            value = libinput.libinput_event_pointer_get_scroll_value(pev, 0)
                            self.script.handle_mouse_scroll(True, value)
                        elif libinput.libinput_event_pointer_has_axis(pev, 1):
                            value = libinput.libinput_event_pointer_get_scroll_value(pev, 1)
                            self.script.handle_mouse_scroll(False, value)

                    elif evtype == 300:                 # LIBINPUT_EVENT_KEYBOARD_KEY
                        # Keyboard keys
                        kev = libinput.libinput_event_get_keyboard_event(ev)
                        button = libinput.libinput_event_keyboard_get_key(kev)
                        if libinput.libinput_event_keyboard_get_key_state(kev):
                            self.script.handle_key(button, True)
                        else:
                            self.script.handle_key(button, False)
                    libinput.libinput_event_destroy(ev)

        except KeyboardInterrupt:
            # Silent exit
            pass
        except:
            traceback.print_exc()

        # Cleanup
        self.ui.close()
        libinput.libinput_unref(self.m_libinput)
        udev.udev_unref(self.m_udev)

################################################################################