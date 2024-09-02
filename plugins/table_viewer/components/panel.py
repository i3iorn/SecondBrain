import wx

from config.colors import *
from .mixins import SetFontMixin


class BasePanel(SetFontMixin, wx.Panel):
    def __init__(self, parent: wx.Panel) -> None:
        super().__init__(parent)
        self.SetForegroundColour(COMPONENT_FOREGROUND)
        self.set_font()
