import wx

from config.colors import *
from .mixins import SetFontMixin


class BasePanel(SetFontMixin, wx.Panel):
    def __init__(self, parent: wx.Panel) -> None:
        super().__init__(parent)
        self.parent_sizer = parent.GetSizer().GetItem(0).GetSizer()
        self.parent_sizer.Add(self, 1, wx.EXPAND)

        self.SetForegroundColour(COMPONENT_FOREGROUND)

        self.set_font()

        self.__outer_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__outer_sizer)

    @property
    def outer_sizer(self):
        return self.__outer_sizer
