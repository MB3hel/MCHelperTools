;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;
; Copyright © 2020 Marcus Behel
;
; Permission is hereby granted, free of charge, to any person obtaining a copy 
; of this software and associated documentation files (the “Software”), to deal
; in the Software without restriction, including without limitation the rights
; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
; copies of the Software, and to permit persons to whom the Software is
; furnished to do so, subject to the following conditions:
;
; The above copyright notice and this permission notice shall be included in all
; copies or substantial portions of the Software.
;
; THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
; SOFTWARE.
;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;
; Windows version of script (written with AutoHotKey)
; 
; Script to simulate the behavior of Minecraft Java Edition 1.15+
; When ctrl is pressed sprint is enabled until it is pressed again
; This persists across sneaking, opening UIs, etc
;
; Bedrock edition (and Java Edition before 1.15) lack this feature.
; This script provides a way to get this behavior in these versions of the game
; by mapping a different key (by default F9) to sprint in the game. This script
; will then "hold" F9 when you press ctrl, and release it when you press it
; again, thereby simulating the toggle sprint functionality of Java Edition
; 1.15+.
;
; NOTE: Do not leave this script running while playing Java Edition 1.15+ as it
; can prevent ctrl from being passed to the game correctly and sprint will not
; work at all. Either remap F9 in Java Edition 1.15+ (not recommended) or just
; stop the script before playing Java Edition 1.15+ and use the builtin toggle
; sprint functionality.
;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;
; Author: Marcus Behel
; Date: Sept 22, 2020
; Version: 1.0.4
;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; Track sprint state
sprint_state := 0


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Toggle holding the sprint key (F9)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
ToggleSprint(){
    global sprint_state
	sprint_state := !sprint_state
    if (sprint_state = 0){
        Send, {F9 up}
    }else{
        Send, {F9 down}
    }
}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Quickly release then continue holding the sprint key (assuming it was held
;     to begin with)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
QuickRelease(){
    global sprint_state
    if (sprint_state = 1){
        Send, {F9 up}
        Sleep, 50
        Send, {F9 down}
    }
}


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Sprint toggle key(s)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; Toggle holding the sprint key (F9) when ctrl is pressed
; ~ makes sure to pass throught the key to any other application
~LControl::
    ToggleSprint()
return
~RControl::
    ToggleSprint()
return


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;
; There are several situations where bedrock edition (Win10) does not continue
; to detect the held key. Usually, these are when leaving a GUI (chat, block 
; GUI, etc). To have the game re-detect the key it is necessary to briefly
; release and then continue holding the sprint key (F9).
;
; Enter can be used to exit chat
; Esc can be used to exit chat or a block GUI
; E can be used to exit a block GUI
; Z can be used to close potion effects gui
;
; There is another (more subtle issue) related to sneaking. After releasing 
; shift to stop sneak sprint sometimes "glitches" when you next start moving.
; By this I mean you start to sprint, stop, then start again really quickly.
; This seems to be fixed by quickly toggling the sprint key (like when leaving a
; UI) when releasing shift.
;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$~Enter::
    ; Wait for UI to close
    Sleep 100
    QuickRelease()
return
$~Esc::
    ; Wait for UI to close
    Sleep 100
    QuickRelease()
return
$~*e::
    ; Wait for UI to close
    Sleep 100
    QuickRelease()
return
$~*z::
    ; Wait for UI to close
    Sleep 100
    QuickRelease()
return
$~Shift Up::
    ; Wait for sneak to fully stop
    Sleep 50
    QuickRelease()
return
