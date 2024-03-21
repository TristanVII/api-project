import yaml


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
    with open('app_conf.yml', 'r') as f:
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
            'KAFKA_DELAY': events['delay']
        }
    return config_dict
