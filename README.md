# SDVX in CircuitPython
 SDVX controller in CircuitPython for Raspberry Pi Pico

 Written in CircuitPython for ease of changing configuration without requiring recompiling firmware.

 Currently, keyboard mode has a response time of roughly 6-8ms and 14-17ms with mouse. Gamepad mode is probably the same as keyboard. Thats the fastest CircuitPython will go.

 Default settings are meant for Speedy's pocket SDVX pico. Enjoy reactive encoder light animation instead of RGB rainbow.

 Supports WS2812B as button LEDs, change led_btn in config line 32 to False.
 
 *WARNING*
 Flashing/Strobing lights

Installation:
1. Install CircuitPython
https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython

 Optional: Use CircuitPython_Konami_spoof.uf2 (CircuitPython 7.2.0-alpha). Untested, not sure if spoof works.

2. Copy boot.py, code.py, and config.py to CIRCUITPY drive

3. Hold BT-A while plugging in controller for Keyboard only mode, and BT-D for Keyboard and Mouse mode
