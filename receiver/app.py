import time
import connexion
import requests
import datetime
import json
from connexion import FlaskApp, NoContent
from load_configs import load_app_conf, load_log_conf
from kafka_client import Kafka

CONFIG = load_app_conf()
CREATE_URL = CONFIG['job_create_url']
APPLICATION_URL = CONFIG['job_application_url']
KAFKA_HOST = CONFIG['KAFKA_SERVER']
KAFKA_PORT = CONFIG['KAFKA_PORT']
KAFKA_TOPIC = CONFIG['KAFKA_TOPIC']
KAFKA_TRIES = CONFIG['KAFKA_TRIES']
KAFKA_DELAY = CONFIG['KAFKA_DELAY']
KAFKA_EVENT_LOG = CONFIG['KAFKA_EVENT_LOG']
LOGGER = load_log_conf()
event_log_producer = None
event_producer = None


def kafka_init():
    global event_log_producer, event_producer
    kafka = Kafka(KAFKA_HOST, KAFKA_PORT, LOGGER, KAFKA_TRIES, KAFKA_DELAY)

    event_log_producer = kafka.get_producer(KAFKA_EVENT_LOG)
    event_producer = kafka.get_producer(KAFKA_TOPIC)
    if not event_log_producer or not event_producer:
        LOGGER.error("Failed to get producers")
        exit(1)

    msg = {"code": "0001",
           "datetime":
           datetime.datetime.now().strftime(
               "%Y-%m-%dT%H:%M:%S"),
           "payload": "Succesfully connected to Kafka"}
    msg_str = json.dumps(msg)
    LOGGER.info(f"Sent kafka message {msg_str}")
    event_log_producer.produce(msg_str.encode('utf-8'))


kafka_init()


def add_job_listing(body):
    """ Receives a job listing event """
    # header = {'Content-type': 'application/json'}
    trace_id = time.time_ns()
    event_name = "job create"

    LOGGER.info(
        f'Received event "{event_name}" request with a trace id of {trace_id}')

    body['trace_id'] = str(trace_id)

    msg = {"type": "job_create",
           "datetime":
           datetime.datetime.now().strftime(
               "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    event_producer.produce(msg_str.encode('utf-8'))

    LOGGER.info(
        f'Returned event {event_name} response {trace_id} with status 201')
    return NoContent, 201


def add_job_application(body):
    """ Receives a job application event """
    # header = {'Content-type': 'application/json'}
    trace_id = time.time_ns()
    event_name = "job application"

    LOGGER.info(
        f'Received event "{event_name}" request with a trace id of {trace_id}')

    body['trace_id'] = str(trace_id)
    msg = {"type": "job_application",
           "datetime":
           datetime.datetime.now().strftime(
               "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    print(event_producer)
    event_producer.produce(msg_str.encode('utf-8'))
    LOGGER.info(
        f'Returned event "{event_name}" response {trace_id} with status 201')
    return NoContent, 201


# Your functions here
app = FlaskApp(__name__, specification_dir='')
app.add_api("./openapi.yaml", base_path="/receiver",
            strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # nosec
