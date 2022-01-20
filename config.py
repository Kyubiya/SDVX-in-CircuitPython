import board

#
# Controller config
#

# Encoder ppr
enc_ppr = 24

# Encoder pins
# Swap A and B to reverse. Ex. GP1 to A, and GP0 to B
enc_pins = (
    board.GP0,  # VOL-L A
    board.GP1,  # VOL-L B
    board.GP2,  # VOL-R A
    board.GP3,  # VOL-R B
)

# Button pins, in the order of aRGB leds
# Max number of button inputs is 16
btn_pins = (
    board.GP4,   # BT-A
    board.GP6,   # BT-B
    board.GP8,   # BT-C
    board.GP10,  # BT-D
    board.GP12,  # FX-L
    board.GP14,  # FX-R
    board.GP20,  # BT-ST
)

# Are the buttons LED or WS2812B?
led_btns = True

# LED pins
# Match btn_pins order
led_pins = (
    board.GP5,   # BT-A
    board.GP7,   # BT-B
    board.GP9,   # BT-C
    board.GP11,  # BT-D
    board.GP13,  # FX-L
    board.GP15,  # FX-R
    board.GP21,  # BT-ST
)

# WS2812b pin
pixel_pin = board.GP28

pixel_count = 10

# Brightness between 0.0 - 1.0
pixel_brightness = 0.25

# Colors in (R, G, B) max 255
# Match btn_pins order + VOL-L + VOL-R
pixel_colors = (
    (64, 64, 255),  # BT-A
    (64, 64, 255),  # BT-B
    (64, 64, 255),  # BT-C
    (64, 64, 255),  # BT-D
    (255, 0, 0),    # FX-L
    (255, 0, 0),    # FX-R
    (0, 0, 255),    # BT-ST
    (16, 8, 255),   # VOL-L
    (255, 8, 16),   # VOL-R
)

pixel_off = (0, 0, 0)

# Gamepad report button number (1-16)
# Match btn_pins order
report_btn_id = (
    1,  # BT-A
    2,  # BT-B
    3,  # BT-C
    4,  # BT-D
    5,  # FX-L
    6,  # FX-R
    9,  # BT-ST
)

# Keybinds
# Match btn_pins order
report_keybind = (
    0x07,  # BT-A = D
    0x09,  # BT-B = F
    0x0D,  # BT-C = J
    0x0E,  # BT-D = K
    0x06,  # FX-L = C
    0x10,  # FX-R = M
    0x1E,  # BT-ST = 1
)

# Keybinds for VOL-L and VOL-R
enc_keybind = (
    0x4f,   # VOL-L+ = Right
    0x50,   # VOL-L- = Left
    0x51,   # VOL-R+ = Down
    0x52    # VOL-R- = Up
)

# Mouse speed multiplier
mouse_speed = 5
