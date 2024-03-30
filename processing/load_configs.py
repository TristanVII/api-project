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


def load_app_conf():
    """
    Returns:
        database
        schedular
        url
    """
    with open(get_app_conf_file(), 'r') as f:
        app_config = yaml.safe_load(f.read())
        events = app_config['events']

        return {
            'DATABASE': app_config['datastore']['filename'],
            'TIME': app_config['scheduler']['period_sec'],
            'URL': app_config['eventstore']['url'],
            'KAFKA_SERVER': events['hostname'],
            'KAFKA_PORT': events['port'],
            'KAFKA_RETRIES': events['max_tries'],
            'KAFKA_DELAY': events['delay'],
            'KAFKA_EVENT_LOG': events['event_log'],
            'KAFKA_EVENT_COUNT': events['event_count']
        }


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
