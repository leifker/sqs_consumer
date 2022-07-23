# SQS to Database Consumer

This project is designed to read messages from an SQS queue and insert into a postgres database.
The code is using python and the well known [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
and [sqlalchemy](https://www.sqlalchemy.org/) libraries to perform the work.

The project is organized into 2 main components.

1. Database client and data model located in `database_client.py` & `database_models.py`
2. SQS consumer and client wrapper in `sqs_consumer.py`

Additionally, the project contains a few unit tests as well as a local integration test using
the provided localstack instance. The `pytest` framework was used to run the tests and additionally
`flake8` is used for linting. The python code is built and tested in within a virtual environment.

## Build & Test

### Requirements

The requirements are split into separate application and development requirements in `requirements.txt`
and `requirements-dev.txt` respectively. Updates to these files are automatically detected by the
included `Makefile`.

### Unit tests & Linting

By default, the unittests and linter is run by simply running `make`.

```shell 
$ make
python3 -m pytest tests/unit/
===================== test session starts =====================
platform linux -- Python 3.10.5, pytest-7.1.2, pluggy-1.0.0
rootdir: /mnt/code/code/fetch/interview
collected 4 items                                                                                                                                                                                                                   

tests/unit/test_database_client.py .                    [ 25%]
tests/unit/test_database_models.py .                    [ 50%]
tests/unit/test_sqs_consumer.py ..                      [100%]

===================== 4 passed in 4.13s =======================
flake8 project
```

### Localstack tests

A separate make command is provided for running the localstack tests. `make awslocal_test`.

#### 1. Start localstack

Per the instructions, setup the localstack environment by cloning the git repo and running the `make start`

```shell
$ make start
docker-compose up -d
Creating network "data-engineering-take-home_default" with the default driver
Creating data-engineering-take-home_localstack_1 ... done
Creating data-engineering-take-home_postgres_1   ... done
```

#### 2. Run localstack tests

Change to this project's directory to execute the tests.

The test will read the expected 100 messages from the queue, insert them into the database, and
then select from the table checking for the expected 100 messages in the database table.

```shell
$ make awslocal_test
python3 -m pytest tests/awslocal/
===================== test session starts =====================
platform linux -- Python 3.10.5, pytest-7.1.2, pluggy-1.0.0
rootdir: /mnt/code/code/fetch/interview
collected 1 item                                                                                                                                                                                                                    

tests/awslocal/test_awslocal.py .                        [100%]

===================== 1 passed in 0.41s =======================
```

### Clean up

`Makefile` provides clean-up of virtual environment and python artifacts.

```shell
rm -rf python/venv
find . -type f -name *.pyc -delete
find . -type d -name __pycache__ -delete

```

## Execution

Running the application in a non-test/non-virtual environment.

Requirements:
* python 3 (tested with 3.10)
* AWS credentials

1. Install app requirements `pip install -r requirements.txt [--user]`
2. Export SQS and Postgres information. Examples for AWS from localstack.
```shell

export SQS_URL="http://localhost:4566/000000000000/login-queue"
export PG_URL="postgresql://postgres:postgres@localhost:5432/postgres"

export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_ENDPOINT_URL="http://localhost:4566"
```

3. Execute `make run`, the application will run until the queue is empty.
```shell
$ make run
python3 project/app.py
$ echo $?
0
$ awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
$ 
```

Note: By default the client will execute indefinitely.

## Design Notes

### Supports Multiple Models

Flexibility was added to allow re-using the same consumer class to read other types of
objects from other SQS queues by simply passing the consumer a compatible model.

The model, `UserLogins` used for this project, can be swapped with a different 
models for different object queues.

```python
    SQSConsumer(model=UserLogins)
```

### Supports Multiple Backends

SQLAlchemy has a number of backends besides the postgres backend used in this project.
This allows for swapping the destination datastore, for example the unit tests swap
the postgres engine for a sqlite in memory database to run tests.

```python
    engine = create_engine("sqlite://", echo=True, future=True)
    SQSConsumer(db_client=DatabaseClient(engine))
```

### Consumer modes

There are 3 different consumer modes offered which make it easier to write tests
for even if not particularly useful in the real world.

1. Consume indefinitely
2. Consume N batches
3. Consume until emtpy

```python
consumer = SQSConsumer(model=UserLogins)

# Consume forever
consumer.run()

# Consume 1 batch
consumer.run(limit=1)

# Consume until empty
consumer.run(until_empty=True)
```

## Future Work

### Database Schema

#### Primary Key

For postgres, the lack of a primary key on the table is suspect. Likely this table should
include a primary key either based on an auto-incrementing `event_id` or possibly adding
a timestamp column in order to construct a composite primary key of (`timestamp`, `user_id`)
or something similar assuming duplicates at the millisecond range are unlikely.

#### Constraints & Indexes

There are also no constraints on the schema for non-null columns, missing pk (as mentioned), 
nor are there indexes on any of the columns. These are likely addressed in the actual 
implementation already.

#### app_version type

The `app_version` column is an integer while the messages contain string versions. The temporary
solution was to insert the major version, however it might be useful to capture the complete
and accurate application version.

#### Unit Test Coverage

Increase the unit test coverage.

#### CLI options

Additional CLI options including help documentation and command line arguments using
[argparse](https://docs.python.org/3/library/argparse.html). Things like the consumer
run modes, log levels, and perhaps a queue peek function would be useful for debugging.


#### Consumer Retry

There are situations where a certain number of re-tries may be useful before failing.
This project is written to fail fast without any re-try logic.
