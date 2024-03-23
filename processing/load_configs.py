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
        events = app_config['events']

        return {
            'DATABASE': app_config['datastore']['filename'],
            'TIME': app_config['scheduler']['period_sec'],
            'URL': app_config['eventstore']['url'],
            'KAFKA_SERVER': events['hostname'],
            'KAFKA_PORT': events['port'],
            'KAFKA_TOPIC': events['topic'],
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
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
        logger = logging.getLogger('basicLogger')

    return logger
