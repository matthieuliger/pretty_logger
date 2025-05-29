import logging
from typing import Optional, Union, Tuple, Type
from pathlib import Path
from typing import Optional
from types import TracebackType

level_styles: dict[str, dict[str, str | bool | int]]
LOG_PATH: Path
LOG_FILE: Path
FORMAT_FIELDS: dict[str, dict[str, str | int]]
FORMAT_STRING: str

class EnsureClassName(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool: ...

class WrappedColoredFormatter(logging.Formatter):
    def __init__(
        self, base_formatter: logging.Formatter, width: int = 240
    ) -> None: ...
    def format(self, record: logging.LogRecord) -> str: ...

from typing import Any, Optional
import logging

from typing import Optional, Mapping, Union
import logging

ExcInfoType = Union[
    bool,
    BaseException,
    Tuple[Type[BaseException], BaseException, Optional[TracebackType]],
    Tuple[None, None, None],
    None,
]

class ClassLogger(logging.Logger):
    EMPTY_CLASS: str

    def _log(
        self,
        level: int,
        msg: object,
        args: Union[tuple[object, ...], Mapping[str, object]],
        exc_info: ExcInfoType = None,
        extra: Mapping[str, object] | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
    ) -> None: ...

def get_git_root() -> Optional[str]: ...
def configure_logging(
    level: int = logging.DEBUG,
    log_file: Path = LOG_FILE,
    console: bool = True,
    width: int = 240,
) -> None: ...
def get_module_logger(
    name: str, level: int = logging.DEBUG
) -> logging.Logger: ...
