import boto3
import pytest
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session
from project.database_client import DatabaseClient
from project.database_models import UserLogins
from project.sqs_consumer import SQSConsumer, SQSClient


@pytest.fixture(scope="session")
def localstack_sqs_client():
    session = boto3.Session(
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    return session.client("sqs", endpoint_url='http://localhost:4566')


def test_consumer(localstack_sqs_client):
    sqs_client = SQSClient(
        "http://localhost:4566/000000000000/login-queue",
        aws_client=localstack_sqs_client
    )
    pg_engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")

    test = SQSConsumer(
        sqs_client=sqs_client,
        db_client=DatabaseClient(pg_engine),
        model=UserLogins)
    test.run(until_empty=True)

    with Session(pg_engine) as db_session:
        count = db_session.query(UserLogins).count()
        assert 100 == count
