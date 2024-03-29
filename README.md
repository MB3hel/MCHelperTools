# MCHelperTools
Helper tools for use with Minecraft.


## WindowsKeyHelpers

*Most of the windows tools were built with [AutoHotKey](https://www.autohotkey.com/). Binaries created using AutoHotKey are available to download on the [releases](https://github.com/MB3hel/MCHelperTools/releases) page. These binaries are unsigned, so you may get a warning from windows smart screen.*

*To use one such script on windows, simply launch the exe before starting the game. The script will have an icon in the task bar to indicate that it is running. To stop the script, right click the task bar icon and click Exit. These scripts affect all programs, not just specific games, so make sure you close them afterwards or you may experience weird effects in other programs.*

- **ToggleSprintBedrock**: This script is used to replicate Minecraft Java Edition 1.15+'s toggle sprint behavior in Minecraft Bedrock Edition (Win 10 edition) or in older versions of Java Edition. This script will use the `F9` key as the sprint key. Pressing left `Ctrl` will toggle whether the `F9` key is "held". This replicates the behavior of toggle sprint, once the sprint key is mapped to `F9` in game.   
    - This script also has some "extra" features to help with bedrock (none of the features described here matter in Java edition). In bedrock edition, the sprint key must be quickly released then held again after some actions (exiting a gui, sneaking, sleeping, respawning, etc). Some of these are easily detected. When left `Shift` is released, `E` is pressed, or `Esc` is pressed the sprint key will be released and then re-held quickly. This should never be noticeable to the player. Sleeping and respawning are not easily detected, therefore it is up to the player to reactivate sprint after these actions (easiest way is tapping left shift).

- **MouseRemap**: Remaps side buttons on cheap mice to F13 and F14. This allows them to be used in game instead of as back and forward.

- **DisableCtrlEsc**: Disables the Ctrl+Esc key combo. Prevents accidental exiting of some games.

- **DisableWinKey**: Disables the windows (super) key. Prevents accidental exiting of some games.



## LinuxKeyHelpers

*Run the following commands before using any of these tools. Then reboot. Alternatively, run the scripts as root.*

```sh
sudo usermod -G input -a "${USERNAME}"
```

*Note that these scripts require python3 along with the python libinput and evdev libraries.*

- **ToggleSprintBedrock.py**: This is a Linux version of the toggle sprint helper script. Works on X11 and Wayland sessions. *Be aware that [this bug](https://gitlab.gnome.org/GNOME/mutter/-/issues/398) will result in this causing freezes on Gnome X11 sessions. Wayland and other desktops are not impacted.*

- **FixGnomeScrollXwayland.py**: This is a workaround for a bug with GNOME. After suspend (and maybe at other times too?), xwayland apps (including minecraft) will miss the first scroll event after changing direction with the scroll wheel. [GNOME Bug Report](https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/5896)


## Notices

- Minecraft is a trademark of Mojang. Nothing in this repository is related to Minecraft or affiliated with Mojang in any way. This is simply a collection of scripts / tools useful when playing the game.

- Note that it may be against the rules to use these scripts on some servers. It is the responsibility of the user to ensure that the use of these script / tools does not violate any rules or regulations.



## License (MIT License)

This license applies only to these scripts / tools. This does not apply to binaries created with AutoHotKey. These are distributed under the terms of AHK's GPLv2 license.

Copyright © 2021 Marcus Behel

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
