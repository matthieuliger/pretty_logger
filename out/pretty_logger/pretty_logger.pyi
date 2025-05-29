import logging
from pathlib import Path
from types import TracebackType

level_styles: dict[str, dict[str, str | bool | int]]
LOG_PATH: Path
LOG_FILE: Path
FORMAT_FIELDS: dict[str, dict[str, str | int]]
FORMAT_STRING: str

class EnsureClassName(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool: ...

class WrappedColoredFormatter(logging.Formatter):
    def __init__(self, base_formatter: logging.Formatter, width: int = 240) -> None: ...
    def format(self, record: logging.LogRecord) -> str: ...
ExcInfoType = bool | BaseException | tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None] | None

class ClassLogger(logging.Logger):
    EMPTY_CLASS: str

def get_git_root() -> str | None: ...
def configure_logging(level: int = ..., log_file: Path = ..., console: bool = True, width: int = 240) -> None: ...
def get_module_logger(name: str, level: int = ...) -> logging.Logger: ...
