# yellowkitten/custom_logger.py
import logging
import coloredlogs  # type: ignore
from pathlib import Path
import subprocess
import textwrap
import time
from typing import Optional

# yellowkitten/custom_logger.py
import logging
import coloredlogs  # type: ignore
from pathlib import Path
import subprocess
import textwrap
import time
from typing import Optional


level_styles = {
    "debug": {"color": "white", "faint": True},
    "info": {"color": 222},
    "warning": {"color": "magenta", "bright": True},
    "error": {"color": "red", "bold": True},
    "critical": {"color": "black", "bold": True, "background": "red"},
}

LOG_PATH = Path("logs")
LOG_FILE = LOG_PATH / "pretty_logger.log"

# Field styles
FORMAT_FIELDS = {
    "name": {"color": "green"},
    "levelname": {"color": "green"},
    "lineno": {"color": "magenta"},
    "asctime": {"color": 192},
    "msecs": {"color": "yellow"},
    "message": {"color": "green"},
    "funcName": {"color": "white"},
    "filename": {"color": "blue"},
    "className": {"color": "magenta"},
}

FORMAT_STRING = (
    "[%(asctime)s.%(msecs)03d] - %(name)s - %(levelname)s %(className)s "
    "- %(filename)s:%(lineno)d [%(funcName)s]: %(message)s"
)


class EnsureClassName(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "className"):
            record.className = "N/A"
        return True


class WrappedColoredFormatter(logging.Formatter):
    def __init__(self, base_formatter, width=240):
        self.base_formatter = base_formatter
        self.width = width

    def format(self, record):
        base_output = self.base_formatter.format(record)
        wrapped = []
        for line in base_output.splitlines():
            if not line.strip():
                wrapped.append("")
            else:
                wrapped.extend(textwrap.wrap(line, self.width))
        return "\n".join(wrapped)


class ClassLogger(logging.Logger):
    EMPTY_CLASS = "N/A"

    def _log(self, level, msg, args, **kwargs):
        if "extra" not in kwargs:
            className = self.EMPTY_CLASS
            if args and hasattr(args[0], "__class__"):
                className = args[0].__class__.__name__
            kwargs["extra"] = {"className": className}
        super()._log(level, msg, args, **kwargs)


def get_git_root() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def configure_pretty_logging(
    level=logging.DEBUG,
    log_file: Path = LOG_FILE,
    console: bool = True,
    width: int = 150,
    silenced_modules: list[str] = ["pymongo", "motor", "httpcore", "httpx"],
):
    if not log_file.parent.exists():
        log_file.parent.mkdir(parents=True)
    print(f"Configuring logging to {log_file}, level={level}, width={width}")

    logging.setLoggerClass(ClassLogger)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Prevent duplicate handlers
    if root_logger.handlers:
        root_logger.warning("Root logger already has handlers.")
        # return

    formatter = coloredlogs.ColoredFormatter(
        fmt=FORMAT_STRING,
        level_styles=level_styles,
        field_styles=FORMAT_FIELDS,
    )
    formatter.converter = time.gmtime
    wrapped_formatter = WrappedColoredFormatter(formatter, width=width)

    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(wrapped_formatter)
    root_logger.addHandler(file_handler)

    default_filter = EnsureClassName()
    file_handler.addFilter(default_filter)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(wrapped_formatter)
        console_handler.addFilter(default_filter)

        root_logger.addHandler(console_handler)

    coloredlogs.install(
        logger=root_logger, handlers=root_logger.handlers, milliseconds=True
    )
    root_logger.propagate = False
    for silenced_module in silenced_modules:
        logging.getLogger(silenced_module).setLevel(logging.CRITICAL + 1)


def get_module_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Only add handler once
    if not logger.handlers:
        module_name = name.split(".")[-1]
        module_log_path = LOG_PATH / f"{module_name}.log"
        file_handler = logging.FileHandler(module_log_path, mode="w")
        file_handler.setLevel(level)

        # Use the same formatter and filter
        base_formatter = coloredlogs.ColoredFormatter(
            fmt=FORMAT_STRING,
            level_styles=level_styles,
            field_styles=FORMAT_FIELDS,
        )
        wrapped_formatter = WrappedColoredFormatter(base_formatter)
        file_handler.setFormatter(wrapped_formatter)

        file_handler.addFilter(EnsureClassName())
        logger.addHandler(file_handler)

        # Important: do not propagate to root logger if you only want module-specific logging
        # But if you want *both*, leave propagate=True (default)
        logger.propagate = True  # ✅ Send log to root handlers too

    return logger
