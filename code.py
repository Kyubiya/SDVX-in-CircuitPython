from adafruit_pixelbuf import PixelBuf
import board
from digitalio import DigitalInOut, Direction, Pull
from neopixel_write import neopixel_write
from rotaryio import IncrementalEncoder
from time import monotonic
from usb_hid import devices

# Load eveyrthing in config
from config import (
    enc_ppr,
    enc_pins,
    btn_pins,
    led_btns,
    led_pins,
    pixel_pin,
    pixel_count,
    pixel_brightness,
    pixel_colors,
    pixel_off,
    report_btn_id,
    report_keybind,
    enc_keybind,
    mouse_speed,
)

# Prepare button input array
buttons = [DigitalInOut(x) for x in btn_pins]
for x in buttons:
    x.pull = Pull.UP

# Keyboard & Mouse mode check
# While plugging in controller
# Hold BT-A - Keyboard Only
# Hold BT-D - Keyboard & Mouse
kb_mode = False
m_mode = False

# Wait until button is released
while (not buttons[0].value) or (not buttons[3].value):
    kb_mode = True
    if not buttons[3].value:
        m_mode = True

# Binary lookup table for gamepad_report
if not kb_mode:
    bin_lookup = (1, 2, 4, 8, 16, 32, 64, 128)

# Subclass to use pixel buffer module
# Needed GPIO pin and _transmit() to work
class pixelBuffer(PixelBuf):
    def __init__(self, pin: board.Pin, size, byteorder, brightness, auto_write):
        super().__init__(
            size=size, byteorder=byteorder, brightness=brightness, auto_write=auto_write
        )

        self.pin = DigitalInOut(pin)
        self.pin.direction = Direction.OUTPUT

    def _transmit(self, buffer: bytearray) -> None:
        neopixel_write(self.pin, buffer)


# Create pixel buffer
pixel_buf = pixelBuffer(
    pixel_pin,
    pixel_count,
    byteorder="GRB",
    brightness=pixel_brightness,
    auto_write=True,
)

# Initialize pixel buffer with colors
# WS2812B behavior is the inverse of LED buttons
# On while not pressed, off while pressed
if not led_btns:
    for x in range(len(pixel_colors) - 2):
        pixel_buf[x] = pixel_colors[x]

# Set LED pins
btn_leds = [DigitalInOut(x) for x in led_pins]
for x in btn_leds:
    x.direction = Direction.OUTPUT

# Find HID devices to be used
for x in devices:
    if x.usage == 0x02 and m_mode:
        mouse = x
        continue
    if x.usage == 0x06 and kb_mode:
        keyboard = x
        continue
    elif x.usage == 0x05 and not kb_mode:
        gamepad = x
        continue

# Set appropriate reports
if kb_mode:
    keyboard_report = bytearray(len(report_keybind) + 4)
    kb_delta = 0
    if m_mode:
        mouse_report = bytearray(2)
else:
    gamepad_report = bytearray(4)
    gpd_temp = None

# Set encoders
encoders = (
    IncrementalEncoder(enc_pins[0], enc_pins[1]),
    IncrementalEncoder(enc_pins[2], enc_pins[3]),
)

# Initialize position variables
prev_enc_pos = [0, 0]
cur_pos = None
enc_led_pos = [0, int(pixel_count / 2)]

# Start encoder WS2812B
if led_btns:
    pixel_buf[enc_led_pos[0]] = pixel_colors[len(btn_pins)]
    pixel_buf[enc_led_pos[1]] = pixel_colors[len(btn_pins) + 1]

# Timestamps for movement timeouts
cur_time = monotonic()
enc_last_ch = [cur_time, cur_time]
enc_led_ch = [cur_time, cur_time]

#
# Main loop to poll inputs
#
while True:
    # Poll encoders
    for x in range(2):
        # Save position
        cur_pos = encoders[x].position
        # Save current time
        cur_time = monotonic()

        # Encoder moved
        if prev_enc_pos[x] != cur_pos:
            # WS2812B animations
            # For LED buttons' reactive encoder animation
            if led_btns:
                # Restrict speed of led animation
                if (cur_time - enc_led_ch[x]) > 0.1:
                    # Turn off prev pixel
                    pixel_buf[enc_led_pos[x]] = pixel_off

                    # +/-1 to position
                    enc_led_pos[x] += prev_enc_pos[x] - cur_pos
                    # Restrict position to half
                    enc_led_pos[x] %= int(pixel_count / 2)
                    # Left or right side
                    enc_led_pos[x] += x * int(pixel_count / 2)

                    # Turn on pixel
                    pixel_buf[enc_led_pos[x]] = pixel_colors[len(btn_pins) + x]

                    # Mark timer for speed restriction
                    enc_led_ch[x] = cur_time
            else:
                # WS2812B buttons reactive encoders
                # Turn on for reactive encoders
                pixel_buf[len(btn_pins) + x] = pixel_colors[len(btn_pins) + x]

                # Update movement timeout check
                enc_last_ch[x] = cur_time

            # Calculate relative movement position
            if kb_mode:
                kb_delta = cur_pos - prev_enc_pos[x]
                if m_mode:
                    # Mouse speed multiplier
                    kb_delta *= mouse_speed
                    # Confine to max speed
                    if kb_delta > 120:
                        kb_delta = 120
                    elif kb_delta < -120:
                        kb_delta = -120
                    mouse_report[x] = kb_delta % 256
                else:
                    if kb_delta > 0:
                        # + enc_keybind 0, 2
                        keyboard_report[len(report_keybind) + 2 + x] = enc_keybind[
                            x * 2
                        ]
                    else:
                        # - enc_keybind 1, 3
                        keyboard_report[len(report_keybind) + 2 + x] = enc_keybind[
                            (x * 2) + 1
                        ]

            # Confine to range 0 - enc_ppr
            prev_enc_pos[x] = cur_pos % enc_ppr
            # Update encoder to match
            encoders[x].position = prev_enc_pos[x]

            # Absolute movement position
            if not kb_mode:
                # gamepad_report[2:3] are X, Y
                # Change to range 0-255
                gamepad_report[x + 2] = int(prev_enc_pos[x] * (255 / enc_ppr))
        else:
            if (
                # For WS2812B reactive encoder
                not led_btns
                # Check if not already off
                and pixel_buf[len(btn_pins) + x] != pixel_off
                # Check for movement timeout
                and (cur_time - enc_last_ch[x]) > 0.2
            ):
                pixel_buf[len(btn_pins) + x] = pixel_off
    # Report mouse mid-loop, maybe even out timing
    if m_mode:
        mouse.send_report(mouse_report)
        # Clear report
        if mouse_report[0] != 0:
            mouse_report[0] = 0
        if mouse_report[1] != 0:
            mouse_report[1] = 0

    # Poll all the buttons
    for x in range(0, len(buttons)):
        if not buttons[x].value:
            # Reactive button lights
            if led_btns:
                btn_leds[x].value = True
            else:
                pixel_buf[x] = pixel_off

            # Mark button as pressed
            if kb_mode:
                keyboard_report[x + 2] = report_keybind[x]
            else:
                gpd_temp = report_btn_id[x] - 1
                if gpd_temp < 8:
                    gamepad_report[0] += bin_lookup[gpd_temp]
                else:
                    gamepad_report[1] += bin_lookup[gpd_temp % 8]
        else:
            # Reactive button lights
            if led_btns:
                btn_leds[x].value = False
            else:
                pixel_buf[x] = pixel_colors[x]

    # Send HID reports
    if kb_mode:
        keyboard.send_report(keyboard_report)
        # Clear report
        for x in range(1, len(keyboard_report)):
            if keyboard_report[x] != 0:
                keyboard_report[x] = 0
    else:
        gamepad.send_report(gamepad_report)
        # Clear only button section of report
        # Gamepad uses absolute movement, keep X,Y positions
        if gamepad_report[0] != 0:
            gamepad_report[0] = 0
        if gamepad_report[1] != 0:
            gamepad_report[1] = 0
