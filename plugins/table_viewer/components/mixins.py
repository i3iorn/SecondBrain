import wx


class SetFontMixin:
    def set_font(self, font_size: int = 10, font_name: str = "Avenir") -> None:
        font = wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, font_name)
        self.SetFont(font)
