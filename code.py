from adafruit_pixelbuf import PixelBuf
import board
from digitalio import DigitalInOut, Direction, Pull
from neopixel_write import neopixel_write
from rotaryio import IncrementalEncoder
from time import monotonic
from usb_hid import devices

#
# Load eveyrthing from config
#
from config import (
    enc_ppr, enc_pins, enc_addr, enc_colors, enc_keybind, btn_map, led_btns, pixel_pin,
    pixel_count, pixel_brightness, mouse_speed
)

#
# Button map index
# 0 = Button GPIO pin
# 1 = Gamepad button ID
# 2 = HID keyboard code
# 3 = LED GPIO pin
# 4 = WS2812b button LED address
# 5 = WS2812b button pressed color
# 6 = WS2812b button released color
#
BTN_PIN, GPD_ID, KEY_COD, LED_PIN, WS_ADD, WS_PRE, WS_REL = range(7)

#
# Prepare button input array
#
buttons = [DigitalInOut(x[BTN_PIN]) for x in btn_map]
for x in buttons:
    x.pull = Pull.UP

#
# Keyboard & Mouse mode check
# Default is Gamepad mode, kb_mode = False
#
kb_mode = False     # Keyboard
m_mode = False      # Mouse

#
# Controller mode button press check
# While plugging in controller
# Hold BT-A - Keyboard Only
# Hold BT-D - Keyboard & Mouse
# Wait until button is released
#
while (not buttons[0].value) or (not buttons[3].value):
    kb_mode = True
    if not buttons[3].value:
        m_mode = True

#
# Subclass to use pixel buffer module
# Needed GPIO pin and _transmit() to work
#
class pixelBuffer(PixelBuf):
    def __init__(self, pin: board.Pin, size, byteorder, brightness, auto_write):
        super().__init__(
            size=size, byteorder=byteorder, brightness=brightness, auto_write=auto_write
        )

        self.pin = DigitalInOut(pin)
        self.pin.direction = Direction.OUTPUT

    def _transmit(self, buffer: bytearray) -> None:
        neopixel_write(self.pin, buffer)

#
# Create pixel buffer
#
pixel_buf = pixelBuffer(
    pixel_pin,
    pixel_count,
    byteorder="GRB",
    brightness=pixel_brightness,
    auto_write=True,
)

#
# Set LED pins
#
btn_leds = [x[LED_PIN] for x in btn_map]
for x in range(len(btn_leds)):
    if btn_leds[x] is not None:
        btn_leds[x] = DigitalInOut(btn_leds[x])
        btn_leds[x].direction = Direction.OUTPUT

#
# Find HID devices to be used
#
for x in devices:
    if x.usage == 0x02 and m_mode:
        mouse = x
        continue
    if x.usage == 0x06 and kb_mode:
        keyboard = x
        continue
    if x.usage == 0x05 and not kb_mode:
        gamepad = x
        continue

#
# Set appropriate reports
#
if kb_mode:
    keyboard_report = bytearray(len(btn_map) + 4)
    if m_mode:
        mouse_report = bytearray(2)
else:
    gamepad_report = bytearray(4)
    # Binary lookup table
    bin_lookup = (1, 2, 4, 8, 16, 32, 64, 128)

#
# Set encoders
#
encoders = (
    IncrementalEncoder(enc_pins[0], enc_pins[1]),
    IncrementalEncoder(enc_pins[2], enc_pins[3]),
)

#
# LED button mode animation variables
#
prev_enc_pos = [0, 0]
cur_pos = 0
enc_delta = 0

if led_btns:
    pixeloffset = int(pixel_count / 2)
    enc_led_pos = [0, pixeloffset]

#
# Timestamps for movement timeouts
#
cur_time = monotonic()
enc_last_ch = [cur_time, cur_time]

#
# Main loop to poll inputs
#
while True:
    #
    # Poll encoders
    #
    for x in range(2):
        # Save position
        cur_pos = encoders[x].position
        # Save current time
        cur_time = monotonic()
        # Get delta
        enc_delta = cur_pos - prev_enc_pos[x]
        # Confine to range 0 - (enc_ppr - 1)
        prev_enc_pos[x] = cur_pos % enc_ppr
        # Update encoder to match
        encoders[x].position = prev_enc_pos[x]

        #
        # LED animations
        # Two types of animations
        # If buttons have simple LEDS, and WS2812b underlights:
        #   Scroll encoder color on the side
        #
        # Buttons have WS2812b leds:
        #   Simple on off for encoder led
        #
        if led_btns:    # Simple LEDs in buttons
            # Check for led change delay
            if (cur_time - enc_last_ch[x]) > 0.1:
                # Move led position
                if enc_delta != 0:
                    # Move pos +-1
                    if enc_delta > 0:
                        enc_led_pos[x] += 1
                    else:
                        enc_led_pos[x] -= 1

                    # Restrict range
                    enc_led_pos[x] %= pixeloffset

                    # Mark time for led delay
                    enc_last_ch[x] = cur_time

                # Set colors
                for y in range(0, pixeloffset):
                    if y == enc_led_pos[x]:
                        pixel_buf[y + (x * pixeloffset)] = enc_colors[x]
                    else:
                        pixel_buf[y + (x * pixeloffset)] = enc_colors[x + 2]

        else:   # WS2812b buttons
            # Encoder moved
            if enc_delta != 0:
                # Set to on color
                pixel_buf[enc_addr[x]] = enc_colors[x]
                # Mark time for last moved
                enc_last_ch[x] = cur_time
            # Check for delay to prevent blinking
            elif (cur_time - enc_last_ch[x]) > 0.1:
                # Set to off color
                pixel_buf[enc_addr[x]] = enc_colors[x + 2]

        # Relative position
        if kb_mode:
            # Mouse mode
            if m_mode:
                # Exaggerate movement for mouse
                enc_delta *= mouse_speed

                # Cap relative position to +/-120
                if enc_delta > 120:
                    enc_delta = 120
                elif enc_delta < -120:
                    enc_delta = -120

                mouse_report[x] = enc_delta % 256

            # Keyboard mode
            else:
                if enc_delta > 0:       # +delta = keybinds 0, 1
                    keyboard_report[len(buttons) + 2 + x] = enc_keybind[x]
                elif enc_delta < 0:     # -delta = keybinds 2, 3
                    keyboard_report[len(buttons) + 2 + x] = enc_keybind[x + 2]
                else:               # 0
                    keyboard_report[len(buttons) + 2 + x] = 0x00

        # Absolute position
        else:
            # gamepad_report[2:3] are X, Y
            # Change to range 0-255
            gamepad_report[x + 2] = int(prev_enc_pos[x] * (255 / enc_ppr))

    #
    # Report mouse mid-loop, maybe even out timing
    #
    if m_mode:
        mouse.send_report(mouse_report)

    #
    # Poll all the buttons
    # Buttons are to ground with pull up resisters
    # Inputs must be reversed/negated
    #
    for x in range(0, len(buttons)):
        # Button is pressed
        if not buttons[x].value:
            # Reactive button lights
            if led_btns:
                if btn_leds[x] is not None:
                    btn_leds[x].value = True
            else:
                if btn_map[x][WS_ADD] is not None:
                    pixel_buf[x] = btn_map[x][WS_PRE]

            # Mark button as pressed
            if kb_mode:
                keyboard_report[x + 2] = btn_map[x][KEY_COD]
            else:
                if (btn_map[x][GPD_ID]) < 8:
                    gamepad_report[0] |= bin_lookup[btn_map[x][GPD_ID] - 1]
                else:
                    gamepad_report[1] |= bin_lookup[(btn_map[x][GPD_ID] - 1) % 8]

        # Button is not pressed
        else:
            # Reactive button lights
            if led_btns:
                if btn_leds[x] is not None:
                    btn_leds[x].value = False
            else:
                if btn_map[x][WS_ADD] is not None:
                    pixel_buf[x] = btn_map[x][WS_REL]

            # Mark button as not pressed
            if kb_mode:
                keyboard_report[x + 2] = 0
            else:
                if (btn_map[x][GPD_ID]) < 8:
                    gamepad_report[0] &= ~bin_lookup[btn_map[x][GPD_ID] - 1]
                else:
                    gamepad_report[1] &= ~bin_lookup[(btn_map[x][GPD_ID] - 1) % 8]

    #
    # Send HID reports
    #
    if kb_mode:
        keyboard.send_report(keyboard_report)
    else:
        gamepad.send_report(gamepad_report)
