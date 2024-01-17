
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
