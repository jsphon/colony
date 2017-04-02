import multiprocessing
from queue import Queue
from threading import Thread

from colony.observer import Observer, Observable
from inspect import signature


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

    def notify(self, data):
        print('OutputPort.notify(%s), notifying %i observers' % (data, len(self.observers)))
        self.notify_observers(data)


class NodeEvent(object):
    def __init__(self, payload):
        self.payload = payload

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.payload:
            s_payload = str(self.payload)
            if len(s_payload) > 10:
                s_payload = s_payload[:7] + '...'
            return '<%s payload="%s">' % (class_name, s_payload)
        else:
            return '<%s>' % class_name


class PoisonPill(NodeEvent):

    def __init__(self):
        super(PoisonPill, self).__init__(payload=None)


class InputPort(Observer):

    def __init__(self, node=None):
        self.node = node

    def connect_to(self, node):
        self.node = node

    def notify(self, data):
        print('InputPort.notify(%s)' % data)
        self.node.handle_input(data, self)


class ArgInputPort(InputPort):

    def __init__(self, idx=None, node=None):
        super(ArgInputPort, self).__init__(node=node)
        self.idx = idx

    def notify(self, data):
        self.node.handle_input(data, idx=self.idx)


class MappingArgInputPort(ArgInputPort):

    def notify(self, data):
        for x in data:
            self.node.handle_input(x, idx=self.idx)


class KwargInputPort(InputPort):

    def __init__(self, kwarg):
        super(KwargInputPort, self).__init__()
        self.kwarg = kwarg

    def notify(self, data):
        for x in data:
            self.node.handle_input(x, kwarg=self.idx)


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
                 reactive_input_ports=None,
                 default_reactive_input_values = None,
                 node_args=None,
                 node_kwargs=None,
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
        node_args : list of nodes
            represents a function argument that could change
        node_kwargs : dict of nodes
            represents a keyword argument that could change

        """
        self._target = target

        function_analyser = FunctionAnalyser(target)
        num_reactive_input_ports = function_analyser.num_args

        if isinstance(reactive_input_ports, list):
            assert len(reactive_input_ports) == num_reactive_input_ports
            self.reactive_input_ports = reactive_input_ports
            for rip in reactive_input_ports:
                rip.connect_to(self)
        elif isinstance(reactive_input_ports, ArgInputPort):
            # Single Reactive Input Port
            self.reactive_input_ports = [reactive_input_ports]
            self.reactive_input_ports[0].idx = 0
            self.reactive_input_ports[0].connect_to(self)
        elif num_reactive_input_ports:
            self.reactive_input_ports = []
            for i in range(num_reactive_input_ports):
                rip = ArgInputPort(i, self)
                self.reactive_input_ports.append(rip)
        else:
            raise ValueError('Need to provide some reactive input ports')

        if default_reactive_input_values:
            self.reactive_input_values = default_reactive_input_values
        else:
            self.reactive_input_values = [None] * len(self.reactive_input_ports)

        if node_args:
            if isinstance(node_args, Node):
                node_args = [node_args]
            for i, node_arg in enumerate(node_args):
                node_arg.output_port.register_observer(self.reactive_input_ports[i])

        self.output_port = OutputPort()
        self.output_port.connect_to(self)
        self.name = name

        self.passive_input_ports = {}
        self.passive_input_values = {}
        print('kwargs are %s'%str(function_analyser.kwargs))
        for kwarg in function_analyser.kwargs:
            kwip = KwargInputPort(kwarg.name)
            kwip.connect_to(self)
            self.passive_input_ports[kwarg.name] = kwip
            self.passive_input_values[kwarg.name] = kwarg.default

        if node_kwargs:
            for kwarg, node_kwarg in node_kwargs.items():
                node_kwarg.output_port.register_observer(self.passive_input_ports[kwarg])

        self._value = None

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.name:
            return '<%s name="%s">' % (class_name, self.name)
        else:
            return '<%s>' % class_name

    def add_child(self, child_node):
        self.output_port.register_observer(child_node.input_port)

    def execute(self, data, port):
        self.handle_input(data, port)

    def kill(self):
        pass

    def get_value(self):
        return self._value

    def start(self):
        pass

    def handle_input(self, data, idx=None, kwarg=None):

        print('handle_input(%s, idx=%s, kwarg=%s)' % (data, idx, kwarg))

        if idx is not None:
            self.reactive_input_values[idx] = data
            result = self._target(*self.reactive_input_values, **self.passive_input_values)
            self._value = result
            self.handle_result(result)
        elif kwarg is not None:
            self.passive_input_values[kwarg] = data
        else:
            raise ValueError('Need to provide idx or kwarg')

    def handle_result(self, result):
        self._value = result
        self.output_port.notify(result)


class MapNode(Node):
    """ Input should be iterable. Forwards the input's individual elements
    to the output"""

    def __init__(self):
        super(MapNode, self).__init__()


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
                 num_threads=10,
                 async_class=Thread,
                 node_args=None,
                 node_kwargs=None,
                 name=None):
        super(AsyncNode, self).__init__(target=target, node_args=node_args, node_kwargs=node_kwargs, name=name)

        self.async_class = async_class
        self.queue_class = self.get_queue_class(async_class)

        self.num_threads = num_threads
        self.worker_queue = self.queue_class()

        self.worker_threads = []#[async_class(target=self.worker) for _ in range(num_threads)]

    def get_queue_class(self, async_class):
        if async_class == Thread:
            return Queue
        elif async_class == multiprocessing.Process:
            return multiprocessing.Queue

    def start(self):
        self.worker_threads = [self.async_class(target=self.worker) for _ in range(self.num_threads)]
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

    # def execute(self, event):
    #     print('execute(%s)' % event)
    #     self.worker_queue.put(event)

    def handle_input(self, data, idx=None, kwarg=None):
        self.worker_queue.put((data, idx, kwarg))

    def worker(self):
        while True:
            data, idx, kwarg = self.worker_queue.get()
            print('AsyncNode worker got stuff')
            super(AsyncNode, self).handle_input(data, idx, kwarg)
            # return_code = self.handle_event(event)
            # if return_code == -1:
            #     return

    # def handle_event(self, event):
    #     print('worker received event %s' % event)
    #     if isinstance(event, PoisonPill):
    #         return -1
    #     elif isinstance(event, NodeArgEvent):
    #         self.node_arg_values[event.idx] = event.payload
    #     elif isinstance(event, NodeKwargEvent):
    #         self.node_kwarg_values[event.kwarg] = event.payload
    #     elif isinstance(event, NodeEvent):
    #         result = self._target(event.payload, *self.node_arg_values, **self.node_kwarg_values)
    #         print('worker got result "%s"' % str(result))
    #         self.handle_result(result)
    #     else:
    #         raise ValueError('Event type not recognised: %s' % type(event))

    # def handle_result(self, result):
    #     self._value = result
    #     self.output_port.notify(NodeEvent(result))


class FunctionAnalyser(object):

    def __init__(self, func):
        self.func = func

    @property
    def num_args(self):
        sig = self.signature
        return len([x for x in sig.parameters.values() if x.default == sig.empty])

    @property
    def num_kwargs(self):
        return len(self.kwargs)

    @property
    def kwargs(self):
        sig = self.signature
        return [x for x in sig.parameters.values() if x.default != sig.empty]

    @property
    def signature(self):
        return signature(self.func)


if __name__ == '__main__':
    import time
    from colony.observer import ProcessSafeRememberingObserver

    def _target(a, b):
        return a+b

    obs = ProcessSafeRememberingObserver()

    col = Colony()

    node1 = col.add(Node, _target, name='node1',
                    default_reactive_input_values=[0, 0])
    node1.output_port.register_observer(obs)

    col.start()

    node1.reactive_input_ports[0].notify(1)
    node1.reactive_input_ports[1].notify(2)

    print(node1.get_value())

    node1.reactive_input_ports[0].notify(2)

    print(node1.get_value())

    obs.kill()
    print('observer calls:')
    print(obs.calls)
