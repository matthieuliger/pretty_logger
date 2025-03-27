import logging
import coloredlogs  # type: ignore
from pathlib import Path
import subprocess
import textwrap

format_dictionary = {
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


def get_git_root():
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


def get_logger(
    level=logging.DEBUG,
    name="logger",
    full_path="logger.log",
    add_console_hander: bool = False,
):
    logging.setLoggerClass(ClassLogger)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    format_string = (
        "[%(asctime)s.%(msecs)03d] - %(name)s"
        "- %(levelname)s %(className)s"
        "- %(filename)s: %(lineno)d [%(funcName)s]: %(message)s"
    )
    if Path(path).exists():
        Path(path).unlink()

    if not Path(path).parent.exists():
        Path(path).parent.mkdir()

    file_handler = logging.FileHandler(path, mode="w")
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    colored_formatter = coloredlogs.ColoredFormatter(
        fmt=format_string,
        level_styles=dict(
            debug=dict(color="white", faint=True),
            info=dict(color=222),
            warning=dict(color="magenta", bright=True),
            error=dict(color="red", bold=True, bright=False),
            critical=dict(color="black", bold=True, background="red"),
        ),
        field_styles=format_dictionary,
    )

    wrapped_colored_formatter = WrappedColoredFormatter(colored_formatter)
    file_handler.setFormatter(wrapped_colored_formatter)
    handlers = []
    handlers += [file_handler]

    if add_console_hander:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(wrapped_colored_formatter)
        handlers += [console_handler]  # type: ignore
        logger.addHandler(console_handler)

    coloredlogs.install(logger=logger, handlers=handlers, milliseconds=True)

    logger.propagate = False
    return logger


class WrappedColoredFormatter(logging.Formatter):
    def __init__(self, colored_formatter, width=240):
        self.colored_formatter = colored_formatter
        self.width = width

    def format(self, record):
        original = self.colored_formatter.format(record)
        return "\n".join(textwrap.wrap(original, self.width))


class ClassLogger(logging.Logger):
    EMPTY_CLASS = "N/A"

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def _log(self, *args, **kwargs):
        if len(args) >= 2:
            if len(args[2]) != 0:
                # kwargs['extra'] = {'className': }
                kwargs["extra"] = {"className": args[2][0].__class__.__name__}
                args = (args[0], args[1], ())

            else:
                kwargs["extra"] = {"className": ClassLogger.EMPTY_CLASS}
        super()._log(*args, stacklevel=2, **kwargs)
        pass
