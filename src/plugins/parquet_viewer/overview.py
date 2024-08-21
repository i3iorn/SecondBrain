import wx


class Overview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

        self.__base_info = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_NO_VSCROLL)
        self.__sizer.Add(self.__base_info, 1, wx.EXPAND)

    def update(self, plugin):
        self.__base_info.Clear()
        self.__base_info.AppendText(f"Total Rows: {plugin.get_total_rows()}\n")
        self.__base_info.AppendText(f"Total Columns: {len(plugin.get_relation().columns)}\n")

        for i, column in enumerate(plugin.get_relation().columns):
            self.__base_info.AppendText(f"{i + 1}. {column}\n")

        self.__base_info.AppendText("\n")

        self.Layout()
        self.Refresh()
