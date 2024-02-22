import time
import connexion
from pykafka import KafkaClient
import requests
import datetime
import json
from connexion import FlaskApp, NoContent
from load_configs import load_log_conf, load_app_conf


LOGGER = load_log_conf()
CONFIG = load_app_conf()
KAFKA_HOST = CONFIG['KAFKA_SERVER']
KAFKA_PORT = CONFIG['KAFKA_PORT']
KAFKA_TOPIC = CONFIG['KAFKA_TOPIC']


def get_event_at_index(event, index):
    client = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_PORT}')
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    LOGGER.info(f"Retrieving {event} at index: {index} ")
    try:
        curr = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == event:
                if curr == index:
                    return msg['payload']
                else:
                    curr += 1
    except:
        LOGGER.error("No more messages found")
        LOGGER.error(f"Could not find {event} at index: {index}")
        return None


def get_application(index):
    res = get_event_at_index('job_application', index)
    if res:
        return res
    return {"message": "Not Found"}, 404


def get_job(index):
    res = get_event_at_index('job_create', index)
    if res:
        return res
    return {"message": "Not Found"}, 404


# Your functions here
app = FlaskApp(__name__, specification_dir='')
app.add_api("./openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8110)
