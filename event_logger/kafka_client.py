import time
from pykafka import KafkaClient
from pykafka.common import OffsetType


class Kafka:
    def __init__(self, hostname, port, logger, max_tries=5, delay=5):
        self.hostname = hostname
        self.port = port
        self.max_tries = max_tries
        self.delay = delay
        self.logger = logger
        self.client = None

        # Try connecting to kafka
        self.__init_kafka()

    def __init_kafka(self):
        tries = 0

        while not self.client and tries < self.max_tries:
            try:
                self.logger.info(
                    f"Trying to connect to Kafka at {self.hostname}:{self.port}")
                self.client = KafkaClient(hosts=f'{self.hostname}:{self.port}')
            except:
                self.logger.error(
                    f"Failed connecting to kafka on attempt {tries + 1}")
                tries += 1
                self.client = None
                time.sleep(self.delay)

        if not self.client:
            self.logger.error(
                f'Failed to connect to Kafka client after {tries} attempts. Exiting...')
            exit(1)

        self.logger.info("Succesfully connected to Kafka")

    def __get_topic(self, topic):
        if not self.client:
            raise Exception("Not connected to kafka client")

        key = str.encode(topic)

        if key in self.client.topics:
            return self.client.topics[key]

        raise Exception(f"No topic {key} was found")

    def get_consumer(self, topic_name):
        try:
            topic = self.__get_topic(topic_name)
            print(topic)
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                                 reset_offset_on_start=False,
                                                 auto_offset_reset=OffsetType.LATEST)
            print(consumer)
        except:
            self.logger.error("Failed to get comsumer")
            return

        self.logger.debug(f"Got consumer for {topic_name}")
        return consumer

    def get_producer(self, topic_name):
        try:
            topic = self.__get_topic(topic_name)
            producer = topic.get_sync_producer()
        except:
            self.logger.error("Failed to get producer")
            return

        self.logger.debug(f"Got producer for {topic_name}")
        return producer
