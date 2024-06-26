import os
import time
import connexion
import json
from connexion import FlaskApp
from load_configs import load_log_conf, load_app_conf
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from kafka_client import Kafka
from datetime import datetime

LOGGER = load_log_conf()
CONFIG = load_app_conf()
KAFKA_HOST = CONFIG['KAFKA_SERVER']
KAFKA_PORT = CONFIG['KAFKA_PORT']
KAFKA_TOPIC = CONFIG['KAFKA_TOPIC']
KAFKA_TRIES = CONFIG['KAFKA_TRIES']
KAFKA_DELAY = CONFIG['KAFKA_DELAY']
kafka = None


def kafka_init():
    global kafka
    kafka = Kafka(KAFKA_HOST, KAFKA_PORT, LOGGER, KAFKA_TRIES, KAFKA_DELAY)


kafka_init()


def get_event_at_index(event, index):
    global kafka
    LOGGER.info(f"Retrieving {event} at index: {index} ")
    consumer = kafka.get_consumer(KAFKA_TOPIC)
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


if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    LOGGER.info("In test env. CORS disabled")
    app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
#
app.add_api("./openapi.yaml", base_path="/audit_log",
            strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8110)
