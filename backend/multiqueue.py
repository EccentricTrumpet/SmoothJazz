import logging
import random
import time
import queue
import threading

# A thread-safe multi-consumer queue.
class MultiQueue:
    def __init__(self):
        self.mutex = threading.RLock()
        self.queues = []

    # Returns listener ID
    def Subscribe(self):
        with self.mutex:
            self.queues.append(queue.Queue())
            id = len(self.queues) - 1
            return id

    def Put(self, obj):
        if self.queues is None:
            raise RuntimeError("Queue is already terminated")
        with self.mutex:
            for q in self.queues:
                q.put(obj)

    # Gets an item from the queue, blocks if no item is available.
    # The last item will be None, after which Poll should not be called.
    def Poll(self, id):
        if self.queues is None:
            raise RuntimeError("Queue is already terminated")

        with self.mutex:
            if id >= len(self.queues):
                # queue already deleted
                raise RuntimeError("Queue with id %s does not exist" % id)
            q = self.queues[id]
        obj = q.get()

        # call task_done to let publisher know we've retrieved something from
        # the queue.
        q.task_done()
        return obj

    # Wait until all subscribers finish processing items in their queues, then
    # deletes all queues.
    #
    # Caller can safely assume that consumers will not access this queue after
    # Join returns. 
    def Join(self):
        with self.mutex:
            for q in self.queues:
                q.put(None)
        for q in self.queues:
            q.join()
        self.queues = None
    
