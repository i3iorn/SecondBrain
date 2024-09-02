import wx


class TVTextCntrl(wx.TextCtrl):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, style=wx.BORDER_SIMPLE | wx.TE_CENTER | wx.TE_PROCESS_ENTER)
        self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        self.parent_sizer = parent.GetSizer()
        self.parent_sizer.Add(self, 1, wx.EXPAND)
