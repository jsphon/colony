import multiprocessing
from queue import Queue
from threading import Thread

from colony.observer import Observer, Observable


class Colony(object):
    def __init__(self):
        self.nodes = []

    def add(self, node_class, *args, **kwargs):
        new_node = node_class(*args, **kwargs)
        self.nodes.append(new_node)
        return new_node

    def start(self):
        for node in self.nodes:
            node.start()

    def kill(self):
        for node in self.nodes:
            print('Killing %s' % node)
            node.kill()


class OutputPort(Observable):
    def __init__(self):
        super(OutputPort, self).__init__()

    def connect_to(self, node):
        self.node = node

    def notify(self, event):
        print('OutputPort.notify(%s), notifying %i observers' % (event, len(self.observers)))
        self.notify_observers(event)


class NodeEvent(object):
    def __init__(self, payload):
        self.payload = payload

    def __repr__(self):
        #return 'NodeEvent(payload=%s)' % str(self.payload)

        class_name = self.__class__.__name__
        if self.payload:
            s_payload = str(self.payload)
            if len(s_payload)>10:
                s_payload = s_payload[:7] + '...'
            return '<%s payload="%s">' % (class_name, s_payload)
        else:
            return '<%s>' % class_name


class PoisonPill(NodeEvent):

    def __init__(self):
        super(PoisonPill, self).__init__(payload=None)


class NodeArgEvent(NodeEvent):
    def __init__(self, payload, idx):
        super(NodeArgEvent, self).__init__(payload)
        self.idx = idx


class NodeKwargEvent(NodeEvent):
    def __init__(self, payload, kwarg):
        super(NodeKwargEvent, self).__init__(payload)
        self.kwarg = kwarg


class InputPort(Observer):
    def __init__(self):
        self.node = None

    def connect_to(self, node):
        self.node = node

    def notify(self, node_event):
        print('NodeInput.notify(%s)' % node_event)
        self.node.execute(node_event)


class ArgInputPort(InputPort):
    def __init__(self, idx):
        super(ArgInputPort, self).__init__()
        self.idx = idx

    def notify(self, node_event):
        self.node.execute(NodeArgEvent(node_event.payload, self.idx))


class KwargInputPort(InputPort):
    def __init__(self, kwarg):
        super(KwargInputPort, self).__init__()
        self.kwarg = kwarg

    def notify(self, node_event):
        self.node.execute(NodeKwargEvent(node_event.payload, self.kwarg))


# class BatchNodeInput(InputPort):
#     def __init__(self, batch_size):
#         self.batch_size = batch_size
#
#     def notify(self, payload):
#         for batch in self.chunks(payload):
#             self.node.execute(NodeEvent(batch))
#
#     def chunks(self, payload):
#         """ Yield successive n-sized chunks from l.
#         """
#         for i in range(0, len(payload), self.batch_size):
#             yield payload[i:i + self.batch_size]


class Node(object):
    def __init__(self,
                 target=None,
                 input_node=None,
                 args=None,
                 kwargs=None,
                 name=None):
        """ Processing unit of code

        We have args and kwargs to allow this unit to retrieve changed
        values from other nodes, that might be from other processes.
        Do we really need them if we are using threading rather than
        multi-processing?

        Parameters
        ----------
        input_port : InputPort
        output_port : OutputPort
        args : NodeArgEvent
            represents a function argument that could change
        kwargs : NodeKwargEvent
            represents a keyword argument that could change

        """
        self._target = target
        self.input_port = InputPort()
        self.input_port.connect_to(self)
        self.output_port = OutputPort()
        self.output_port.connect_to(self)
        self.name = name

        self.node_args = args
        self.node_arg_values = []

        for i, arg in enumerate(args or []):
            node_arg_input = ArgInputPort(i)
            node_arg_input.connect_to(self)
            arg.output.register_observer(node_arg_input)
            self.node_arg_values.append(arg.get_value())

        self.node_kwargs = kwargs or {}
        self.node_kwarg_values = {}
        for k, v in (kwargs or {}).items():
            node_kwarg_input = KwargInputPort(k)
            node_kwarg_input.connect_to(self)
            v.output.register_observer(node_kwarg_input)
            self.node_kwarg_values[k] = v.get_value()

        self._value = None

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.name:
            return '<%s name="%s">' % (class_name, self.name)
        else:
            return '<%s>' % class_name

    def add_child(self, child_node):
        self.output_port.register_observer(child_node.input_port)

    def execute(self, event):
        self.handle_event(event)

    def kill(self):
        pass

    def get_value(self):
        return self._value

    def start(self):
        pass

    def handle_event(self, event):
        print('worker received event %s' % event)
        if isinstance(event, PoisonPill):
            return -1
        elif isinstance(event, NodeArgEvent):
            self.node_arg_values[event.idx] = event.payload
        elif isinstance(event, NodeKwargEvent):
            self.node_kwarg_values[event.kwarg] = event.payload
        elif isinstance(event, NodeEvent):
            result = self._target(event.payload, *self.node_arg_values, **self.node_kwarg_values)
            print('worker got result "%s"' % str(result))
            self.handle_result(result)
        else:
            raise ValueError('Event type not recognised: %s' % type(event))

    def handle_result(self, result):
        self._value = result
        self.output_port.notify(NodeEvent(result))


class MapNode(Node):
    """ Input should be iterable. Forwards the input's individual elements
    to the output"""

    def __init__(self):
        super(MapNode, self).__init__()

    def execute(self, event):
        if isinstance(event, NodeEvent):
            for x in event.payload:
                self.output_port.notify_observers(NodeEvent(x))
        else:
            raise ValueError('MapNode cannot process event of type %s' % event)


class BatchNode(Node):
    def __init__(self, batch_size):
        super(BatchNode, self).__init__()
        self.batch_size = batch_size

    def execute(self, event):
        for batch in self.chunks(event.payload):
            self.node.execute(NodeEvent(batch))

    def chunks(self, payload):
        """ Yield successive n-sized chunks from l.
        """
        for i in range(0, len(payload), self.batch_size):
            yield payload[i:i + self.batch_size]


class AsyncNode(Node):
    def __init__(self,
                 target=None,
                 input_port=None,
                 output_port=None,
                 num_threads=1,
                 async_class=Thread,
                 args=None,
                 kwargs=None,
                 name=None):
        super(AsyncNode, self).__init__(target=target, args=args, kwargs=kwargs, name=name)

        self.async_class = async_class
        self.queue_class = self.get_queue_class(async_class)

        self.num_threads = num_threads
        self.worker_queue = self.queue_class()

        self.worker_threads = [async_class(target=self.worker) for _ in range(num_threads)]

    def get_queue_class(self, async_class):
        if async_class == Thread:
            return Queue
        elif async_class == multiprocessing.Process:
            return multiprocessing.Queue

    def start(self):
        for thread in self.worker_threads:
            thread.start()

    def kill(self):
        super(AsyncNode, self).kill()
        for _ in self.worker_threads:
            self.worker_queue.put(PoisonPill())

        self.join()

    def join(self):
        for thread in self.worker_threads:
            thread.join()

    def execute(self, event):
        print('execute(%s)' % event)
        self.worker_queue.put(event)

    def worker(self):
        while True:
            event = self.worker_queue.get()
            return_code = self.handle_event(event)
            if return_code == -1:
                return

    def handle_event(self, event):
        print('worker received event %s' % event)
        if isinstance(event, PoisonPill):
            return -1
        elif isinstance(event, NodeArgEvent):
            self.node_arg_values[event.idx] = event.payload
        elif isinstance(event, NodeKwargEvent):
            self.node_kwarg_values[event.kwarg] = event.payload
        elif isinstance(event, NodeEvent):
            result = self._target(event.payload, *self.node_arg_values, **self.node_kwarg_values)
            print('worker got result "%s"' % str(result))
            self.handle_result(result)
        else:
            raise ValueError('Event type not recognised: %s' % type(event))

    def handle_result(self, result):
        self._value = result
        self.output_port.notify(NodeEvent(result))


if __name__ == '__main__':
    import time


    def _target(payload):
        print('target(%s)' % payload)
        return ['target(%s)' % payload]


    def _target2(payload):
        print('target2(%s)' % payload)
        return 'target2(%s)' % payload


    observable = Observable()

    col = Colony()

    node1 = col.add(AsyncNode, _target, name='node1')
    node2 = col.add(MapNode)
    node3 = col.add(AsyncNode, _target2, name='node3')

    node1.add_child(node2)
    node2.add_child(node3)

    col.start()

    node1.input_port.notify(NodeEvent('event1'))
    time.sleep(0.1)

    node1.input_port.notify(NodeEvent('event2'))
    time.sleep(0.1)

    node1.input_port.notify(NodeEvent('event2'))
    time.sleep(0.1)

    print('Killing colony')
    col.kill()
    print('done')

    print(node3.get_value())
