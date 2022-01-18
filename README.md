# SDVX in CircuitPython
 SDVX controller in CircuitPython for Raspberry Pi Pico

Written in CircuitPython for ease of changing configuration values without requiring recompiling firmware. Currently, keyboard & mouse mode has a response time of roughly 15ms or 67hz at best. Gamepad mode is probably half of that.
 
 *WARNING*
 Flashing/Strobing lights

Installation:
1. Install CircuitPython
https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython

Optional: Use CircuitPython_Konami_spoof.uf2 (CircuitPython 7.20alpha)

2. Copy boot.py, code.py, and config.py to CIRCUITPY drive

3. Hold BT-A while plugging in controller for Keyboard & Mouse mode
