#!/usr/bin/env python3

################################################################################
#
# Copyright © 2020-2023 Marcus Behel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################
# 
# Linux Version:
#   Only works on X11 (not wayland)
#   Would need to implement a different global key handler for wayland
# 
# Script to simulate the behavior of Minecraft Java Edition 1.15+
# When ctrl is pressed sprint is enabled until it is pressed again
# This persists across sneaking, opening UIs, etc
#
# Bedrock edition (and Java Edition before 1.15) lack this feature.
# This script provides a way to get this behavior in these versions of the game
# by mapping a different key (by default F9) to sprint in the game. This script
# will then "hold" F9 when you press ctrl, and release it when you press it
# again, thereby simulating the toggle sprint functionality of Java Edition
# 1.15+.
#
################################################################################
#
# Author: Marcus Behel
# Date: May 7, 2023
# Version: 1.0.2
#
################################################################################
# 
# To run without root:
#     Setup uinput group (and udev rule to "apply" it to uinput device)
#     Then, add your user to uinput group
#     sudo groupadd -f uinput
#     sudo adduser username uinput
#     echo "KERNEL==\"uinput\", GROUP=\"uinput\", MODE:=\"0660\"" | sudo tee -a /etc/udev/rules.d/99-input.rules
#
################################################################################
#
# Requires python3 and the following libraries (install with pip)
#     evdev
# Xlib is also required, but should be included by your distribution
# May have to install a python3-xlib package (or something similar)
#
################################################################################

import time

from Xlib import X, protocol
from Xlib.display import Display
from Xlib.ext import record

import evdev
from evdev import uinput, ecodes as e

# X11 stuff (used for global key handler)
display = None
root = None

# Track sprint state
sprint_state = False

# Uinput device (see main)
ui = None

def release_sprint_evdev():
    global ui
    # release F9
    ui.write(e.EV_KEY, e.KEY_F9, 0)
    ui.syn()
    print("Sprint Off")

def press_sprint_evdev():
    global ui
    # Ensure the game has time to register that F9 is released
    # This makes things more reliable on bedrock (fewer times missing that F9 is now held)
    # This is seemingly an issue due to running android code on linux
    # Seem to sometimes be some input latency issues.
    ui.write(e.EV_KEY, e.KEY_F9, 0)
    ui.syn()
    time.sleep(0.01)
    
    # Press F9
    ui.write(e.EV_KEY, e.KEY_F9, 1)
    ui.syn()
    print("Sprint On")

def quick_release_evdev():
    """
    Quickly release then continue holding sprint key (if it is currently held)
    """
    global sprint_state, ui

    if sprint_state:
        pass


def toggle_sprint_evdev():
    """
    Toggle holding the sprint key.

    This method uses evdev's uinput device to inject the input low-level
        This ensures best compatibility with all programs (including bedrock edition)
        Other methods were tested (X11 send_event, Python autopy library, PyUserInput library)
        however, all had one or more issues with bedrock edition.
        This is likely due to bedrock edition being run with the compatibility layer.
    """
    global sprint_state, ui

    # Invert sprint state
    sprint_state = not sprint_state

    if not sprint_state:
        release_sprint_evdev()
    else:
        press_sprint_evdev()


# This method of detecting key press will only work on X11 (not wayland)
def handler(reply):
    """
    Handles all key presses. Only responds to some
    """
    data = reply.data
    while len(data):
        event, data = protocol.rq.EventField(None).parse_binary_value(data, display.display, None, None)
        keycode = event.detail
        press = event.type == X.KeyPress

        # LControl (37) or RControl (105) pressed
        if press and (keycode == 37 or keycode == 105):
            toggle_sprint_evdev()
            
        # Release enter key (close chat GUI)
        if not press and keycode == 104:
            time.sleep(0.100)
            quick_release_evdev()
        
        # Release escape key (close any GUI)
        if not press and keycode == 9:
            time.sleep(0.100)
            quick_release_evdev()
        
        # Release E key (close inventory)
        if not press and keycode == 26:
            time.sleep(0.100)
            quick_release_evdev()
        
        # Release Z key (potion effects UI)
        if not press and keycode == 52:
            time.sleep(0.100)
            quick_release_evdev()

        # Release shift key (stop sneaking)
        if not press and (keycode == 50 or keycode == 62):
            time.sleep(0.050)
            quick_release_evdev()
        
def main():
    global display, root, ui

    ui = uinput.UInput()

    display = Display()
    root = display.screen().root

    ctx = display.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyReleaseMask, X.ButtonReleaseMask),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }]
    )

    print("Started.")

    try:
        # Blocks until a call to record_disable_context
        display.record_enable_context(ctx, handler)
    except:
        # Free after disabled
        display.record_free_context(ctx)

        # Program is shutting down. Close uinput device
        ui.close()



if __name__ == '__main__':
    main()
