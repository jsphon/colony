from node_process.observer import Observer, Observable
from threading import Thread
import multiprocessing
from queue import Queue
import logging

logger = logging.getLogger('default')
logger.addHandler(logging.StreamHandler())
logger.info('hello')


class NodeOutput(Observable):

    def __init__(self):
        super(NodeOutput, self).__init__()

    def connect_to(self, node):
        self.node = node


class IterableElementNodeOutput(NodeOutput):
    """Send each element of iterable to output"""
    def notify_observers(self, event):
        if isinstance(event, PoisonPill):
            super(IterableElementNodeOutput, self).notify_observers(event)
        else:
            for x in event:
                super(IterableElementNodeOutput, self).notify_observers(x)


class NodeInput(Observer):

    def __init__(self):
        self.node = None

    def connect_to(self, node):
        self.node = node

    def notify(self, event):
        self.node.execute(event)


class BatchNodeInput(NodeInput):

    def __init__(self, batch_size):
        self.batch_size = batch_size

    def notify(self, payload):
        for batch in self.chunks(payload):
            self.node.execute(batch)

    def chunks(self, payload):
        """ Yield successive n-sized chunks from l.
        """
        for i in range(0, len(payload), self.batch_size):
            yield payload[i:i + self.batch_size]


class ListNodeInput(NodeInput):

    def notify(self, payload):
        for x in payload:
            self.node.execute(x)


class Node(object):

    def __init__(self, node_input, node_output):
        super(Node, self).__init__()
        self.input = node_input or NodeInput()
        self.input.connect_to(self)
        self.output = node_output or NodeOutput()
        self.output.connect_to(self)

        self._value = None

    def add_child(self, child_node):
        self.output.register_observer(child_node.input)

    def execute(self, event):
        result = self.do_work(event)
        self.notify_observers(result)

    def do_work(self, payload):
        """ This is the function that does the work """
        pass
        # raise NotImplementedError('do_work not implemented')

    def kill(self):
        self.execute(PoisonPill())

    def get_value(self):
        return self._value


class AsyncNode(Node):

    def __init__(self, node_input=None, node_output=None, num_threads=1, async_class=Thread):
        super(AsyncNode, self).__init__(node_input, node_output)

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
                # self.notify_observers(result)
                self.output.notify_observers(result)
                return
            else:
                print('Sending %s to %i listeners'%(result, len(self.output._observers)))
                print(self.output.observers)
                self._value = result
                self.output.notify_observers(result)


class PoisonPill(object):
    pass


if __name__=='__main__':

    observable = Observable()

    node = AsyncNode(NodeInput(), NodeOutput())
    node2 = AsyncNode(NodeInput(), NodeOutput())

    node.add_child(node2)

    node.input.notify('event1')
    node.input.notify('event2')

    node.kill()
    #node_input.notify(PoisonPill())
