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


def load_app_conf():
    """
    Returns:
      Dictionary containing:
      KAFKA_SERVER: string
      KAFKA_PORT: string
      KAFKA_TOPIC: string
    """
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())

        kafka = app_config['events']
        datastore = app_config['datastore']
        config_dict = {
            'DATABASE': datastore['filename'],
            'KAFKA_SERVER': kafka['hostname'],
            'KAFKA_PORT': kafka['port'],
            'KAFKA_EVENT_LOG': kafka['event_log'],
            'KAFKA_TRIES': kafka['max_tries'],
            'KAFKA_DELAY': kafka['delay']
        }
    return config_dict
