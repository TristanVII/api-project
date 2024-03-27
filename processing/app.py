from datetime import datetime, timedelta
import json
from uuid import uuid4
import connexion
import requests
from connexion import FlaskApp
from load_configs import load_app_conf, load_log_conf
from create_database import create_database, engine
from models import Stats
from process import process_jobs, process_applications
from schedular import init_scheduler
from sqlalchemy.orm import Session
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from kafka_client import Kafka

# Added Comment
CONFIG = load_app_conf()
TIME = CONFIG['TIME']
EVENT_STORE_URL = CONFIG['URL']
KAFKA_HOST = CONFIG['KAFKA_SERVER']
KAFKA_PORT = CONFIG['KAFKA_PORT']
KAFKA_TRIES = CONFIG['KAFKA_RETRIES']
KAFKA_DELAY = CONFIG['KAFKA_DELAY']
KAFKA_EVENT_LOG = CONFIG['KAFKA_EVENT_LOG']
KAFKA_EVENT_COUNT = CONFIG['KAFKA_EVENT_COUNT']
LOGGER = load_log_conf()
event_log_producer = None


def send_message(code, payload):
    if not event_log_producer:
        LOGGER.error(
            f"Event log producer is missing. Could not send {code} - {payload}")
        return
    msg = {"code": code,
           "datetime":
           datetime.now().strftime(
               "%Y-%m-%dT%H:%M:%S"),
           "payload": payload}
    msg_str = json.dumps(msg)
    LOGGER.info(f"Sent kafka message {msg_str}")
    event_log_producer.produce(msg_str.encode('utf-8'))


def kafka_init():
    global event_log_producer
    kafka = Kafka(KAFKA_HOST, KAFKA_PORT, LOGGER, KAFKA_TRIES, KAFKA_DELAY)

    event_log_producer = kafka.get_producer(KAFKA_EVENT_LOG)
    if not event_log_producer:
        LOGGER.error("Failed to get producer")
        exit(1)

    send_message("0003", "Succesfully connected to Kafka")


kafka_init()


def get_stats():
    LOGGER.info('Received request for stats')
    stats = read_stats(False)
    if stats['num_jobs'] < 1 and stats['num_applications'] < 0:
        LOGGER.error('Database has no statistics yet')
        return {}
    LOGGER.debug(f'GET stats requests returns: {stats}')
    LOGGER.info('GET stats request completed')
    return stats, 200


def fetch_and_process_data():
    data = read_stats(True)
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    params = {
        'end_timestamp': time,
        'start_timestamp': data['last_updated'].strftime("%Y-%m-%dT%H:%M:%S")
    }

    jobs_request = requests.get(
        f'{EVENT_STORE_URL}/jobs', params=params, timeout=10)
    applications_request = requests.get(
        f'{EVENT_STORE_URL}/applications', params=params, timeout=10)

    if jobs_request.status_code != 200:
        raise Exception('Error fetching jobs')
    if applications_request.status_code != 200:
        raise Exception('Error fetching applications')

    jobs_data = jobs_request.json()
    application_data = applications_request.json()

    num_jobs_data = len(jobs_data)
    num_application_data = len(application_data)
    LOGGER.info(
        f'Received {num_jobs_data} job events and {num_application_data} application events')

    if num_jobs_data + num_application_data >= KAFKA_EVENT_COUNT:
        send_message(
            "0004", f"Received {num_application_data + num_jobs_data} events")
        LOGGER.info(
            f"Logging 00004. Received {num_application_data + num_jobs_data} events")

    # updates data inplace
    process_jobs(jobs_data, data)
    process_applications(application_data, data)
    LOGGER.info("Finished processing")

    LOGGER.debug(f'Updated statistic values: {data}')

    return data, time


def populate_stats():
    try:
        data, time = fetch_and_process_data()
        write_stats(data['num_jobs'], data['num_applications'],
                    data['average_salary'], data['max_experience'], time)
    except Exception as e:
        LOGGER.error(str(e))


def write_stats(jobs, applications, salary, experience, current_time):

    with Session(engine) as session:
        stats = Stats(
            id=str(uuid4()),
            num_jobs=jobs,
            num_applications=applications,
            average_salary=salary,
            max_experience=experience,
            last_updated=datetime.fromisoformat(current_time)
        )

        session.add(stats)
        session.commit()


def read_stats(full):
    result = None
    with Session(engine) as session:
        result = session.query(Stats).order_by(
            Stats.last_updated.desc()).first()
    LOGGER.info(f'Read stats {result}')
    if not result:
        old = datetime.now() - timedelta(10.0)
        return {'num_jobs': 0, 'num_applications': 0, 'average_salary': 0, 'max_experience': 0, 'last_updated': old}
    else:
        return result.to_dict(full)


# Your functions here here
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
    init_scheduler(populate_stats, TIME)
    app.run(host="0.0.0.0", port=8100)  # nosec
