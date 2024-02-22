import logging
import logging.config
import yaml


def load_log_conf():
    """
    Returns:
        logger: Logger
    """
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
        logger = logging.getLogger('basicLogger')

    return logger
