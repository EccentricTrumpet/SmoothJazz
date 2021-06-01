from multiqueue import *
import threading
import unittest
import logging
import sys
import time

class MultiQueueTest(unittest.TestCase):

    def _publisher_thread(self, mq, item_count):
        for i in range(item_count):
            mq.Put(i)
        mq.Join()

    def test_multiqueue_gets_same_sequence(self):
        mq = MultiQueue()
        s1 = mq.Subscribe()
        s2 = mq.Subscribe()
        s3 = mq.Subscribe()
        s4 = mq.Subscribe()

        # number of items to put into the queue
        item_count = 10

        publisher_thread = threading.Thread(target=self._publisher_thread, args=(mq, item_count, ))
        publisher_thread.start()

        for sub_id in [s1, s2, s3, s4]:
            for i in range(item_count):
                self.assertEqual(mq.Poll(sub_id), i)
            self.assertEqual(mq.Poll(sub_id), None)

        publisher_thread.join()

if __name__ == '__main__':
    logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] [%(threadName)s]: %(message)s")
    unittest.main()
