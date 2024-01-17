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
# Linux version of script (written with AutoHotKey)
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
# NOTE: Do not leave this script running while playing Java Edition 1.15+ as it
# can prevent ctrl from being passed to the game correctly and sprint will not
# work at all. Either remap F9 in Java Edition 1.15+ (not recommended) or just
# stop the script before playing Java Edition 1.15+ and use the builtin toggle
# sprint functionality.
#
# This script uses libinput and udev (via python3-evdev module) thus works on 
# both X11 and wayland
#
################################################################################
#
# Author: Marcus Behel
# Date: January 17, 2024
# Version: 1.2.0
#
################################################################################




# Input event codes in ecodes. List at https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
from evdev import ecodes
from libmacro import LibMacro, LibMacroScript
from typing import List
import time

class Script(LibMacroScript):
    def __init__(self):
        super().__init__()
        self.sprint_state = False
    
    def toggle_sprint(self):
        self.sprint_state = not self.sprint_state
        if not self.sprint_state:
            # Release the sprint key now
            self.release_key(ecodes.KEY_F9)
            print("RELEASE", flush=True)
        else:
            # Release before pressing
            # Ensures subsequent press is properly detected
            # Not an issue with java edition, but necessary for bedrock
            # using MCPELauncher
            # The sleep is needed because the game polls input (doesn't handle events)
            # So need to wait 50ms to ensure it sees the release
            self.release_key(ecodes.KEY_F9)  
            time.sleep(0.050)          
            self.press_key(ecodes.KEY_F9)
            print("PRESS", flush=True)

    def quick_release(self):
        if self.sprint_state:
            # Release then press again if sprint is currently held
            # The sleep is needed because the game polls input (doesn't handle events)
            # So need to wait 50ms to ensure it sees the release
            self.release_key(ecodes.KEY_F9)
            time.sleep(0.050)
            self.press_key(ecodes.KEY_F9)
            print("QUICK_RELEASE", flush=True)

    def handle_key(self, keycode: int, pressed: bool):
        # When LControl or RControl pressed toggle the sprint key state
        if pressed and keycode in [ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL]:
            self.toggle_sprint()
        elif not pressed:
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
            if keycode in [ecodes.KEY_ENTER, ecodes.KEY_ESC, ecodes.KEY_E, ecodes.KEY_Z]:
                time.sleep(0.100)       # Wait for UI to close
                self.quick_release()
            elif keycode in [ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT]:
                time.sleep(0.050)       # Wait for sneak to fully stop
                self.quick_release()

    def handle_mouse_button(self, button: int, pressed: bool):
        pass

    def handle_mouse_scroll(self, vertical: bool, distance: float):
        pass

    def keys_generated(self) -> List[int]:
        return [ecodes.KEY_F9]


if __name__ == "__main__":
    print("STARTING. Press Ctrl+C to exit.")
    lm = LibMacro(Script())
    lm.run()
