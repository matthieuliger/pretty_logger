import logging
import textwrap
import time
from pathlib import Path
from typing import Optional, Union

import coloredlogs  # type: ignore

level_styles = {
    "debug": {"color": "white", "faint": True},
    "info": {"color": 222},
    "warning": {"color": "magenta", "bright": True},
    "error": {"color": "red", "bold": True},
    "critical": {"color": "black", "bold": True, "background": "red"},
}

DEFAULT_LOG_DIR = Path("logs")

FORMAT_FIELDS = {
    "name": {"color": "green"},
    "levelname": {"color": "green"},
    "lineno": {"color": "magenta"},
    "asctime": {"color": 192},
    "msecs": {"color": "yellow"},
    "message": {"color": "green"},
    "funcName": {"color": "white"},
    "filename": {"color": "blue"},
}

FORMAT_STRING = (
    "[%(asctime)s.%(msecs)03d] - %(name)s - "
    "%(levelname)s - %(filename)s:%(lineno)d [%(funcName)s]: %(message)s"
)

DEFAULT_SILENCED_MODULES = [
    "pymongo",
    "motor",
    "httpcore",
    "httpx",
    "pdfminer",
    "openai",
    "python_multipart",
]


class WrappedColoredFormatter(logging.Formatter):
    def __init__(self, base_formatter: coloredlogs.ColoredFormatter, width: int = 240):
        self.base_formatter = base_formatter
        self.width = width

    def format(self, record: logging.LogRecord) -> str:
        base_output = self.base_formatter.format(record)
        wrapped = []
        for line in base_output.splitlines():
            if not line.strip():
                wrapped.append("")
            else:
                wrapped.extend(textwrap.wrap(line, self.width))
        return "\n".join(wrapped)


def _make_formatter(width: int) -> WrappedColoredFormatter:
    base = coloredlogs.ColoredFormatter(
        fmt=FORMAT_STRING,
        level_styles=level_styles,
        field_styles=FORMAT_FIELDS,
    )
    base.converter = time.gmtime
    return WrappedColoredFormatter(base, width=width)


def configure_pretty_logging(
    level: Union[str, int] = logging.DEBUG,
    log_dir: Union[str, Path] = DEFAULT_LOG_DIR,
    log_name: str = "pretty_logger",
    console: bool = True,
    width: int = 150,
    silenced_modules: Optional[list[str]] = None,
) -> None:
    if silenced_modules is None:
        silenced_modules = DEFAULT_SILENCED_MODULES

    log_dir = Path(log_dir)

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.DEBUG)
    if not isinstance(level, int):
        raise ValueError(f"Invalid logging level: {level}. Must be str or int.")

    root_logger = logging.getLogger()

    # Prevent duplicate handlers
    if root_logger.handlers:
        root_logger.warning("Root logger already has handlers.")
        return

    log_dir.mkdir(parents=True, exist_ok=True)
    root_logger.setLevel(level)

    formatter = _make_formatter(width)

    file_handler = logging.FileHandler(log_dir / f"{log_name}.log", mode="w")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    root_logger.propagate = False

    for module in silenced_modules:
        logging.getLogger(module).setLevel(logging.CRITICAL + 1)


def get_module_logger(
    name: str,
    level: Union[str, int] = logging.DEBUG,
    width: int = 120,
    log_dir: Union[str, Path] = DEFAULT_LOG_DIR,
    console: bool = False,
    mode: str = "w",
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Always propagate so logs reach the root logger's big file + console
    logger.propagate = True

    # Only add the per-module file handler once
    if not logger.handlers:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        module_name = name.split(".")[-1]

        file_handler = logging.FileHandler(log_dir / f"{module_name}.log", mode=mode)
        file_handler.setLevel(level)
        file_handler.setFormatter(_make_formatter(width))
        logger.addHandler(file_handler)

        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(_make_formatter(width))
            logger.addHandler(console_handler)

    return logger
