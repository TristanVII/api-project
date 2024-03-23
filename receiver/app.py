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
LOGGER = load_log_conf()

client = KafkaClient(hosts=f'{KAFKA_SERVER}:{KAFKA_PORT}')
topic = client.topics[str.encode(KAFKA_TOPIC)]
producer = topic.get_sync_producer()


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
