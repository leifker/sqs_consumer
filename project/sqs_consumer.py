import json
import boto3
import logging
import os
logger = logging.getLogger(__name__)


class SQSConsumer:
    """
    Simple consumer reads from SQS queue and writes to database.
    """

    def __init__(self, sqs_client, db_client, model):
        """
        Constructor for a generic consumer. Reads objects from queue, writes to database.
        :param sqs_client: SQS client wrapper
        :param db_client: Database client wrapper
        :param model: Object model to save to database
        """
        self._model = model
        self._db = db_client
        self._sqs = sqs_client

    def run(self, limit=None, until_empty=False):
        """
        Runs the consuming process
        :return:
        """
        if limit:
            logger.info("Consuming {} message batches.".format(limit))
            for i in range(limit):
                self._receive()
        elif until_empty:
            logger.info("Consuming until empty queue")
            count = -1
            while count != 0:
                count = self._receive()
        else:
            logger.info("Consuming infinite messages batches")
            while True:
                self._receive()

    def _receive(self):
        messages = []
        try:
            resp = self._sqs.receive_message()
            try:
                messages = resp['Messages']
            except KeyError:
                logger.info("Empty queue")
        except Exception:
            raise Exception("Error receiving messages.")

        if messages:
            self._process(messages)
            self._acknowledge(messages)

        return len(messages)

    def _process(self, messages):
        try:
            models = [self._model(**json.loads(msg['Body'])) for msg in messages]
            self._db.add_all(models)
        except Exception:
            raise Exception("Error inserting to database")

    def _acknowledge(self, messages):
        try:
            entries = [{'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']} for msg in messages]
            resp = self._sqs.delete_message_batch(Entries=entries)
            if len(resp['Successful']) != len(entries):
                raise Exception("Error removing messages from queue. Response: {}".format(resp))
        except Exception:
            raise Exception("Error acknowledging messages from queue.")


class SQSClient:
    """
    SQS client wrapper, reads messages from SQS queue
    """

    def __init__(self, queue_url, max_messages=10, aws_client=None):
        self._queue_url = queue_url
        self._max_messages = max_messages

        if not aws_client:
            session = boto3.Session()
            self._aws_sqs = session.client('sqs', endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))
            logger.info("Default AWS Session created.")
        else:
            self._aws_sqs = aws_client

    def receive_message(self, **kwargs):
        return self._aws_sqs.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=self._max_messages,
            **kwargs)

    def delete_message_batch(self, **kwargs):
        return self._aws_sqs.delete_message_batch(QueueUrl=self._queue_url, **kwargs)
