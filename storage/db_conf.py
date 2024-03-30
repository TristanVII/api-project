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


def load_app_conf():
    """
    Returns:
      Dictionary containing:
        - USER: string
        - PASSWORD: string
        - HOST: string
        - PORT: string
        - DB: string
    """
    with open(get_app_conf_file(), 'r') as f:
        app_config = yaml.safe_load(f.read())
        datastore = app_config['datastore']
        events = app_config['events']
        config_dict = {
            'USER': datastore['user'],
            'PASSWORD': datastore['password'],
            'HOST': datastore['hostname'],
            'PORT': datastore['port'],
            'DB': datastore['db'],
            'KAFKA_SERVER': events['hostname'],
            'KAFKA_PORT': events['port'],
            'KAFKA_TOPIC': events['topic'],
            'KAFKA_RETRIES': events['max_tries'],
            'KAFKA_DELAY': events['delay'],
            'KAFKA_EVENT_LOG': events['event_log']
        }
    return config_dict
