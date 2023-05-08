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
# Works on X11 and Wayland (using libinput and evdev)
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
# Version: 1.1.0
#
################################################################################

import libinput
import libinput.evcodes as lie
import sys
import time
import threading
from evdev import uinput, ecodes as e
from queue import Queue

# Libinput to get keyboard events
li = libinput.LibInput(udev=True)
li.udev_assign_seat('seat0')

# Uinput device to inject keyboard events
ui = uinput.UInput()

# Queue libinput events and handle on different thread
# Prevents uinput injection from stalling libinput itself
evqueue = Queue()


# Track sprint key state
sprint_state = False


def toggle_sprint():
    """
    Toggle holding sprint key
    """
    global sprint_state, ui

    # Invert sprint state
    sprint_state = not sprint_state

    # Apply state
    if not sprint_state:
        # Release F9
        ui.write(e.EV_KEY, e.KEY_F9, 0)
        ui.syn()
        # print("RELEASE", flush=True)
    else:
        # Release F9
        # Ensures subsequent press is properly detected
        # Not an issue with java edition, but necessary for bedrock
        # using MCPELauncher
        ui.write(e.EV_KEY, e.KEY_F9, 0)
        ui.syn()
        time.sleep(0.01)
        
        # Press F9
        ui.write(e.EV_KEY, e.KEY_F9, 1)
        ui.syn()

        # print("PRESS", flush=True)


def quick_release():
    """
    Quickly release then continue holding the sprint key (assuming it was held to begin with)
    """
    global ui, sprint_state
    if sprint_state:
        # Release F9
        ui.write(e.EV_KEY, e.KEY_F9, 0)
        ui.syn()

        time.sleep(0.05)

        # Press F9
        ui.write(e.EV_KEY, e.KEY_F9, 1)
        ui.syn()

        # print("QUICK_RELEASE", flush=True)


def handle_event(kcode, kstate):
    if kstate == libinput.constant.KeyState.PRESSED:
        # LControl or RControl pressed toggle the sprint key state
        if kcode == lie.Key.KEY_LEFTCTRL or kcode == lie.Key.KEY_RIGHTCTRL:
            toggle_sprint()
    elif kstate == libinput.constant.KeyState.RELEASED:
        # There are several situations where bedrock edition does not continue
        # to detect the held key. Usually, these are when leaving a GUI (chat, block 
        # GUI, etc). To have the game re-detect the key it is necessary to briefly
        # release and then continue holding the sprint key (F9).
        #
        # Enter released could be exiting chat
        # Esc can be used to exit GUI
        # E can be used to exit block GUI
        # Z can be used to close potion effects GUI
        #
        # There is another (more subtle issue) related to sneaking. After releasing 
        # shift to stop sneak sprint sometimes "glitches" when you next start moving.
        # By this I mean you start to sprint, stop, then start again really quickly.
        # This seems to be fixed by quickly toggling the sprint key (like when leaving a
        # UI) when releasing shift.
        if kcode == lie.Key.KEY_ENTER or kcode == lie.Key.KEY_ESC or kcode == lie.Key.KEY_E or kcode == lie.Key.KEY_Z:
            time.sleep(0.100)       # Wait for UI to close
            quick_release()
        elif kcode == lie.Key.KEY_LEFTSHIFT or kcode == lie.Key.KEY_RIGHTSHIFT:
            time.sleep(0.050)       # Wait for sneak to fully stop
            quick_release()


def event_task():
    global evqueue
    try:
        while True:
            kcode, kstate = evqueue.get()
            handle_event(kcode, kstate)
    except KeyboardInterrupt:
        sys.exit(0)

def main():
    global li, evqueue
    try:
        while True:
            try:
                for event in li.get_event():
                    if event.type == libinput.constant.Event.KEYBOARD_KEY:
                        kbev = event.get_keyboard_event()
                        kcode = kbev.get_key()
                        kstate = kbev.get_key_state()
                        evqueue.put((kcode, kstate))
            except ValueError:
                # Unknown / unhandled event
                # Scroll wheel seems to cause this
                pass
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    event_thread = threading.Thread(target=event_task, daemon=True)
    event_thread.start()
    main()
