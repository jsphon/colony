import unittest
from multiprocessing import Process
from threading import Thread
import time
import os
import tempfile

from colony.node import AsyncNode, DictionaryNode
from colony.node import Graph, Node, MappingArgInputPort, BatchArgInputPort
from colony.observer import RememberingObserver, ProcessSafeRememberingObserver, Observable

EPS = 0.01


def _x_squared(x):
    return x * x


def _x_plus_one(x):
    return x + 1


def _ax(x, a=1):
    return a*x


def _x_squared_elements(lst):
    return tuple(x*x for x in lst)


class NodeTests(unittest.TestCase):

    def test_calls_observer(self):
        obs = RememberingObserver()
        col = Graph()

        node = col.add(Node, target_func=_x_squared)
        node.output_port.register_observer(obs)

        node.notify(1)
        node.notify(2)
        node.notify(3)

        col.stop()

        self.assertEqual([1, 4, 9], obs.calls)

    def test_target_func_class(self):

        class target_funcClass(object):
            def __init__(self, c):
                print('Initialising target_funcClass')
                self.data = set([c])
                print('data is %s'%str(self.data))

            def execute(self, x):
                self.data.add(x)
                return self.data

        n = Node(target_class=target_funcClass, target_class_args=(0,))
        n.start()

        n.notify(1)
        self.assertEqual({0, 1}, n.get_value())

        n.notify(2)
        self.assertEqual({0, 1, 2}, n.get_value())

        n.notify(3)
        self.assertEqual({0, 1, 2, 3}, n.get_value())


class DictionaryNodeTests(unittest.TestCase):

    def setUp(self):
        self.name = os.path.basename(tempfile.NamedTemporaryFile().name)
        self.dictionary_node = DictionaryNode(name=self.name)

    def test_get_value(self):

        self.assertEqual({}, self.dictionary_node.get_value())

    def test_notify_update_and_get_value(self):

        self.dictionary_node.notify(('update', {'hello': 'world'}))

        self.assertEqual({'hello': 'world'}, self.dictionary_node.get_value())

    def test_notify_update_delete_and_get_value(self):

        self.dictionary_node.notify(('update', {'hello': 'world'}))
        self.dictionary_node.notify(('delete', 'hello'))

        self.assertEqual({}, self.dictionary_node.get_value())

    def test_notify_and_get_value_recovers(self):

        self.dictionary_node.notify(('update', {'hello': 'world'}))

        d2 = DictionaryNode(name=self.name)

        self.assertEqual({'hello': 'world'}, d2.get_value())

    def test_notify_update_delete_and_get_value_recovers(self):

        self.dictionary_node.notify(('update', {'hello': 'world'}))
        self.dictionary_node.notify(('delete', 'hello'))

        d2 = DictionaryNode(name=self.name)

        self.assertEqual({}, d2.get_value())


class AsyncNodeTests(unittest.TestCase):

    def test_calls_observer_process(self):
        for async_class in (Thread, Process):
            self.do_test_calls_observer_process(async_class)

    def do_test_calls_observer_process(self, async_ckass):
        obs = ProcessSafeRememberingObserver()
        col = Graph()

        node = col.add(AsyncNode,
                       target_func=_x_squared,
                       async_class=async_ckass,
                       num_threads=1)
        node.output_port.register_observer(obs)

        col.start()

        node.notify(1)
        node.notify(2)
        node.notify(3)

        col.stop()
        obs.stop()

        self.assertEqual([1, 4, 9], obs.calls)

    def test_map(self):
        for async_class in (Thread, Process,):
            self.do_test_map(async_class)

    def do_test_map(self, async_class):

        obs = ProcessSafeRememberingObserver()
        graph = Graph()

        map_node = graph.add(AsyncNode,
                             target_func=_x_squared,
                             async_class=async_class,
                             reactive_input_ports=MappingArgInputPort())
        map_node.output_port.register_observer(obs)

        graph.start()

        map_node.notify([1, 2, 3])
        map_node.notify([3, 4, 5])

        graph.stop()
        obs.stop()

        expected = {1, 4, 9, 9, 16, 25}
        actual = set(obs.calls)
        self.assertEqual(expected, actual)

    def test_batch(self):
        for async_class in (Thread, Process,):
            self.do_test_batch(async_class)

    def do_test_batch(self, async_class):

        obs = ProcessSafeRememberingObserver()
        graph = Graph()

        batch_node = graph.add(AsyncNode,
                               target_func=_x_squared_elements,
                               async_class=async_class,
                               reactive_input_ports=BatchArgInputPort(batch_size=2))
        batch_node.output_port.register_observer(obs)

        graph.start()

        batch_node.notify([1, 2, 3])
        batch_node.notify([3, 4, 5])

        graph.stop()
        obs.stop()

        expected = {(1, 4), (9, ), (9, 16), (25,)}
        actual = set(obs.calls)
        self.assertEqual(expected, actual)

    def test_node_args(self):

        obs = RememberingObserver()
        col = Graph()

        node1 = col.add(AsyncNode, target_func=_x_squared)
        node2 = col.add(AsyncNode, target_func=_x_plus_one, node_args=node1)

        col.start()

        node2.output_port.register_observer(obs)

        node1.notify(1)
        node1.notify(2)
        node1.notify(3)

        col.stop()
        self.assertEqual({2, 5, 10}, obs.call_set)

    def test_node_kwargs(self):

        obs = RememberingObserver()
        col = Graph()

        node_a = col.add(AsyncNode, target_func=_ax)
        node1 = col.add(AsyncNode, target_func=_ax, node_kwargs={'a':node_a})
        node1.output_port.register_observer(obs)

        col.start()

        # Node1 should output 1 * 2 = 2
        node_a.notify(1)
        node1.notify(2)

        time.sleep(EPS)

        # Node2 should output 2 * 3 = 6
        node_a.notify(2)
        time.sleep(EPS) # Need to wait to allow the data to propagate to node1
        node1.notify(3)

        col.stop()

        self.assertEqual({2, 6}, obs.call_set)


if __name__ == '__main__':
    unittest.main()
