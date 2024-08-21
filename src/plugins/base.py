from abc import ABC, abstractmethod


class IPlugin(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def run(self, engine):
        pass

    @abstractmethod
    def stop(self):
        pass