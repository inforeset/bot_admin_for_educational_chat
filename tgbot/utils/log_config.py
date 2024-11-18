import logging.config


dictLogConfig = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "fileDebug": {
            "class": "logging.handlers.RotatingFileHandler",
            "mode": "a",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 0,
            "delay": False,
            "formatter": "myFormatter",
            "level": "DEBUG",
            "filename": "logs/debug.log",
            "encoding": "utf-8"
        },
        "fileWarning": {
            "class": "logging.handlers.RotatingFileHandler",
            "mode": "a",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 0,
            "delay": False,
            "formatter": "myFormatter",
            "level": "WARNING",
            "filename": "logs/error.log",
            "encoding": "utf-8"
        },
        "stream": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "myFormatter",
            "stream": "ext://sys.stdout",
        },

    },
    "loggers": {
        'root': {
            "handlers": [
                "fileDebug",
                "fileWarning",
                "stream",
            ],
            "level": "DEBUG",
        },
    },
    "formatters": {
        "myFormatter": {
            "format": "%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
            "datefmt": '%d-%m-%Y %H:%M:%S'
        },
    }
}


logger = logging.getLogger('root')
logging.config.dictConfig(dictLogConfig)