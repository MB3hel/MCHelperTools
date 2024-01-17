#!/usr/bin/env python3

################################################################################
#
# Copyright © 2024 Marcus Behel
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
# Workaround for a GNOME bug
# https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/5896
#
# Note that this bug only impacts (some) xwayland apps on wayland sessions
# Some apps are impacted (eg Minecraft), but others (eg vscode) are not
# THIS SCRIPT WILL HAVE UNINTENDED SIDE EFFECTS IN APPS THAT ARE NOT IMPACTED!
#
################################################################################
#
# Author: Marcus Behel
# Date: Jan 14, 2024
# Version: 1.0.0
#
################################################################################

import libinput
import libinput.evcodes as lie
import sys
import traceback
from evdev import uinput, ecodes as e

# Libinput to get mouse wheel events
li = libinput.LibInput(udev=True)
li.udev_assign_seat('seat0')

# Uinput device to inject scroll events
ui = uinput.UInput({ e.EV_KEY : [e.KEY_SCROLLUP, e.KEY_SCROLLDOWN] }, name="FixGnomeScrollXwayland", version=0x3)


# 0 = unknown, -1 for up, +1 for down
last_direction = 0


def handle_scroll(amount: float):
    global last_direction

    if amount == 1.0 and last_direction == -1.0:
        # This event is scrolling down 1 click after previously scrolling up
        # Generate a scroll event that will be properly handled
        print("Repeat down")

    if amount == -1.0 and last_direction == 1.0:
        # This event is scrolling up 1 click after previously scrolling down
        # Generate a scroll event that will be properly handled
        print("Repeat up")

    # Store sign of last scroll event
    if amount > 0.0:
        last_direction = 1.0
    elif amount < 0.0:
        last_direction = -1.0



def main():
    global li
    try:
        while True:
            try:
                for event in li.get_event():
                    
                    # Workaround for old unmaintained library stuff
                    # LIBINPUT_EVENT_POINTER_SCROLL_WHEEL is not in the enum...
                    event._libinput.libinput_event_get_type.restype = int

                    print(event.type)
                    continue
                    if event.type == libinput.constant.Event.POINTER_AXIS:
                        ptev = event.get_pointer_event()
                        if ptev.has_axis(libinput.constant.PointerAxis.SCROLL_VERTICAL):
                            handle_scroll(ptev.get_axis_value_discrete(libinput.constant.PointerAxis.SCROLL_VERTICAL))
            except ValueError:
                # Unknown / unhandled event
                print("HERE")
                traceback.print_exc()
                pass
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
