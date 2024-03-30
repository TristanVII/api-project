import logging
import logging.config
import yaml
import os


def get_log_conf_file():
    log_conf_file = ''
    if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "TEST":
        print("In Test Env")
        log_conf_file = "/config/log_conf.yml"
    else:
        print("In Dev Env")
        log_conf_file = "log_conf.yml"
    return log_conf_file


def load_log_conf():
    """
    Returns:
        logger: Logger
    """
    with open(get_log_conf_file(), 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
        logger = logging.getLogger('basicLogger')

    return logger
