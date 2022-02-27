import board

#
#   REFERENCE SECTION
#   DO NOT CHANGE
#

# Keybinds reference
# Check https://deskthority.net/wiki/Scancode for more
(KEY_A, KEY_B, KEY_C, KEY_D, KEY_E, KEY_F, KEY_G, KEY_H, KEY_I, KEY_J, KEY_K, KEY_L,
 KEY_M, KEY_N, KEY_O, KEY_P, KEY_Q, KEY_R, KEY_S, KEY_T, KEY_U, KEY_V, KEY_W, KEY_X,
 KEY_Y, KEY_Z, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0,
 KEY_ENT, KEY_ESC, KEY_BAC, KEY_TAB, KEY_SPA, KEY_MIN, KEY_PLU, KEY_LBR, KEY_RBR,
 KEY_FSL, KEY_POU, KEY_COL, KEY_APO, KEY_TIL, KEY_COM, KEY_PER, KEY_QUE, KEY_CAP,
 KEY_F1, KEY_F2, KEY_F3, KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8, KEY_F9, KEY_F10,
 KEY_F11, KEY_F12, KEY_PRT, KEY_SCR, KEY_PAU, KEY_INS, KEY_HOM, KEY_PGU, KEY_DEL,
 KEY_END, KEY_PGD, KEY_RIG, KEY_LEF, KEY_DOW, KEY_UP) = range(4, 83)

#
#   END REFERENCE SECTION
#

#
# CONTROLLER CONFIG
# Edit variables below
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

# Encoder WS2812b address
enc_addr = (7, 8) # VOL-L, VOL-R

# Encoder WS2812b colors
# (Red, Green, Blue)
# Range 0-255
enc_colors = (
    (16, 8, 255),   # VOL-L On
    (255, 8, 16),   # VOL-R On
    (0, 0, 0),      # VOL-L Off
    (0, 0, 0),      # VOL-R Off
    )

# Keybinds for VOL-L and VOL-R
enc_keybind = (
    KEY_RIG,   # VOL-L+ = Right Arrow
    KEY_UP,   # VOL-R+ = Up Arrow
    KEY_LEF,   # VOL-L- = Left Arrow
    KEY_DOW,   # VOL-R- = Down Arrow
)

# Button maps
# Max number of button inputs is 16
# (GPIO pin, Gamepad ID, key code, LED pin, WS2812b address, pressed color, released color
#  0         1           2         3        4                5              6
# Gamepad ID as reported in Windows, starts at 1
# GPIO and gamepad ID are required sections
# Use None for unused LED pin, WS2812b address, key code, colors
# If WS2812b address is set, you must have both colors set
# Colors are (Red, Green, Blue) range 0-255
btn_map = (
    (board.GP4, 1, KEY_D, board.GP5, 0, (0, 0, 0), (192, 192, 255)),         # BT-A  = D
    (board.GP6, 2, KEY_F, board.GP7, 1, (0, 0, 0), (192, 192, 255)),         # BT-B  = F
    (board.GP8, 3, KEY_J, board.GP9, 2, (0, 0, 0), (192, 192, 255)),         # BT-C  = J
    (board.GP10, 4, KEY_K, board.GP11, 3, (0, 0, 0), (192, 192, 255)),       # BT-D  = K
    (board.GP12, 5, KEY_C, board.GP13, 4, (0, 0, 0), (255, 0, 0)),           # FX-L  = C
    (board.GP14, 6, KEY_M, board.GP15, 5, (0, 0, 0), (255, 0, 0)),           # FX-R  = M
    (board.GP20, 9, KEY_1, board.GP21, 6, (0, 0, 0), (0, 0, 255)),           # BT-ST = 1
    (board.GP27, 7, KEY_BAC, None, None, None, None),                      # Extra = Backspace
)

# Are the buttons LED or WS2812B?
led_btns = True

# WS2812b pin
pixel_pin = board.GP28

pixel_count = 10

# Brightness between 0.0 - 1.0
pixel_brightness = 0.4

# Mouse speed multiplier
mouse_speed = 5
