import logging
import logging.config
import yaml
import os


def get_app_conf_file():
    app_conf_file = ''
    if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "TEST":
        print("In Test Env")
        app_conf_file = "/config/app_conf.yml"
    else:
        print("In Dev Env")
        app_conf_file = "app_conf.yml"
    return app_conf_file


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
    with open(load_log_conf(), 'r') as f:
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
    with open(get_app_conf_file(), 'r') as f:
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
