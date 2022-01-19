from adafruit_pixelbuf import PixelBuf
import board
from digitalio import DigitalInOut, Direction, Pull
from neopixel_write import neopixel_write
from rotaryio import IncrementalEncoder
from time import monotonic, sleep
from usb_hid import devices

# Config file
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
    mouse_speed,
)

# Binary lookup table
bin_lookup = (1, 2, 4, 8, 16, 32, 64, 128)

buttons = [DigitalInOut(x) for x in btn_pins]
for x in buttons:
    x.direction = Direction.INPUT
    x.pull = Pull.UP

# Keyboard & Mouse mode check
# Hold BT-A while plugging in controller
kbm_mode = False

# Wait until button is released
while not buttons[0].value:
    if not kbm_mode:
        kbm_mode = True

# Subclass to use built in pixel buffer
# Needed IO pin and _transmit()
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

# WS2812B behavior is inverse of LED
# On while not pressed, initialize buffer with colors
if not led_btns:
    for x in range(len(pixel_colors) - 2):
        pixel_buf[x] = pixel_colors[x]

# Set LED pins
btn_leds = [DigitalInOut(x) for x in led_pins]
for x in btn_leds:
    x.direction = Direction.OUTPUT

# Set HID devices to be used
for x in devices:
    if kbm_mode:
        if x.usage == 0x06:
            keyboard = x
        elif x.usage == 0x02:
            mouse = x
    elif x.usage == 0x05:
        gamepad = x
# Set appropriate reports
if "gamepad" in locals():
    gamepad_report = bytearray(4)
    gpd_temp = None
else:
    keyboard_report = bytearray(2 + len(report_keybind))
    mouse_report = bytearray(2)
    mouse_delta = 0

# Set encoders
encoders = (
    IncrementalEncoder(enc_pins[0], enc_pins[1]),
    IncrementalEncoder(enc_pins[2], enc_pins[3]),
)

prev_enc_pos = [0, 0]
cur_pos = None
enc_led_pos = [0, int(pixel_count / 2)]

# Start encoder WS2812B
if led_btns:
    pixel_buf[enc_led_pos[0]] = pixel_colors[len(btn_pins)]
    pixel_buf[enc_led_pos[1]] = pixel_colors[len(btn_pins) + 1]

# Time trackers
cur_time = monotonic()
enc_last_ch = [cur_time, cur_time]
enc_led_ch = [cur_time, cur_time]


# Main loop to poll inputs
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
            # WS2812B buttons reactive encoders
            else:
                # Turn on for reactive encoders
                pixel_buf[len(btn_pins) + x] = pixel_colors[len(btn_pins) + x]

                # Update movement timer
                enc_last_ch[x] = cur_time

            if "mouse" in locals():
                # Calculate relative mouse movement
                mouse_delta = (cur_pos - prev_enc_pos[x]) * mouse_speed

                # Check max speed
                if mouse_delta > 120:
                    mouse_delta = 120
                elif mouse_delta < -120:
                    mouse_delta = -120

                mouse_report[x] = mouse_delta % 256

            # Update prev position
            prev_enc_pos[x] = cur_pos % enc_ppr
            encoders[x].position = prev_enc_pos[x]

            if "gamepad" in locals():
                gamepad_report[1 + x] = int(prev_enc_pos[x] * (255 / enc_ppr))
        else:
            # For WS2812B reactive encoder
            if (
                not led_btns
                # Check if not already off
                and pixel_buf[len(btn_pins) + x] != pixel_off
                # Check if encoder stopped moving
                and (cur_time - enc_last_ch[x]) > 0.2
            ):
                pixel_buf[len(btn_pins) + x] = pixel_off

    # Scan buttons
    for x in range(0, len(buttons)):
        if not buttons[x].value:
            # Reactive button lights
            if led_btns:
                btn_leds[x].value = True
            else:
                pixel_buf[x] = pixel_off
            # Mark button as pressed
            if "gamepad" in locals():
                gpd_temp = report_btn_id[x] - 1
                if gpd_temp < 8:
                    gamepad_report[0] += bin_lookup[gpd_temp]
                else:
                    gamepad_report[1] += bin_lookup[gpd_temp % 8]
            else:
                keyboard_report[x + 2] = report_keybind[x]
        else:
            # Reactive button lights
            if led_btns:
                btn_leds[x].value = False
            else:
                pixel_buf[x] = pixel_colors[x]
    # Send HID reports
    if "gamepad" in locals():
        gamepad.send_report(gamepad_report)
        if gamepad_report[0] != 0:
            gamepad_report[0] = 0
        if gamepad_report[1] != 0:
            gamepad_report[1] = 0
    else:
        keyboard.send_report(keyboard_report)
        for x in range(1, len(keyboard_report)):
            if keyboard_report[x] != 0:
                keyboard_report[x] = 0
        mouse.send_report(mouse_report)
        if mouse_report[0] != 0:
            mouse_report[0] = 0
        if mouse_report[1] != 0:
            mouse_report[1] = 0
