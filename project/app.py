#!/usr/bin/env python3

import logging
import os
import sys
from sqlalchemy import create_engine
from database_models import UserLogins
from database_client import DatabaseClient
from sqs_consumer import SQSConsumer, SQSClient

log_level = os.environ.get("LOG_LEVEL") if os.environ.get("LOG_LEVEL") else logging.WARN
logging.basicConfig(stream=sys.stdout, level=log_level)


if __name__ == '__main__':
    sqs_client = SQSClient(os.environ["SQS_URL"], max_messages=10)
    pg_engine = create_engine(os.environ["PG_URL"])
    SQSConsumer(sqs_client=sqs_client, db_client=DatabaseClient(pg_engine), model=UserLogins).run(until_empty=True)
