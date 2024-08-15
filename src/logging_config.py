import logging
import logging.handlers


def add_log_level(level_name, level_num):
    level_name = level_name.upper()
    logging.addLevelName(level_num, level_name)

    def log_method(self, message, *args, **kws):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kws)

    setattr(logging.Logger, level_name.lower(), log_method)


colors = {
    "TRACE": "\033[94m",
    "DEBUG3": "\033[94m",
    "DEBUG2": "\033[96m",
    "DEBUG": "\033[96m",
    "VERBOSE": "\033[92m",
    "INFO": "\033[92m",
    "NOTICE": "\033[93m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[91m",
    "ENDC": "\033[0m",
}


class CustomStreamFormatter(logging.Formatter):
    _fmt = "%(levelname)s - %(message)s"

    def __init__(self):
        super().__init__(fmt=self._fmt)

    def format(self, record):
        levelname = record.levelname
        if levelname in colors:
            levelname_color = f"{colors[levelname]}{levelname}{colors['ENDC']}"
            record.levelname = levelname_color
        return super().format(record)


class CustomFileFormatter(logging.Formatter):
    _fmt = "%(asctime)s - %(levelname)s - %(message)s"

    def __init__(self):
        super().__init__(fmt=self._fmt)


class CustomFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, mode="a", maxBytes=0, backupCount=0, encoding=None, delay=0):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.setFormatter(CustomFileFormatter())
        if self.level < 15:
            self.setLevel(15)


class CustomStreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.setFormatter(CustomStreamFormatter())


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.propagate = False
        self.addHandler(CustomFileHandler(f"{name}.log"))
        self.addHandler(CustomStreamHandler())


def setup_logging():
    custom_log_levels = {
        "TRACE": 4,
        "DEBUG3": 6,
        "DEBUG2": 8,
        "VERBOSE": 15,
        "NOTICE": 25,
    }

    for level_name, level_num in custom_log_levels.items():
        add_log_level(level_name, level_num)

    logging.setLoggerClass(CustomLogger)
    logging.basicConfig(level=logging.WARNING)

    logging.getLogger("app").setLevel(1)

    logging.getLogger("app").trace("Trace message")
    logging.getLogger("app").debug3("Debug3 message")
    logging.getLogger("app").debug2("Debug2 message")
    logging.getLogger("app").debug("Debug message")
    logging.getLogger("app").verbose("Verbose message")
    logging.getLogger("app").info("Info message")
    logging.getLogger("app").notice("Notice message")
    logging.getLogger("app").warning("Warning message")
    logging.getLogger("app").error("Error message")
    logging.getLogger("app").critical("Critical message")

    logging.getLogger("app").setLevel(30)
