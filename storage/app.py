from datetime import datetime
import json
from threading import Thread
from sqlalchemy.orm import Session
from sqlalchemy import and_
from connexion import FlaskApp
from create_database import create_database, engine
from models import JobApplication, JobListing
from load_configs import load_log_conf
from db_conf import load_app_conf
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from kafka_client import Kafka

LOGGER = load_log_conf()
CONFIG = load_app_conf()
KAFKA_HOSTNAME = CONFIG['KAFKA_SERVER']
KAFKA_PORT = CONFIG['KAFKA_PORT']
KAFKA_TOPIC = CONFIG['KAFKA_TOPIC']
KAFKA_RETRIES = CONFIG['KAFKA_RETRIES']
KAFKA_DELAY = CONFIG['KAFKA_DELAY']
KAFKA_EVENT_LOG = CONFIG['KAFKA_EVENT_LOG']


def add_job_listing(body):
    """ Receives a job listing event """
    trace_id = body['trace_id']

    curr_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    LOGGER.info(f'Added job event at {curr_time}')
    job_listing = JobListing(
        job_listing_id=body['job_listing_id'],
        title=body['title'],
        location=body['location'],
        salary=body['salary'],
        sector=body['sector'],
        date=datetime.fromisoformat(body['date']),
        date_created=curr_time,
        trace_id=body['trace_id']
    )

    with Session(engine) as session:
        session.add(job_listing)
        session.commit()

    LOGGER.debug(
        f'Stored event "job create" request with a trace id of {trace_id}')


def add_job_application(body):
    """ Receives a job application event """
    trace_id = body['trace_id']

    curr_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    LOGGER.info(f'Added application event at {curr_time}')
    job_application = JobApplication(
        job_application_id=body['job_application_id'],
        job_listing_id=body['job_listing_id'],
        gender=body['gender'],
        age=body['age'],
        years_of_experience=body['years_of_experience'],
        date=datetime.fromisoformat(body['date']),
        date_created=curr_time,
        trace_id=body['trace_id']
    )

    with Session(engine) as session:
        session.add(job_application)
        session.commit()

    LOGGER.debug(
        f'Stored event "job application" request with a trace id of {trace_id}')


def get_applications(start_timestamp, end_timestamp):
    start_timestamp_datetime = datetime.strptime(
        start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.strptime(
        end_timestamp, "%Y-%m-%dT%H:%M:%S")

    data = []
    with Session(engine) as session:
        data = session.query(JobApplication).filter(and_(
            end_timestamp_datetime > JobApplication.date_created, JobApplication.date_created >= start_timestamp_datetime)).all()
    res = [application.to_dict() for application in data]

    LOGGER.info("Query for applications after %s returns %d results" %
                (start_timestamp, len(res)))
    return res, 200


def get_jobs(start_timestamp, end_timestamp):
    start_timestamp_datetime = datetime.strptime(
        start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.strptime(
        end_timestamp, "%Y-%m-%dT%H:%M:%S")

    data = []
    with Session(engine) as session:
        data = session.query(JobListing).filter(and_(
            end_timestamp_datetime > JobListing.date_created, JobListing.date_created >= start_timestamp_datetime)).all()
    res = [job.to_dict() for job in data]

    LOGGER.info("Query for jobs after %s returns %d results" %
                (start_timestamp, len(res)))
    return res, 200


def process_messages():
    """ Process event messages """
    kafka = Kafka(KAFKA_HOSTNAME, KAFKA_PORT,
                  LOGGER, KAFKA_RETRIES, KAFKA_DELAY)

    consumer = kafka.get_consumer(KAFKA_TOPIC)
    producer = kafka.get_producer(KAFKA_EVENT_LOG)

    msg = {"code": "0002",
           "datetime":
           datetime.now().strftime(
               "%Y-%m-%dT%H:%M:%S"),
           "payload": "Ready to receive messages"}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    for msg in consumer:

        msg_str = msg.value.decode('utf-8')

        msg = json.loads(msg_str)

        LOGGER.info("Message: %s" % msg)

        payload = msg["payload"]

        try:

            if msg["type"] == "job_application":
                LOGGER.debug(f"Processing job_application: {payload}")
                add_job_application(payload)
            elif msg["type"] == "job_create":
                LOGGER.debug(f"Processing job_application: {payload}")
                add_job_listing(payload)
            else:
                LOGGER.error(
                    "Message is not of type job_application or job_create")

            consumer.commit_offsets()
        except:
            LOGGER.error(f"Error connecting to mysql to add '{msg}'")


app = FlaskApp(__name__, specification_dir='')
app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_api("./openapi.yaml", base_path="/storage",
            strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    create_database()
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()
    app.run(host="0.0.0.0", port=8090)  # nosec
