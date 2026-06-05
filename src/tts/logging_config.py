import logging.config


def set_logging_config():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "stdout": {
                "class": logging.StreamHandler,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "__main__": {"level": logging.DEBUG},
            # "kokoro": {"level": logging.DEBUG},
            "tts": {"level": logging.DEBUG},
        },
        "root": {
            "level": logging.WARNING,
            "handlers": ["stdout"],
        },
    }
    logging.config.dictConfig(config)
