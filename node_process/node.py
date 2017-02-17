from node_process.observer import Observer, Observable
from threading import Thread
import multiprocessing
from queue import Queue
import logging

logger = logging.getLogger('default')
logger.addHandler(logging.StreamHandler())
logger.info('hello')


class Node(Observable):

    def __init__(self, input_observable):
        super(Node, self).__init__()
        self.input = NodeInput(self, input_observable)
        self._value = None

    def execute(self, event):
        result = self.do_work(event)
        self.notify_observers(result)

    def do_work(self, payload):
        raise NotImplementedError('do_work not implemented')

    def kill(self):
        self.execute(PoisonPill())

    def get_value(self):
        return self._value


class AsyncNode(Node):

    def __init__(self, input_observable, num_threads=1, async_class=Thread):
        super(AsyncNode, self).__init__(input_observable)

        self.async_class = async_class
        self.queue_class = self.get_queue_class(async_class)

        self.num_threads = num_threads
        self.worker_queue = self.queue_class()

        self.worker_threads = [async_class(target=self.worker) for _ in range(num_threads)]

        self.result_queue = self.queue_class()
        self.result_thread = async_class(target=self.distribute)

        self.start()

    def get_queue_class(self, async_class):
        if async_class == Thread:
            return Queue
        elif async_class == multiprocessing.Process:
            return multiprocessing.Queue

    def start(self):
        for thread in self.worker_threads:
            thread.start()
        self.result_thread.start()

    def kill(self):
        super(AsyncNode, self).kill()
        self.result_queue.put(PoisonPill())
        self.join()

    def join(self):
        for thread in self.worker_threads:
            thread.join()
        self.result_thread.join()

    def execute(self, payload):
        if isinstance(payload, PoisonPill):
            for _ in range(self.num_threads):
                self.worker_queue.put(payload)
        else:
            print('executing %s'%payload)
            self.worker_queue.put(payload)

    def worker(self):
        while True:
            payload = self.worker_queue.get()
            print('Worker received payload %s'%payload)
            if isinstance(payload, PoisonPill):
                return
            else:
                try:
                    result = self.do_work(payload)
                    print('result is %s'%result)
                except Exception as e:
                    # TODO: Nodes should log
                    print('Ignoring exception')
                else:
                    print('Putting result %s'%result)
                    self.result_queue.put(result)

    def distribute(self):
        while True:
            result = self.result_queue.get()
            if isinstance(result, PoisonPill):
                self.notify_observers(result)
                return
            else:
                print('Sending %s to %i listeners'%(result, len(self._observers)))
                print(self._observers)
                self._value = result
                self.notify_observers(result)


class NodeInput(Observer):

    def __init__(self, node, input_observable):
        self.node = node
        input_observable.register_observer(self)

    def notify(self, event):
        self.node.execute(event)


class BatchNodeInput(NodeInput):

    def __init__(self, node, input_observable, chunk_size):
        super(BatchNodeInput, self).__init__(node, input_observable)
        self.chunk_size = chunk_size

    def notify(self, payload):
        for chunk in self.chunks(payload, self.chunk_size):
            self.node.execute(chunk)

    def chunks(self, payload):
        """ Yield successive n-sized chunks from l.
        """
        for i in range(0, len(payload), self.chunk_size):
            yield payload[i:i + self.chunk_size]


class BatchAsyncNode(AsyncNode):
    """ Splits the Input into multiple parts"""

    nodeClass = BatchNodeInput

    def __init__(self, input_observable, chunk_size):
        super(BatchAsyncNode, self).__init__(input_observable)
        self.chunk_size = chunk_size



class PoisonPill(object):
    pass


if __name__=='__main__':

    observable = Observable()
    node = AsyncNode(observable)
    node.start()
    observable.notify_observers()
