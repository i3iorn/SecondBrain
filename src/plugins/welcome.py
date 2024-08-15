import wx

from src.plugins.base import IPlugin


class Welcome(IPlugin):
    @property
    def name(self):
        return "Welcome"

    def run(self, event, environment):
        raise NotImplementedError("This plugin is not implemented yet.")
