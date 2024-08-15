import glob
import json
import yaml
import logging
import importlib
from pathlib import Path

from gui import GuiApplication
from src.logging_config import setup_logging
from src.plugins.base import IPlugin


class Environment:
    LOG_LEVEL = logging.INFO

    def __init__(self):
        setup_logging()

        self.logger = logging.getLogger("app")
        self.logger.setLevel(self.LOG_LEVEL)
        self.plugins = self.__load_plugins()
        self.config = self.__load_config()

    def get(self, key, default=None):
        return self.config.get(key, default)

    def __load_config(self):
        config_folder_path = Path(__file__).parent / "config"
        self.logger.debug(f"Loading config from {config_folder_path}")

        config = {}
        for file_path in glob.glob(str(config_folder_path.absolute()) + "/*"):
            self.logger.debug2(f"Looking for config in {file_path}")
            if Path(file_path).suffix == ".yaml":
                self.logger.debug(f"Loading config from {file_path}")
                with open(file_path, "r") as file:
                    config.update(yaml.safe_load(file))
            elif Path(file_path).suffix == ".json":
                self.logger.debug(f"Loading config from {file_path}")
                with open(file_path, "r") as file:
                    config.update(json.load(file))

        self.logger.info(f"Loaded {len(str(config))} bytes of data into config.")
        self.logger.trace(f"Loaded config: {config}")
        return config

    def __load_plugins(self):
        plugins = []

        folder_path = Path(__file__).parent / "plugins"
        self.logger.debug(f"Loading plugins from {folder_path}")

        for file_path in glob.glob(str(folder_path / "*.py")):
            self.logger.debug2(f"Loading plugin from {file_path}")

            module_name = Path(file_path).stem
            if module_name == "__init__" or module_name == "base":
                continue
            module = importlib.import_module(f"src.plugins.{module_name}")
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, IPlugin) and obj != IPlugin:
                    self.logger.debug2(f"Found plugin class {obj}")
                    plugins.append(obj())

        self.logger.verbose(f"Loaded {len(plugins)} plugins")
        return plugins

    def __setitem__(self, key, value):
        self.config[key] = value

    def __getitem__(self, key):
        return self.config[key]


class DevelopmentEnvironment(Environment):
    LOG_LEVEL = 4

    def __init__(self):
        super().__init__()
        self.logger.debug("Development environment loaded")


class StagingEnvironment(Environment):
    LOG_LEVEL = 15

    def __init__(self):
        super().__init__()
        self.logger.debug("Staging environment loaded")


class ProductionEnvironment(Environment):
    LOG_LEVEL = 30

    def __init__(self):
        super().__init__()
        self.logger.debug("Production environment loaded")


def create_app(application_mode: str) -> GuiApplication:
    if application_mode == "development":
        return GuiApplication(DevelopmentEnvironment())
