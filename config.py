import board

#
# Controller config
#

# Encoder ppr
enc_ppr = 24

# Encoder pins
enc_pins = (
    board.GP0,  # VOL_L A
    board.GP1,  # VOL_L B
    board.GP2,  # VOL_R A
    board.GP3,  # VOL_R B
)

# Button pins, in the order of aRGB leds
btn_pins = (
    board.GP4,  # BT_A
    board.GP6,  # BT_B
    board.GP8,  # BT_C
    board.GP10,  # BT_D
    board.GP12,  # FX_L
    board.GP14,  # FX_R
    board.GP20,  # BT_ST
)

# Are the buttons LED or WS2812B?
led_btns = True

# LED pins
led_pins = (
    board.GP5,  # BT_A
    board.GP7,  # BT_B
    board.GP9,  # BT_C
    board.GP11,  # BT_D
    board.GP13,  # FX_L
    board.GP15,  # FX_R
    board.GP21,  # BT_ST
)

# WS2812b pin
pixel_pin = board.GP28

pixel_count = 10

pixel_brightness = 0.25

# Colors
pixel_colors = (
    (64, 64, 255),  # BT_A
    (64, 64, 255),  # BT_B
    (64, 64, 255),  # BT_C
    (64, 64, 255),  # BT_D
    (255, 0, 0),  # FX_L
    (255, 0, 0),  # FX_R
    (0, 0, 255),  # BT_ST
    (16, 8, 255),  # VOL_L
    (255, 8, 16),  # VOL_R
)

pixel_off = (0, 0, 0)

# Gamepad report button number (1-16)
report_btn_id = (
    1,  # BT_A
    2,  # BT_B
    3,  # BT_C
    4,  # BT_D
    5,  # FX_L
    6,  # FX_R
    9,  # BT_ST
)

# Keybinds
report_keybind = (
    0x07,  # BT_A = D
    0x09,  # BT_B = F
    0x0D,  # BT_C = J
    0x0E,  # BT_D = K
    0x06,  # FX_L = C
    0x10,  # FX_R = M
    0x1E,  # BT_ST = 1
)
