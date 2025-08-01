# yellowkitten/custom_logger.py
import logging
import coloredlogs  # type: ignore
from pathlib import Path
import subprocess
import textwrap
import time
import inspect
from typing import Optional, Union

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

# FORMAT_STRING = (
#     "[%(asctime)s.%(msecs)03d] - %(name)s - %(levelname)s - "
#     "- %(filename)s:%(lineno)d [%(funcName)s]: %(message)s"
# )
FORMAT_STRING = (
    "[%(asctime)s.%(msecs)03d] - %(name)s - "
    "%(levelname)s - %(filename)s:%(lineno)d [%(funcName)s]: %(message)s"
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
    level: Union[str, int] = logging.DEBUG,
    log_file: Union[str, Path] = LOG_FILE,
    console: bool = True,
    width: int = 150,
    silenced_modules: list[str] = [
        "pymongo",
        "motor",
        "httpcore",
        "httpx",
        "pdfminer",
        "openai",
        "python_multipart",
    ],
):

    if isinstance(log_file, str):
        log_file = Path(log_file)
    if not log_file.suffix:
        log_file = log_file.with_suffix(".log")

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.DEBUG)
    if not isinstance(level, int):
        raise ValueError(f"Invalid logging level: {level}. Must be str or int.")

    if not log_file.parent.exists():
        log_file.parent.mkdir(parents=True)
    print(f"Configuring logging to {log_file}, level={level}, width={width}")

    # logging.setLoggerClass(ClassLogger)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Prevent duplicate handlers
    if root_logger.handlers:
        root_logger.warning("Root logger already has handlers.")
        return

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


def get_module_logger(
    name: str,
    level=logging.DEBUG,
    width: int = 120,
    mode: str = "a",
    console: bool = True,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Only add handler once
    if not logger.handlers:
        module_name = name.split(".")[-1]
        module_log_path = LOG_PATH / f"{module_name}.log"

        if not module_log_path.parent.exists():
            module_log_path.parent.mkdir(parents=True)

        file_handler = logging.FileHandler(module_log_path, mode=mode)
        file_handler.setLevel(level)

        # Use the same formatter and filter
        base_formatter = coloredlogs.ColoredFormatter(
            fmt=FORMAT_STRING,
            level_styles=level_styles,
            field_styles=FORMAT_FIELDS,
        )
        wrapped_formatter = WrappedColoredFormatter(base_formatter, width=width)
        file_handler.setFormatter(wrapped_formatter)

        file_handler.addFilter(EnsureClassName())
        logger.addHandler(file_handler)
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # We can reuse the same wrapped_formatter for console output,
            # or use a simpler coloredlogs formatter directly
            console_formatter = coloredlogs.ColoredFormatter(
                fmt=FORMAT_STRING,
                level_styles=level_styles,
                field_styles=FORMAT_FIELDS,
            )
            console_handler.setFormatter(console_formatter)
            console_handler.addFilter(EnsureClassName())
            logger.addHandler(console_handler)

        # Important: do not propagate to root logger if you only want module-specific logging
        # But if you want *both*, leave propagate=True (default)
        logger.propagate = True  # ✅ Send log to root handlers too

    return logger
