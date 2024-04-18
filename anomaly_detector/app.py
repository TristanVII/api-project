import time
import connexion
import requests
import datetime
import json
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from connexion import FlaskApp, NoContent
from load_configs import load_app_conf, load_log_conf
from kafka_client import Kafka
from create_database import create_database, engine
from threading import Thread
from models import Anomaly
from sqlalchemy.orm import Session

LOGGER = load_log_conf()
CONFIG = load_app_conf()
KAFKA_HOST = CONFIG['KAFKA_SERVER']
KAFKA_PORT = CONFIG['KAFKA_PORT']
KAFKA_TOPIC = CONFIG['KAFKA_TOPIC']
KAFKA_TRIES = CONFIG['KAFKA_TRIES']
KAFKA_DELAY = CONFIG['KAFKA_DELAY']
SALARY_THRESHOLD = CONFIG['SALARY_THRESHOLD']
AGE_THRESHOLD = CONFIG['AGE_THRESHOLD']
kafka = None


def kafka_init():
    global kafka
    kafka = Kafka(KAFKA_HOST, KAFKA_PORT, LOGGER, KAFKA_TRIES, KAFKA_DELAY)


kafka_init()


def get_anomalies(anomaly_type):
    return [], 200


def write_message(msg):
    time = datetime.now()
    event = Anomaly(
        event_id=str(msg['event_id']),
        trace_id=str(msg['trace_id']),
        event_type=str(msg['event_type']),
        anomaly_type=str(msg['anomaly_type']),
        description=str(msg['description']),
        date=time
    )
    LOGGER.info(
        f"Event: {event.event_id} - {event.trace_id} - {event.date}")
    with Session(engine) as session:
        session.add(event)
        session.commit()

    LOGGER.debug(f"Stored event to database")


def process_messages():
    """ Process event messages """

    kafka = Kafka(KAFKA_HOST, KAFKA_PORT,
                  LOGGER, KAFKA_TRIES, KAFKA_DELAY)

    consumer = kafka.get_consumer(KAFKA_TOPIC)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        LOGGER.info(f"received msg {msg}")

        try:
            if msg['type'] == 'job_application':
                LOGGER.info('Processing job_application')
                msg = msg["payload"]
                if int(msg['age']) > int(AGE_THRESHOLD):
                    event = {"event_id": msg['job_application_id'], "trace_id": msg['trace_id'],
                             'event_type': msg['type'], 'anomaly_type': 'TooHigh', 'description': f'Age: {msg["age"]} is above treshold of {AGE_THRESHOLD}'}
                    write_message(event)

            elif msg['type'] == 'job_create':
                LOGGER.info('Processing job create')
                msg = msg["payload"]
                if int(msg['salary']) < int(SALARY_THRESHOLD):
                    event = {"event_id": msg['job_listing_id'], "trace_id": msg['trace_id'],
                             'event_type': msg['type'], 'anomaly_type': 'TooLow', 'description': f'Age: {msg["salary"]} is below treshold of {SALARY_THRESHOLD}'}
                    write_message(event)
            else:
                LOGGER.error(
                    "Message is not of type job_application or job_create")
            consumer.commit_offsets()
        except:
            pass
            LOGGER.error(f"Error writing data to mysql lite")


app = FlaskApp(__name__, specification_dir='')

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_api("./openapi.yaml", strict_validation=True,
            validate_responses=True, base_path="/anomaly_detector")


if __name__ == "__main__":
    create_database()
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()
    app.run(host="0.0.0.0", port=8999)
