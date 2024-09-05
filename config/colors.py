WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)
PURPLE = (128, 0, 128)
MAROON = (128, 0, 0)
OLIVE = (128, 128, 0)
TEAL = (0, 128, 128)
NAVY = (0, 0, 128)
SKY_BLUE = (135, 206, 235)
VIOLET = (238, 130, 238)
TURQUOISE = (64, 224, 208)

LIGHTER_BLUE = (173, 216, 230)

"""
######################################
############# DNB COLORS #############
######################################
"""

# Primary Palette
PRIMARY_PALETTE = {
    "DARK_BLUE": (0, 81, 114),
    "LIGHT_BLUE": (48, 149, 180),
    "GRAY": (164, 169, 173),
    "BLACK": (16, 24, 32),
}

# Primary UI Palette
PRIMARY_UI_PALETTE = {
    "DARK_BLUE": (0, 81, 114),
    "LIGHT_BLUE": (48, 149, 180),
    "LIGHTER_GRAY": (247, 247, 247),
    "LIGHT_GRAY": (214, 214, 214),
    "GRAY": (134, 134, 134),
    "BLACK": (0, 0, 0),
}

# Secondary Palette
# Secondary colors add depth and variety to our brand.
# The primary palette has been expanded to include the use of both active and neutral colors that complement each
# other. A set of tonally darker and lighter colors has been developed in order to support the two primary colors.
# These 12 secondary colors are set in complementary pairs of tone and are designed to work with the primary colors in
# various combinations.
SECONDARY_PALETTE = {
    "LIGHT_VIOLET": (198, 87, 154),
    "DARK_VIOLET": (137, 59, 103),
    "LIGHT_PINK": (210, 91, 115),
    "DARK_PINK": (155, 50, 89),
    "LIGHT_PURPLE": (160, 94, 181),
    "DARK_PURPLE": (100, 47, 108),
    "LIGHT_TEAL": (0, 178, 169),
    "DARK_TEAL": (0, 95, 97),
    "LIGHT_GREEN": (116, 170, 80),
    "DARK_GREEN": (4, 106, 56),
    "LIGHT_ORANGE": (230, 166, 93),
    "DARK_ORANGE": (190, 77, 0),
}

# PLUGIN COLORS
HOVER_COLOR = LIGHTER_BLUE
WINDOW_BACKGROUND = PRIMARY_UI_PALETTE["DARK_BLUE"]

COMPONENT_BACKGROUND = WHITE
COMPONENT_FOREGROUND = PRIMARY_UI_PALETTE["BLACK"]

BUTTON_BACKGROUND = PRIMARY_UI_PALETTE["LIGHT_BLUE"]
BUTTON_FOREGROUND = WHITE
BUTTON_BACKGROUND_HOVER = HOVER_COLOR
BUTTON_FOREGROUND_HOVER = PRIMARY_UI_PALETTE["BLACK"]
BUTTON_BACKGROUND_CLICK = SECONDARY_PALETTE["DARK_TEAL"]
BUTTON_FOREGROUND_CLICK = WHITE
BUTTON_BACKGROUND_DISABLED = PRIMARY_UI_PALETTE["LIGHTER_GRAY"]
BUTTON_FOREGROUND_DISABLED = PRIMARY_UI_PALETTE["GRAY"]

TEXTBOX_BACKGROUND = WHITE
TEXTBOX_FOREGROUND = PRIMARY_UI_PALETTE["BLACK"]
TEXTBOX_BACKGROUND_HOVER = HOVER_COLOR
