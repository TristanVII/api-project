import time
import uuid
import connexion
from datetime import datetime
from pykafka import KafkaClient
import json
from threading import Thread
from connexion import FlaskApp
from pykafka.common import OffsetType
from sqlalchemy import func
from load_configs import load_log_conf, load_app_conf
from create_database import create_database, engine
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import Event


LOGGER = load_log_conf()
CONFIG = load_app_conf()
KAFKA_HOST = CONFIG['KAFKA_SERVER']
KAFKA_PORT = CONFIG['KAFKA_PORT']
KAFKA_EVENT_LOG = CONFIG['KAFKA_EVENT_LOG']
KAFKA_TRIES = CONFIG['KAFKA_TRIES']
KAFKA_DELAY = CONFIG['KAFKA_DELAY']


def get_events_stats():
    with Session(engine) as session:
        query = session.query(Event.code, func.sum(
            Event.code)).group_by(Event.code)
        results = query.all()

    LOGGER.info(f"Stats database query returned {results}")
    resp = {
        "0001": 0,
        "0002": 0,
        "0003": 0,
        "0004": 0
    }
    for code, count in results:
        resp[code] = count

    return resp, 201


def write_message(msg):
    time = datetime.now()
    event = Event(
        id=str(uuid.uuid4()),
        code=str(msg['code']),
        message=str(msg['payload']),
        date=time
    )
    LOGGER.info(
        f"Received message: {event.code} - {event.message} - {event.date}")
    with Session(engine) as session:
        session.add(event)
        session.commit()

    LOGGER.debug(f"Stored event to database")


def process_messages():
    """ Process event messages """

    hostname = "%s:%d" % (
        KAFKA_HOST, KAFKA_PORT)
    client = None

    retry = 1
    while not client and retry < KAFKA_TRIES:
        try:
            LOGGER.info("Storage connecting to kafka...")
            client = KafkaClient(hosts=hostname)
        except:
            LOGGER.error(f"Failed to connect to kafka. Retry attempt {retry}")
            retry += 1
            client = None
            time.sleep(KAFKA_DELAY)

    if not client:
        LOGGER.error(
            f'Failed to connect to Kafka client after {retry} retries.')
        exit(1)

    LOGGER.info("Succesfully connected to Kafka")

    topic = client.topics[str.encode(KAFKA_EVENT_LOG)]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        print(msg)
        write_message(msg)
        try:
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
app.add_api("./openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    create_database()
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()
    app.run(host="0.0.0.0", port=8120)
