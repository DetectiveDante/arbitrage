import logging


class LogFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', *,
                 extra_arg_name: str,
                 extra_arg_value: str):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)  # standard init :contentReference[oaicite:2]{index=2}
        self.extra_arg_name = extra_arg_name
        self.extra_arg_value = extra_arg_value

    def format(self, record: logging.LogRecord) -> str:
        # Inject extra field before formatting
        setattr(record, self.extra_arg_name, self.extra_arg_value)
        return super().format(record)  # calls Formatter.format(record) :contentReference[oaicite:3]{index=3}


def get_logger(name: str) -> logging.Logger:
    """Factory that returns a configured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "[%(asctime)s] %(levelname)s %(name)s: %(message)s (req=%(request_id)s)"
        handler.setFormatter(LogFormatter(fmt=fmt,
                                          datefmt="%H:%M:%S",
                                          extra_arg_name="request_id",
                                          extra_arg_value="unknown"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger
    


class Log:
    def __init__(self, name):
        self.log =          logging.getLogger(name)
        console_handler =   logging.StreamHandler()
        formatter = LogFormatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(title)s - %(message)s",
            datefmt=None,
            extra_arg_name="title",
            extra_arg_value=""
        )
        console_handler.setFormatter(formatter)

        self.log.addHandler(console_handler)
        self.log.setLevel(logging.INFO)

    def n(self, msg: str = '', title: str = '', lvl: str = 'info'):
        extra = {'title': title} if title else {}
        
        if lvl == 'info':
            # Pass extra as a keyword
            self.log.info(msg, extra=extra)
        elif lvl == 'error':
            self.log.error(msg, extra=extra)
        else:
            # Fallback to info if unknown level
            self.log.log(logging.INFO, msg, extra=extra)

def log(name, title, level, msg):
    log = get_logger(name)
    extra = {}
    if title:
        extra.update(title=title)

    match level:
        case 'info':
            log.info(msg, extra)
        case 'error':
            log.error(msg, extra)


