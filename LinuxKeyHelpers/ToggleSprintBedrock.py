
from libmacro import libmacro_run, libmacro_press_key, libmacro_release_key, EventType
from evdev import ecodes
import time


sprint_state = False


def toggle_sprint():
    global sprint_state

    # Invert sprint state
    sprint_state = not sprint_state

    # Apply state
    if not sprint_state:
        # Release F9
        libmacro_release_key(ecodes.KEY_F9)
        print("RELEASE", flush=True)
    else:
        # Release F9
        # Ensures subsequent press is properly detected
        # Not an issue with java edition, but necessary for bedrock
        # using MCPELauncher
        libmacro_release_key(ecodes.KEY_F9)
        time.sleep(0.01)
        
        # Press F9
        libmacro_press_key(ecodes.KEY_F9)

        print("PRESS", flush=True)


def quick_release():
    global ui, sprint_state
    if sprint_state:
        # Release F9
        libmacro_release_key(ecodes.KEY_F9)

        time.sleep(0.05)

        # Press F9
        libmacro_press_key(ecodes.KEY_F9)

        print("QUICK_RELEASE", flush=True)


def handler(event_type: EventType, value):
    # Keycode constants available in ecodes
    # See https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h

    
    if event_type == EventType.KeyPress:
         # LControl or RControl pressed toggle the sprint key state
        if value in [ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL]:
            toggle_sprint()
    elif event_type == EventType.KeyRelease:
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
        if value in [ecodes.KEY_ENTER, ecodes.KEY_ESC, ecodes.KEY_E, ecodes.KEY_Z]:
            time.sleep(0.100)       # Wait for UI to close
            quick_release()
        elif value in [ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT]:
            time.sleep(0.050)       # Wait for sneak to fully stop
            quick_release()

libmacro_run(handler)
