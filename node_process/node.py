import multiprocessing
from queue import Queue
from threading import Thread

from node_process.observer import Observer, Observable


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


class NodeEvent(object):
    def __init__(self, payload):
        self.payload = payload


class NodeArgEvent(NodeEvent):
    def __init__(self, payload, idx):
        super(NodeArgEvent, self).__init__(payload)
        self.idx = idx


class NodeKwargEvent(NodeEvent):
    def __init__(self, payload, kwarg):
        super(NodeKwargEvent, self).__init__(payload)
        self.kwarg = kwarg


class NodeInput(Observer):
    def __init__(self):
        self.node = None

    def connect_to(self, node):
        self.node = node

    def notify(self, payload):
        self.node.execute(NodeEvent(payload))


class NodeArgInput(NodeInput):
    def __init__(self, idx):
        super(NodeArgInput, self).__init__()
        self.idx = idx

    def notify(self, payload):
        self.node.execute(NodeArgEvent(payload, self.idx))


class NodeKwargInput(NodeInput):
    def __init__(self, kwarg):
        super(NodeKwargInput, self).__init__()
        self.kwarg = kwarg

    def notify(self, payload):
        self.node.execute(NodeKwargEvent(payload, self.kwarg))


class BatchNodeInput(NodeInput):
    def __init__(self, batch_size):
        self.batch_size = batch_size

    def notify(self, payload):
        for batch in self.chunks(payload):
            self.node.execute(NodeEvent(batch))

    def chunks(self, payload):
        """ Yield successive n-sized chunks from l.
        """
        for i in range(0, len(payload), self.batch_size):
            yield payload[i:i + self.batch_size]


class ListNodeInput(NodeInput):
    def notify(self, payload):
        for x in payload:
            self.node.execute(NodeEvent(x))


class Node(object):
    def __init__(self, node_input, node_output, args, kwargs):
        """ Processing unit of code

        We have args and kwargs to allow this unit to retrieve changed
        values from other nodes, that might be from other processes.
        Do we really need them if we are using threading rather than
        multi-processing?

        Parameters
        ----------
        node_input : NodeInput
        node_output : NodeOutput
        args : NodeArgEvent
            represents a function argument that could change
        kwargs : NodeKwargEvent
            represents a keyword argument that could change

        """
        super(Node, self).__init__()
        self.input = node_input or NodeInput()
        self.input.connect_to(self)
        self.output = node_output or NodeOutput()
        self.output.connect_to(self)

        self.node_args = args
        self.node_arg_values = []

        for i, arg in enumerate(args or []):
            node_arg_input = NodeArgInput(i)
            node_arg_input.connect_to(self)
            arg.output.register_observer(node_arg_input)
            self.node_arg_values.append(arg.get_value())

        self.node_kwargs = kwargs
        self.node_kwarg_values = {}
        for k, v in (kwargs or {}).items():
            node_kwarg_input = NodeKwargInput(k)
            node_kwarg_input.connect_to(self)
            v.output.register_observer(node_kwarg_input)
            self.node_kwarg_values[k] = v.get_value()

        self._value = None

    def add_child(self, child_node):
        self.output.register_observer(child_node.input)

    def execute(self, event):
        result = self.do_work(event)
        self.output.notify_observers(result)

    def do_work(self, payload, *args, **kwargs):
        """ This is the function that does the work """
        pass

    def kill(self):
        self.execute(PoisonPill())

    def get_value(self):
        return self._value


class AsyncNode(Node):
    def __init__(self, node_input=None,
                 node_output=None,
                 num_threads=1,
                 async_class=Thread,
                 args=None,
                 kwargs=None):
        super(AsyncNode, self).__init__(node_input, node_output, args, kwargs)

        self.async_class = async_class
        self.queue_class = self.get_queue_class(async_class)

        self.num_threads = num_threads
        self.worker_queue = self.queue_class()

        self.worker_threads = [async_class(target=self.worker) for _ in range(num_threads)]

        self.result_queue = self.queue_class()

        # This has to be a thread, not a process, or the output node
        # won't be able to notify observers that were created on the main thread
        self.result_thread = Thread(target=self.distribute)

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
            self.worker_queue.put(payload)

    def worker(self):
        while True:
            event = self.worker_queue.get()
            if isinstance(event, PoisonPill):
                return
            elif isinstance(event, NodeArgEvent):
                self.node_arg_values[event.idx] = event.payload
            elif isinstance(event, NodeKwargEvent):
                self.node_kwarg_values[event.kwarg] = event.payload
            elif isinstance(event, NodeEvent):
                result = self.do_work(event.payload, *self.node_arg_values, **self.node_kwarg_values)

                self.result_queue.put(result)
            else:
                raise ValueError('Event type not recognised: %s' % type(event))

    def distribute(self):
        while True:
            result = self.result_queue.get()
            if isinstance(result, PoisonPill):
                self.output.notify_observers(result)
                return
            else:
                self._value = result
                self.output.notify_observers(result)


class PoisonPill(object):
    pass


if __name__ == '__main__':
    observable = Observable()

    node = AsyncNode(NodeInput(), NodeOutput())
    node2 = AsyncNode(NodeInput(), NodeOutput())

    node.add_child(node2)

    node.input.notify('event1')
    node.input.notify('event2')

    node.kill()
    # node_input.notify(PoisonPill())
