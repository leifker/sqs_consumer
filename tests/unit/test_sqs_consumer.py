import json
import boto3
import pytest
from botocore.stub import Stubber
from project.database_client import DatabaseClient
from project.database_models import UserLogins
from project.sqs_consumer import SQSConsumer, SQSClient


@pytest.fixture(scope="function")
def mock_aws_client():
    aws_client = boto3.client("sqs", region_name='us-east-1')
    stubber = Stubber(aws_client)
    stubber.add_response('receive_message',
                         {
                             "Messages": [
                                 {
                                     "Body": json.dumps({
                                         'user_id': 'abcd',
                                         'device_type': 'mobile',
                                         'masked_ip': '127.0.0.1',
                                         'masked_device_id': '89ABCDEF-01234567-89ABCDEF',
                                         'locale': 'us',
                                         'app_version': 1,
                                         'create_date': '2022-07-23'
                                     }),
                                     "ReceiptHandle": "AQEB6nR4...HzlvZQ==",
                                     "MD5OfBody": "1000f835...a35411fa",
                                     "MD5OfMessageAttributes": "b8e89563...e088e74f",
                                     "MessageId": "d6790f8d-d575-4f01-bc51-40122EXAMPLE",
                                     "Attributes": {
                                         "SenderId": "AIDAIAZKMSNQ7TEXAMPLE",
                                         "SentTimestamp": "1442428276921"
                                     },
                                     "MessageAttributes": {
                                         "PostalCode": {
                                             "DataType": "String",
                                             "StringValue": "ABC123"
                                         }
                                     }
                                 },
                                 {
                                     "Body": json.dumps({
                                         'user_id': 'abcd',
                                         'device_type': 'mobile',
                                         'masked_ip': '127.0.0.1',
                                         'masked_device_id': '89ABCDEF-01234567-89ABCDEF',
                                         'locale': 'us',
                                         'app_version': 1,
                                         'create_date': '2022-07-24'
                                     }),
                                     "MessageId": "d6790f8d-d575-4f01-bc51-40122EXAMPLE",
                                     "ReceiptHandle": "AQEB6nR4...HzlvZQ==",
                                 }
                             ]
                         },
                         {'MaxNumberOfMessages': 10, 'QueueUrl': 'queue_url'})
    stubber.add_response('delete_message_batch',
                         {'Successful': [
                             {'Id': 'd6790f8d-d575-4f01-bc51-40122EXAMPLE'},
                             {'Id': 'd6790f8d-d575-4f01-bc51-40122EXAMPLE'}
                         ], 'Failed': []},
                         {'QueueUrl': 'queue_url',
                          'Entries': [
                              {'Id': 'd6790f8d-d575-4f01-bc51-40122EXAMPLE', 'ReceiptHandle': 'AQEB6nR4...HzlvZQ=='},
                              {'Id': 'd6790f8d-d575-4f01-bc51-40122EXAMPLE', 'ReceiptHandle': 'AQEB6nR4...HzlvZQ=='}
                          ]})
    stubber.activate()
    yield aws_client


class TestSQSClient:

    def test_receive_message(self, mock_aws_client):
        test = SQSClient("queue_url", aws_client=mock_aws_client)
        assert len(test.receive_message()['Messages']) == 2


class TestConsumer:

    def test_consumer(self, db_session, engine, mock_aws_client):
        test = SQSConsumer(
            sqs_client=SQSClient("queue_url", aws_client=mock_aws_client),
            db_client=DatabaseClient(engine),
            model=UserLogins)
        test.run(limit=1)

        count = db_session.query(UserLogins).filter(UserLogins.user_id == 'abcd').count()
        assert count == 2
