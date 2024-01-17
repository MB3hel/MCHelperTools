
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
