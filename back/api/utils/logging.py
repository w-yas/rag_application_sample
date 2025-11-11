import logging
import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s%(reset)s: %(asctime)s %(name)s %(request_id)s %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bg_red",
            },
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "level": "INFO",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
logging.config.dictConfig(LOGGING)
logger = logging.getLogger("api_logger")
