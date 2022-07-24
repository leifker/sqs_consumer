#!/usr/bin/env python3
import threading
import logging
import os
import sys
from sqlalchemy import create_engine
from database_models import UserLogins
from database_client import DatabaseClient
from sqs_consumer import SQSConsumer, SQSClient

log_level = os.environ.get("LOG_LEVEL", logging.WARN)
logging.basicConfig(stream=sys.stdout, level=log_level)
logger = logging.getLogger(__name__)


class ConsumerThread(threading.Thread):
    def __init__(self, thread_id, queue_url, engine):
        threading.Thread.__init__(self)
        self._id = thread_id
        self._queue_url = queue_url
        self._engine = engine

    def run(self):
        logger.info("Starting thread {}".format(self._id))
        sqs_client = SQSClient(self._queue_url, max_messages=10)
        db_client = DatabaseClient(self._engine)
        SQSConsumer(sqs_client=sqs_client, db_client=db_client, model=UserLogins).run(until_empty=True)
        logger.info("Thread {} completed.".format(self._id))


def main():
    thread_count = int(os.environ.get("APP_THREAD_COUNT", 1))
    sqs_url = os.environ["SQS_URL"]
    pg_engine = create_engine(os.environ["PG_URL"])

    threads = [ConsumerThread(i, queue_url=sqs_url, engine=pg_engine) for i in range(thread_count)]

    for t in threads:
        t.start()

    logger.info("Waiting for thread completion.")
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
