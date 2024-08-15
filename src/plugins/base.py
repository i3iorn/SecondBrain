from abc import ABC, abstractmethod


class IPlugin(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def run(self, event, engine):
        pass