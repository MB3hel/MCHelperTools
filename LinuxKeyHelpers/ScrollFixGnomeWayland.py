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
# Workaround for a GNOME bug where first scroll after changing direction is
# ignored (sometimes by some xwayland apps)
# https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/5896
#
# Note that this bug only impacts (some) xwayland apps on wayland sessions
# Some apps are impacted (eg Minecraft), but others (eg vscode) are not
# THIS SCRIPT WILL HAVE UNINTENDED SIDE EFFECTS IN APPS THAT ARE NOT IMPACTED!
#
################################################################################
#
# Author: Marcus Behel
# Date: January 17, 2024
# Version: 1.0.0
#
################################################################################



# Input event codes in ecodes. List at https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
from evdev import ecodes
from libmacro import LibMacro, LibMacroScript
from typing import List

class Script(LibMacroScript):
    def __init__(self):
        super().__init__()
        self.last_distance = 0.0

    def handle_key(self, keycode: int, pressed: bool):
        pass
    
    def handle_mouse_button(self, button: int, pressed: bool):
        pass

    def handle_mouse_scroll(self, vertical: bool, distance: float):
        # If this is the first scroll in a different direction, repeat the event
        if distance > 0.0 and self.last_distance < 0.0:
            # Repeat first scroll down after scrolling up
            self.scroll_wheel_vertical(1)
        if distance < 0.0 and self.last_distance > 0.0:
            # Repeat first scroll up after scrolling down
            self.scroll_wheel_vertical(-1)
        self.last_distance = distance

    def rel_events_generated(self) -> List[int]:
        return [ecodes.REL_WHEEL]


if __name__ == "__main__":
    print("STARTING. Press Ctrl+C to exit.")
    lm = LibMacro(Script())
    lm.run()
