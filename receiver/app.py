import time
import connexion
from pykafka import KafkaClient
import requests
import datetime
import json
from connexion import FlaskApp, NoContent
from load_configs import load_app_conf, load_log_conf

CONFIG = load_app_conf()
CREATE_URL = CONFIG['job_create_url']
APPLICATION_URL = CONFIG['job_application_url']
KAFKA_SERVER = CONFIG['KAFKA_SERVER']
KAFKA_PORT = CONFIG['KAFKA_PORT']
KAFKA_TOPIC = CONFIG['KAFKA_TOPIC']
KAFKA_TRIES = CONFIG['KAFKA_TRIES']
KAFKA_DELAY = CONFIG['KAFKA_DELAY']
KAFKA_EVENT_LOG = CONFIG['KAFKA_EVENT_LOG']
KAFKA_HOST = f'{KAFKA_SERVER}:{KAFKA_PORT}'
LOGGER = load_log_conf()

client = None
tries = 0

while tries < KAFKA_TRIES and not client:
    try:
        LOGGER.info("Storage connecting to kafka...")
        client = KafkaClient(hosts=KAFKA_HOST)
        tries += 1

    except:
        LOGGER.error(f"Failed to connect to kafka. Rety attempt {tries}")
        client = None
        time.sleep(KAFKA_DELAY)

if not client:
    LOGGER.error(
        f'Failed to connect to Kafka client after {tries} retries.')
    exit(1)

LOGGER.info("Succesfully connected to Kafka")
topic = client.topics[str.encode(KAFKA_EVENT_LOG)]
producer = topic.get_sync_producer()
msg = {"code": "0001",
       "datetime":
       datetime.datetime.now().strftime(
           "%Y-%m-%dT%H:%M:%S"),
       "payload": "Succesfully connected to Kafka"}
msg_str = json.dumps(msg)
producer.produce(msg_str.encode('utf-8'))


def add_job_listing(body):
    """ Receives a job listing event """
    # header = {'Content-type': 'application/json'}
    trace_id = time.time_ns()
    event_name = "job create"

    LOGGER.info(
        f'Received event "{event_name}" request with a trace id of {trace_id}')

    body['trace_id'] = str(trace_id)

    print("KAFKA")

    msg = {"type": "job_create",
           "datetime":
           datetime.datetime.now().strftime(
               "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    print("SENT")

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
    producer.produce(msg_str.encode('utf-8'))
    LOGGER.info(
        f'Returned event "{event_name}" response {trace_id} with status 201')
    return NoContent, 201


# Your functions here
app = FlaskApp(__name__, specification_dir='')
app.add_api("./openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    print("Receiver service closed...")
