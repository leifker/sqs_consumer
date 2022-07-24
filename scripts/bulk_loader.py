import json
import gzip
import threading
import localstack_client.session as boto3


threadLock = threading.Lock()


class LoaderThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self._id = thread_id

    def run(self):
        threadLock.acquire()
        sqs = boto3.client("sqs")
        threadLock.release()

        queue_url = "http://localhost:4566/000000000000/login-queue"

        with gzip.open("sample_data.json.gz", "r") as f:
            data = json.load(f)

        assert len(data) == 100

        for multiplier in range(1000):
            for record in data:
                temp = dict(record)
                temp['user_id'] = "{}-{}-{}".format(self._id, record['user_id'], multiplier)
                sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(temp))
            print("Loaded({}) {}/1000 * 100".format(self._id, multiplier + 1))


def main():
    # 10 * 100,000
    threads = [LoaderThread(i) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
