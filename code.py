import adafruit_pixelbuf
import board
import digitalio
import keypad
import neopixel_write
import rotaryio
import time
import usb_hid

# Config file
import config

# Keyboard & Mouse mode check
# Hold BT-A while plugging in controller
kbm_mode = False
kbm_check = digitalio.DigitalInOut(config.btn_pins[0])
kbm_check.direction = digitalio.Direction.INPUT
kbm_check.pull = digitalio.Pull.UP

# Wait to verify button is held
time.sleep(0.5)

# Wait until button is released
while not kbm_check.value:
    if not kbm_mode:
        kbm_mode = True
    time.sleep(1)

# Release GPIO pin
kbm_check.deinit()

# Subclass to use built in pixel buffer
# Needed IO pin and _transmit()
class pixelBuffer(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin: board.Pin, size, byteorder, brightness, auto_write):
        super().__init__(
            size=size, byteorder=byteorder, brightness=brightness, auto_write=auto_write
        )

        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT

    def _transmit(self, buffer: bytearray) -> None:
        neopixel_write.neopixel_write(self.pin, buffer)


# Create pixel buffer
pixel_buf = pixelBuffer(
    config.pixel_pin,
    config.pixel_count,
    byteorder="GRB",
    brightness=config.pixel_brightness,
    auto_write=True,
)

# WS2812B behavior is inverse of LED
# On while not pressed, initialize buffer with colors
if not config.led_btns:
    for x in range(len(config.pixel_colors) - 2):
        pixel_buf[x] = config.pixel_colors[x]

# Set LED pins
btn_leds = [digitalio.DigitalInOut(x) for x in config.led_pins]
for x in btn_leds:
    x.direction = digitalio.Direction.OUTPUT

# Set button input
buttons = keypad.Keys(
    config.btn_pins, value_when_pressed=False, pull=True, interval=0.01
)
btn_event = keypad.Event()

# Set HID devices to be used
for x in usb_hid.devices:
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
    gpd_array = [0] * 16
if "keyboard" in locals():
    keyboard_report = bytearray(18)
if "mouse" in locals():
    mouse_report = bytearray(2)
    mouse_delta = 0


# Set encoders
encoders = [
    rotaryio.IncrementalEncoder(config.enc_pins[0], config.enc_pins[1]),
    rotaryio.IncrementalEncoder(config.enc_pins[2], config.enc_pins[3]),
]

prev_enc_pos = [0, 0]
cur_pos = None
enc_led_pos = [0, int(config.pixel_count / 2)]

# Start encoder WS2812B
if config.led_btns:
    pixel_buf[enc_led_pos[0]] = config.pixel_colors[len(config.btn_pins)]
    pixel_buf[enc_led_pos[1]] = config.pixel_colors[len(config.btn_pins) + 1]

# Time trackers
cur_time = time.monotonic()
enc_last_ch = [cur_time, cur_time]
enc_led_ch = [cur_time, cur_time]

# Main loop to poll inputs
while True:
    # Poll encoders
    for x in range(2):
        # Save position
        cur_pos = encoders[x].position
        # Save current time
        cur_time = time.monotonic()

        # Encoder moved
        if prev_enc_pos[x] != cur_pos:
            # WS2812B animations
            # For LED buttons' reactive encoder animation
            if config.led_btns:
                # Restrict speed of led animation
                if (cur_time - enc_led_ch[x]) > 0.1:
                    # Turn off prev pixel
                    pixel_buf[enc_led_pos[x]] = config.pixel_off

                    # +/-1 to position
                    enc_led_pos[x] += prev_enc_pos[x] - cur_pos
                    # Restrict position to half
                    enc_led_pos[x] %= int(config.pixel_count / 2)
                    # Left or right side
                    enc_led_pos[x] += x * int(config.pixel_count / 2)

                    # Turn on pixel
                    pixel_buf[enc_led_pos[x]] = config.pixel_colors[
                        len(config.btn_pins) + x
                    ]

                    # Mark timer for speed restriction
                    enc_led_ch[x] = cur_time
            # WS2812B buttons reactive encoders
            else:
                # Turn on for reactive encoders
                pixel_buf[len(config.btn_pins) + x] = config.pixel_colors[
                    len(config.btn_pins) + x
                ]

                # Update movement timer
                enc_last_ch[x] = cur_time

            if "mouse" in locals():
                # Calculate relative mouse movement
                mouse_delta = (cur_pos - prev_enc_pos[x]) * config.mouse_speed

                # Check max speed
                if mouse_delta > 120:
                    mouse_delta = 120
                elif mouse_delta < -120:
                    mouse_delta = -120

                mouse_report[x] = mouse_delta % 256

            # Update prev position
            prev_enc_pos[x] = cur_pos % 24
            encoders[x].position = prev_enc_pos[x]
        else:
            # For WS2812B reactive encoder
            if (
                not config.led_btns
                # Check if not already off
                and pixel_buf[len(config.btn_pins) + x] != config.pixel_off
                # Check if encoder stopped moving
                and (cur_time - enc_last_ch[x]) > 0.5
            ):
                pixel_buf[len(config.btn_pins) + x] = config.pixel_off
            if 'mouse' in locals() and mouse_report[x] != 0:
                mouse_report[x] = 0

    # Check for button event
    if buttons.events.get_into(btn_event):
        if btn_event.pressed:
            # Reactive button lights
            if config.led_btns:
                btn_leds[btn_event.key_number].value = True
            else:
                pixel_buf[btn_event.key_number] = config.pixel_off
            # Mark button as pressed
            if "gamepad" in locals():
                gpd_array[config.report_btn_id[btn_event.key_number] - 1] = 1
            else:
                keyboard_report[btn_event.key_number + 2] = config.report_keybind[
                    btn_event.key_number
                ]
        # btn_event.released
        else:
            # Reactive button lights
            if config.led_btns:
                btn_leds[btn_event.key_number].value = False
            else:
                pixel_buf[btn_event.key_number] = config.pixel_colors[
                    btn_event.key_number
                ]
            # Mark button as not pressed
            if "gamepad" in locals():
                gpd_array[config.report_btn_id[btn_event.key_number] - 1] = 0
            else:
                keyboard_report[btn_event.key_number + 2] = 0x00

    # Send HID reports
    if "gamepad" in locals():
        # First byte buttons 1-8
        gamepad_report[0] = int("".join(str(x) for x in reversed(gpd_array[0:7])), 2)
        # Buttons 9-16
        gamepad_report[1] = int("".join(str(x) for x in reversed(gpd_array[8:15])), 2)
        # VOL-L is X
        gamepad_report[2] = int(prev_enc_pos[0] * (255 / 24))
        # VOL-R is Y
        gamepad_report[3] = int(prev_enc_pos[1] * (255 / 24))
        gamepad.send_report(gamepad_report)
    else:
        keyboard.send_report(keyboard_report)
        mouse.send_report(mouse_report)
