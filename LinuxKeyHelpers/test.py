
# Input event codes in ecodes. List at https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
from evdev import ecodes
from libmacro import LibMacro, LibMacroScript
from typing import List

class Script(LibMacroScript):
    def handle_key(self, keycode: int, pressed: bool):
        print("Key {} {}".format(keycode, "pressed" if pressed else "released"))
        

    def handle_mouse_button(self, button: int, pressed: bool):
        print("Mouse {} {}".format(button, "pressed" if pressed else "released"))

    def handle_mouse_scroll(self, vertical: bool, distance: float):
        print("Scroll {} degrees {}".format(distance, "vertically" if vertical else "horizontally"))

    def keys_generated(self) -> List[int]:
        return []

if __name__ == "__main__":
    lm = LibMacro(Script())
    lm.run()
