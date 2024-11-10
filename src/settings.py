import os
import json
from logging.config import dictConfig
import logging
from typing import Any


LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "app": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
    },
}
dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("app")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_config(config_file=""):
    try:
        with open(config_file, "r") as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        logger.warning(
            "Archivo de configuración no encontrado. Usando valores predeterminados."
        )
        return {}


# settings = load_config()
settings = {
  "check_folder_interval_seconds": 10,
  "file_types_to_monitor": [".mp4", ".png", ".jpg", ".jpeg", ".txt"],
}
