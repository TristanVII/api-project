import logging
import logging.config
import yaml
import os


def get_app_conf_file():
    app_conf_file = ''
    print(os.environ)
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
      Dictionary containing:
        - job_create_url: string
        - job_application_url: string
        - KAFKA_SERVER: string
        - KAFKA_PORT: string
        - KAFKA_TOPIC: string
        - KAFKA_TRIES: int
        - KAFKA_DELAY: int
        - KAFKA_EVENT_LOG: string
    """
    with open(get_app_conf_file(), 'r') as f:
        app_config = yaml.safe_load(f.read())
        config_dict = {
            'job_create_url': app_config['job_create']['url'],
            'job_application_url': app_config['job_application']['url'],
            'KAFKA_SERVER': app_config['events']['hostname'],
            'KAFKA_PORT': app_config['events']['port'],
            'KAFKA_TOPIC': app_config['events']['topic'],
            'KAFKA_TRIES': app_config['events']['max_tries'],
            'KAFKA_DELAY': app_config['events']['delay'],
            'KAFKA_EVENT_LOG': app_config['events']['event_log']
        }
    return config_dict


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
