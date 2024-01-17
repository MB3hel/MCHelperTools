
# Requires libudev and libinput installed by distro
# Requires python3-evdev package installed by distro

import ctypes
import os
import traceback
from typing import Callable, Any
from enum import IntEnum
from evdev import uinput, ecodes

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

ui = None

class EventType(IntEnum):
    KeyPress = 0                    # Value is keycode
    KeyRelease = 1                  # Value is keycode
    MousePress = 2                  # Value is keycode
    MouseRelease = 3                # Value is keycode
    MouseScrollVertical = 4         # Value is degrees (positive is down, negative is up)
    MouseScrollHorizontal = 5       # Value is degrees (positive is down, negative is up)

def libmacro_run(callback: Callable[[EventType, Any], Any]):
    global ui


    # Initialize udev and libinput to monitor input events
    m_udev = udev.udev_new()
    libinput_iface  = libinput_interface(CFUNC_OPEN_RESTRICTED(libinput_open_restricted), CFUNC_CLOSE_RESTRICTED(libinput_close_restricted))
    m_libinput = libinput.libinput_udev_create_context(ctypes.byref(libinput_iface), None, m_udev)
    rc = libinput.libinput_udev_assign_seat(m_libinput, "seat0".encode())
    if rc != 0:
        print("ERROR: Unable to initialize udev & libinput!")
        return
    
    # Uinput device to inject keyboard events
    ui = uinput.UInput(name="libmacro-uinput")

    # Event loop
    try:
        while True:
            libinput.libinput_dispatch(m_libinput)
            ev = libinput.libinput_get_event(m_libinput)
            if ev is None:
                continue
            evtype = libinput.libinput_event_get_type(ev)
            if evtype == 402:                   # LIBINPUT_EVENT_POINTER_BUTTON
                # Mouse buttons
                pev = libinput.libinput_event_get_pointer_event(ev)
                button = libinput.libinput_event_pointer_get_button(pev)
                if libinput.libinput_event_pointer_get_button_state(pev):
                    # Button pressed
                    callback(EventType.MousePress, button)
                else:
                    # Button released
                    callback(EventType.MouseRelease, button)
            elif evtype == 404:                 # LIBINPUT_EVENT_POINTER_SCROLL_WHEEL
                pev = libinput.libinput_event_get_pointer_event(ev)
                if libinput.libinput_event_pointer_has_axis(pev, 0):
                    # Vertical scroll wheel
                    value = libinput.libinput_event_pointer_get_scroll_value(pev, 0)
                    callback(EventType.MouseScrollVertical, value)
                elif libinput.libinput_event_pointer_has_axis(pev, 1):
                    # Horizontal scroll wheel
                    value = libinput.libinput_event_pointer_get_scroll_value(pev, 1)
                    callback(EventType.MouseScrollHorizontal, value)
            elif evtype == 300:                 # LIBINPUT_EVENT_KEYBOARD_KEY
                # Keyboard keys
                kev = libinput.libinput_event_get_keyboard_event(ev)
                button = libinput.libinput_event_keyboard_get_key(kev)
                if libinput.libinput_event_keyboard_get_key_state(kev):
                    # Button pressed
                    callback(EventType.KeyPress, button)
                else:
                    # Button released
                    callback(EventType.KeyRelease, button)
            libinput.libinput_event_destroy(ev)

    except KeyboardInterrupt:
        # Silent exit
        pass
    except:
        traceback.print_exc()

    # Cleanup
    libinput.libinput_unref(m_libinput)
    udev.udev_unref(m_udev)


def libmacro_press_key(keycode):
    if ui is None:
        print("Run libmacro first!!!")
        return
    ui.write(ecodes.EV_KEY, keycode, 1)
    ui.syn()

def libmacro_release_key(keycode):
    if ui is None:
        print("Run libmacro first!!!")
        return
    ui.write(ecodes.EV_KEY, keycode, 1)
    ui.syn()

################################################################################