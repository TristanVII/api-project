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

        events = app_config['events']
        config_dict = {
            'KAFKA_SERVER': events['hostname'],
            'KAFKA_PORT': events['port'],
            'KAFKA_TOPIC': events['topic']
        }
    return config_dict
