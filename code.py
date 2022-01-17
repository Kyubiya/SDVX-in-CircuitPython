import adafruit_pixelbuf
import board
import digitalio
import keypad
import neopixel_write
import rotaryio
import time
import usb_hid

#
# Config variables
#

# Encoder ppr
enc_ppr = 24

# Encoder pins
enc_pins = (
    board.GP0,      # VOL_L A
    board.GP1,      # VOL_L B
    board.GP2,      # VOL_R A
    board.GP3       # VOL_R B
)

# Button pins, in the order of aRGB leds
btn_pins = (
    board.GP4,      # BT_A
    board.GP6,      # BT_B
    board.GP8,      # BT_C
    board.GP10,     # BT_D
    board.GP12,     # FX_L
    board.GP14,     # FX_R
    board.GP20      # BT_ST
)

# Are the buttons LED or WS2812B?
btn_type = "LED"

# LED pins
led_pins = (
    board.GP5,      # BT_A
    board.GP7,      # BT_B
    board.GP9,      # BT_C
    board.GP11,     # BT_D
    board.GP13,     # FX_L
    board.GP15,     # FX_R
    board.GP21      # BT_ST
)

# WS2812b pin
pixel_pin = board.GP28

pixel_count = 10

pixel_brightness = 1

# Colors
pixel_colors = (
    (64, 64, 255),  # BT_A
    (64, 64, 255),  # BT_B
    (64, 64, 255),  # BT_C
    (64, 64, 255),  # BT_D
    (255, 0, 0),    # FX_L
    (255, 0, 0),    # FX_R
    (0, 0, 255),    # BT_ST
    (16, 8, 255),   # VOL_L
    (255, 8, 16)    # VOL_R
)

pixel_off = (0, 0, 0)

# Gamepad report button number (1-16)
report_button_id = (
    1,  # BT_A
    2,  # BT_B
    3,  # BT_C
    4,  # BT_D
    5,  # FX_L
    6,  # FX_R
    9   # BT_ST
)

# Keybinds
report_keybind = (
    0x07,       # BT_A = D
    0x09,       # BT_B = F
    0x0D,       # BT_C = J
    0x0E,       # BT_D = K
    0x06,       # FX_L = C
    0x10,       # FX_R = M
    0x1E,       # BT_ST = 1
)

#
# End config variables
#

# Subclass to use built in pixel buffer
class pixelBuffer(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin: board.Pin, size, byteorder, brightness, auto_write):
        super().__init__(size=size, byteorder=byteorder, brightness=brightness, auto_write=auto_write)

        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT

    def _transmit(self, buffer: bytearray) -> None:
        neopixel_write.neopixel_write(self.pin, buffer)

pixel_buf = pixelBuffer(pixel_pin, pixel_count, byteorder="GRB", brightness=pixel_brightness, auto_write=True)

if btn_type == "LED":
    for x in pixel_buf:
        x = pixel_off
else:
    for x in range(len(pixel_colors)):
        pixel_buf[x] = pixel_colors[x]
    pixel_buf[-1] = pixel_off
    pixel_buf[-2] = pixel_off

# Set up LEDs
btn_leds = [digitalio.DigitalInOut(x)for x in led_pins]

for x in btn_leds:
    x.direction = digitalio.Direction.OUTPUT

# Set up inputs
buttons = keypad.Keys(btn_pins, value_when_pressed=False, pull=True)
button_event = keypad.Event()

gamepad_btn = [0] * 16

for x in usb_hid.devices:
    if x.usage == 5:
        gamepad = x

encoders = [
    rotaryio.IncrementalEncoder(enc_pins[0], enc_pins[1]),
    rotaryio.IncrementalEncoder(enc_pins[2], enc_pins[3])
]

prev_enc_pos = [encoders[0].position, encoders[1].position]
cur_pos = None
enc_led_pos = [0, 5]
if btn_type == "LED":
    for x in range(2):
        pixel_buf[enc_led_pos[x]] = pixel_colors[len(btn_pins)+x]

cur_time = time.monotonic()
enc_timeout = [cur_time, cur_time]

gamepad_report = bytearray(4)

# Main loop to poll inputs
while(True):
    for x in range(2):
        encoders[x].position %= enc_ppr
        cur_pos = encoders[x].position

        if prev_enc_pos[x] != cur_pos:
            if btn_type == "LED":
                enc_led_pos[x] = ((enc_led_pos[x] + (prev_enc_pos[x] - cur_pos)) % 5) + (x * 5)
                for y in range(x*5, (x*5)+5):
                    pixel_buf[y] = pixel_off
                pixel_buf[enc_led_pos[x]] = pixel_colors[len(btn_pins)+x]
            else:
                pixel_buf[len(btn_pins)+x] = pixel_colors[len(btn_pins)+x]
            prev_enc_pos[x] = cur_pos
        else:
            cur_time = time.monotonic()
            if (cur_time - enc_timeout[x]) > 0.5:
                if btn_type != "LED":
                    pixel_buf[len(btn_pins)+x] = pixel_off
                enc_timeout[x] = cur_time

    if buttons.events.get_into(button_event):
        if button_event.pressed:
            if btn_type == "LED":
                btn_leds[button_event.key_number].value = True
            else:
                pixel_buf[button_event.key_number] = pixel_off

            gamepad_btn[report_button_id[button_event.key_number]-1] = 1

        if button_event.released:
            if btn_type == "LED":
                btn_leds[button_event.key_number].value = False
            else:
                pixel_buf[button_event.key_number] = pixel_colors[button_event.key_number]

            gamepad_btn[report_button_id[button_event.key_number]-1] = 0

    gamepad_report[0] = int(''.join(str(x) for x in reversed(gamepad_btn[0:7])), 2)
    gamepad_report[1] = int(''.join(str(x) for x in reversed(gamepad_btn[8:15])), 2)
    gamepad_report[2] = int(prev_enc_pos[0] * (255 / 24))
    gamepad_report[3] = int(prev_enc_pos[1] * (255 / 24))

    gamepad.send_report(gamepad_report)
