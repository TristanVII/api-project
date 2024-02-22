import logging
import logging.config
import yaml


def load_app_conf():
    """
    Returns:
        database
        schedular
        url
    """
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
        database = app_config['datastore']['filename']
        schedular = app_config['scheduler']['period_sec']
        url = app_config['eventstore']['url']

    return database, schedular, url


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
