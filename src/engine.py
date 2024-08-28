import glob
import importlib
import json
import logging
from enum import Enum
from pathlib import Path

import yaml

from src.gui import GuiApplication
from src.logging_config import setup_logging
from src.plugins.base import IPlugin


class LogLevel(Enum):
    DEVELOPMENT = 4
    STAGING = 15
    PRODUCTION = 30


class Environment:
    """
    The Environment class.

    This class is responsible for setting up the environment for the application. It loads the plugins and configuration
    and provides access to them.

    Attributes:
        LOG_LEVEL (LogLevel): The log level for the environment.
        logger (logging.Logger): The logger for the environment.
        plugins (list): The list of plugins.
        config (dict): The configuration data.
    """
    LOG_LEVEL = logging.INFO

    def __init__(self):
        """
        Initialize the environment.

        This method sets up the logging and loads the plugins and configuration.
        """
        setup_logging()

        self.logger = logging.getLogger("app")
        self.logger.setLevel(self.LOG_LEVEL)
        self.plugins = self.__load_plugins()
        self.config = self.__load_config()

    def get(self, key, default=None):
        """
        Get a value from the config.

        Args:
            key (str): The key to get from the config.
            default: The default value to return if the key is not found.

        Returns:
            The value from the config, or the default value if the key is not found.
        """
        return self.config.get(key, default)

    def __load_config(self):
        """
        Load the configuration from the config folder.

        This method loads all the configuration files from the config folder and merges them into a single dictionary.

        Returns:
            dict: The configuration data.
        """
        config_folder_path = Path(__file__).parent.parent / "config"
        self.logger.debug(f"Loading config from {config_folder_path.absolute()}")

        config = {}
        for file_path in glob.glob(str(config_folder_path.absolute()) + "/*"):
            self.logger.debug2(f"Looking for config in {file_path}")
            with open(file_path, "r") as file:
                config.update(self.__load_file(file, file_path))

        self.logger.info(f"Loaded {len(str(config))} bytes of data into config.")
        self.logger.trace(f"Loaded config: {config}")
        return config

    def __load_file(self, file, file_path):
        """
        Load a configuration file.

        This method loads a configuration file based on the file extension.

        Args:
            file: The file object to load.
            file_path: The path to the file.

        Returns:
            dict: The configuration data from the file.
        """
        if Path(file_path).suffix == ".yaml":
            return yaml.safe_load(file)
        elif Path(file_path).suffix == ".json":
            return json.load(file)
        return {}

    def __load_plugins(self):
        """
        Load the plugins from the plugins folder.

        This method loads all the plugins from the plugins folder and returns them as a list.

        Returns:
            list: The list of plugins.
        """
        plugins = []
        plugins_folder = Path(__file__).parent.parent / "plugins"
        self.logger.debug(f"Loading plugins from {plugins_folder}")
        for plugin in glob.glob(f"{plugins_folder}/*"):
            plugin = Path(plugin)
            self.logger.debug2(f"Checking plugin: {plugin}")
            if plugin.is_dir() and not plugin.stem.startswith("_"):
                self.logger.debug(f"Loading plugin: {plugin}")
                module = importlib.import_module("plugins."+plugin.stem)
                name = plugin.stem.title().replace("_", "")
                obj = getattr(module, name)
                if isinstance(obj, type):
                    plugins.append(obj())

        return plugins

    def reload_plugins(self):
        """
        Reload the plugins.

        This method reloads the plugins from the plugins folder and updates the plugins list.

        Returns:
            list: The list of plugins
        """
        self.logger.debug("Reloading plugins")
        self.plugins = self.__load_plugins()
        return self.plugins

    def __setitem__(self, key, value):
        self.config[key] = value

    def __getitem__(self, key):
        return self.config[key]


class DevelopmentEnvironment(Environment):
    LOG_LEVEL = LogLevel.DEVELOPMENT.value

    def __init__(self):
        super().__init__()
        self.logger.debug("Development environment loaded")


class StagingEnvironment(Environment):
    LOG_LEVEL = LogLevel.STAGING.value

    def __init__(self):
        super().__init__()
        self.logger.debug("Staging environment loaded")


class ProductionEnvironment(Environment):
    LOG_LEVEL = LogLevel.PRODUCTION.value

    def __init__(self):
        super().__init__()
        self.logger.debug("Production environment loaded")


def create_app(application_mode: str = "development") -> GuiApplication:
    """
    Create the application.

    This method creates the application based on the application mode. The application mode determines the environment
    that the application runs in.

    Args:
        application_mode (str): The application mode. One of "development", "staging", or "production".

    Returns:
        GuiApplication: The application instance.
    """
    if application_mode == "development":
        return GuiApplication(DevelopmentEnvironment())
    elif application_mode == "staging":
        return GuiApplication(StagingEnvironment())
    elif application_mode == "production":
        return GuiApplication(ProductionEnvironment())
