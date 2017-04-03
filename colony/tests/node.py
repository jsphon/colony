import unittest
from multiprocessing import Process
from threading import Thread
import time

from colony.node import AsyncNode
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

        node = col.add(Node, target=_x_squared)
        node.output_port.register_observer(obs)

        node.reactive_input_ports[0].notify(1)
        node.reactive_input_ports[0].notify(2)
        node.reactive_input_ports[0].notify(3)

        col.stop()

        self.assertEqual([1, 4, 9], obs.calls)


class AsyncNodeTests(unittest.TestCase):

    def test_calls_observer_process(self):
        for async_class in (Thread, Process):
            self.do_test_calls_observer_process(async_class)

    def do_test_calls_observer_process(self, async_ckass):
        obs = ProcessSafeRememberingObserver()
        col = Graph()

        node = col.add(AsyncNode,
                       target=_x_squared,
                       async_class=async_ckass,
                       num_threads=1)
        node.output_port.register_observer(obs)

        col.start()

        node.reactive_input_ports[0].notify(1)
        node.reactive_input_ports[0].notify(2)
        node.reactive_input_ports[0].notify(3)

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
                             target=_x_squared,
                             async_class=async_class,
                             reactive_input_ports=MappingArgInputPort())
        map_node.output_port.register_observer(obs)

        graph.start()

        map_node.reactive_input_ports[0].notify([1, 2, 3])
        map_node.reactive_input_ports[0].notify([3, 4, 5])

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
                               target=_x_squared_elements,
                               async_class=async_class,
                               reactive_input_ports=BatchArgInputPort(batch_size=2))
        batch_node.output_port.register_observer(obs)

        graph.start()

        batch_node.reactive_input_ports[0].notify([1, 2, 3])
        batch_node.reactive_input_ports[0].notify([3, 4, 5])

        graph.stop()
        obs.stop()

        expected = {(1, 4), (9, ), (9, 16), (25,)}
        actual = set(obs.calls)
        self.assertEqual(expected, actual)

    def test_node_args(self):

        obs = RememberingObserver()
        col = Graph()

        node1 = col.add(AsyncNode, target=_x_squared)
        node2 = col.add(AsyncNode, target=_x_plus_one, node_args=node1)

        col.start()

        node2.output_port.register_observer(obs)

        node1.reactive_input_ports[0].notify(1)
        node1.reactive_input_ports[0].notify(2)
        node1.reactive_input_ports[0].notify(3)

        col.stop()
        self.assertEqual({2, 5, 10}, obs.call_set)

    def test_node_kwargs(self):

        obs = RememberingObserver()
        col = Graph()

        node_a = col.add(AsyncNode, target=_ax)
        node1 = col.add(AsyncNode, target=_ax, node_kwargs={'a':node_a})
        node1.output_port.register_observer(obs)

        col.start()

        # Node1 should output 1 * 2 = 2
        node_a.reactive_input_ports[0].notify(1)
        node1.reactive_input_ports[0].notify(2)

        time.sleep(EPS)

        # Node2 should output 2 * 3 = 6
        node_a.reactive_input_ports[0].notify(2)
        time.sleep(EPS) # Need to wait to allow the data to propagate to node1
        node1.reactive_input_ports[0].notify(3)

        col.stop()

        self.assertEqual({2, 6}, obs.call_set)


if __name__ == '__main__':
    unittest.main()
