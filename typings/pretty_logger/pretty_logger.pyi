import logging
from _typeshed import Incomplete as Incomplete
from pathlib import Path

level_styles: Incomplete
LOG_PATH: Incomplete
LOG_FILE: Incomplete
FORMAT_FIELDS: Incomplete
FORMAT_STRING: str

class EnsureClassName(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool: ...

class WrappedColoredFormatter(logging.Formatter):
    base_formatter: Incomplete
    width: Incomplete
    def __init__(self, base_formatter, width: int = 240) -> None: ...
    def format(self, record) -> None: ...

class ClassLogger(logging.Logger):
    EMPTY_CLASS: str

def get_git_root() -> str | None: ...
def configure_pretty_logging(level: str | int = ..., log_file: str | Path = ..., console: bool = True, width: int = 150, silenced_modules: list[str] = ['pymongo', 'motor', 'httpcore', 'httpx']): ...
def get_module_logger(name: str, level=...) -> logging.Logger: ...
