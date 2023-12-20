import logging
import coloredlogs  # type: ignore

format_dictionary = {
    "name": {"color": "green"},
    "levelname": {"color": "green"},
    "lineno": {"color": "magenta"},
    "asctime": {"color": 192},
    "msecs": {"color": "yellow"},
    "message": {"color": "green"},
    "funcName": {"color": "white"},
    "filename": {"color": "blue"},
    "ClassName": {"color": "magenta"},
}


def get_logger(
    level=logging.DEBUG,
    name="logger",
    full_path="logger.log",
    add_console_hander: bool = True,
):
    logging.setLoggerClass(ClassLogger)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # adapter = CustomAdapter(logger, {'somextra': 'dummy'})

    format_string = (
        "[%(asctime)s.%(msecs)03d] - %(name)s"
        "- %(levelname)s %(className)s"
        "- %(filename)s: %(lineno)d [%(funcName)s]: %(message)s"
    )

    # plain_formatter = logging.Formatter(format_string)

    coloredlogs.install(logger=logger, milliseconds=True)
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

    console_handler = logger.handlers[0]
    file_handler = logging.FileHandler(full_path, mode="w")

    console_handler.setLevel(level)
    file_handler.setLevel(level)

    file_handler.setFormatter(colored_formatter)

    if add_console_hander:
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


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
